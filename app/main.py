import asyncio
import logging
import os

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import ValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.rate_limit import assistant_rate_limiter
from app.routers import (
    categories,
    github_inventory_router,
    github_router,
    repositories,
)
from app.schemas import (
    ArchitectureComponent,
    ArchitectureConnection,
    ArchitectureProposal,
    ChatRequest,
    ChatResponse,
    ChatSource,
)
from app.orchestrator.orchestrator import AssistantOrchestrator
from app.services.risk_evaluator import evaluate_repository_risk

logger = logging.getLogger(__name__)

# Control de documentación interactiva en producción (Observación menor 7 / Nuclei)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
is_production = ENVIRONMENT == "production"

app = FastAPI(
    title="OpenBridge API",
    description="Catálogo inteligente de herramientas Open Source y Asistente RAG",
    version="1.0.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

# Configuración de CORS segura (Hallazgo N2-003)
# Usa lista blanca explícita y evita reflejar orígenes arbitrarios con allow_credentials: true
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://openbridge-rcv2.onrender.com",
    "https://openbridge-dev.vercel.app",
    "https://openbridge-seven.vercel.app"
]
env_origins = os.getenv("ALLOWED_ORIGINS", "")
if env_origins:
    allowed_origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
else:
    allowed_origins = DEFAULT_ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Cabeceras de seguridad y endurecimiento HTTP (Hallazgo N2-002, N2-001 y Schemathesis ST204)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    # Permitir CDN y scripts inline en /docs y /redoc para que Swagger UI cargue correctamente
    if request.url.path in ("/docs", "/redoc", "/openapi.json"):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; "
            "frame-ancestors 'none'"
        )
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"

    # RFC 9110 / Schemathesis ST204: Asegurar cabecera Allow en respuestas 405
    if response.status_code == 405 and "allow" not in response.headers:
        response.headers["allow"] = "GET, POST, OPTIONS"

    # N2-001: Suprimir cabecera de servidor si uvicorn la inyecta
    if "server" in response.headers:
        del response.headers["server"]

    return response


app.include_router(github_inventory_router.router)
app.include_router(github_router.router)
app.include_router(categories.router)
app.include_router(repositories.router)


@app.get("/health", tags=["Health Check"])
def health_check():
    """Ruta básica de verificación del estado del servidor."""
    return {"status": "ok", "message": "El backend de OpenBridge está activo y funcionando"}


@app.post(
    "/api/v1/assistant/chat",
    response_model=ChatResponse,
    tags=["Asistente"],
    summary="Consultar al Asistente Consultor RAG",
    dependencies=[Depends(assistant_rate_limiter)],
    responses={
        429: {
            "description": "Límite de solicitudes excedido.",
            "content": {
                "application/json": {
                    "example": {"detail": "Límite de solicitudes excedido (10 req/60s). Reintente en 45 segundos."}
                }
            },
        },
        503: {
            "description": "El asistente no está disponible o tardó demasiado en responder.",
            "content": {
                "application/json": {
                    "example": {"detail": "El asistente no está disponible en este momento."}
                }
            },
        },
    },
)
async def chat_with_assistant(request: ChatRequest):
    """Recibe la consulta del usuario en lenguaje natural y devuelve recomendaciones, fuentes y arquitectura."""

    try:
        orchestrator = _get_orchestrator()
        result = await asyncio.wait_for(
            orchestrator.process_message(
                request.message,
                conversation_history=[m.model_dump() for m in request.conversation_history],
            ),
            timeout=ASSISTANT_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.warning("Assistant timed out after %ss", ASSISTANT_TIMEOUT_SECONDS)
        raise HTTPException(status_code=503, detail="El asistente tardó demasiado en responder. Inténtalo de nuevo.")
    except Exception:
        # No se expone el detalle interno al usuario (H7: sin datos ficticios ante errores).
        logger.exception("Assistant failed")
        raise HTTPException(status_code=503, detail="El asistente no está disponible en este momento.")

    return _build_chat_response(result)


ASSISTANT_TIMEOUT_SECONDS = 80
_orchestrator: AssistantOrchestrator | None = None


def _get_orchestrator() -> AssistantOrchestrator:
    """Crea el orquestador una sola vez. Falla con 503 si falta GEMINI_API_KEY."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AssistantOrchestrator()
    return _orchestrator


def _build_chat_response(result: dict) -> ChatResponse:
    """Valida la salida del orquestador contra el contrato y agrega las alertas de riesgo (9.3)."""
    architecture = result.get("architecture") or {}

    components: list[ArchitectureComponent] = []
    for raw in architecture.get("components", []):
        try:
            component = ArchitectureComponent(**raw)
        except ValidationError:
            logger.warning("Discarding invalid architecture component: %s", raw.get("full_name"))
            continue
        component.alerts = evaluate_repository_risk(
            license=component.license,
            health_status=component.health_status,
            is_archived=bool(raw.get("is_archived", False)),
        ).alerts
        components.append(component)

    valid_keys = {component.key for component in components}
    connections: list[ArchitectureConnection] = []
    for raw in architecture.get("connections", []):
        if raw.get("from") not in valid_keys or raw.get("to") not in valid_keys:
            continue
        try:
            connections.append(
                ArchitectureConnection(
                    **{
                        "from": raw["from"],
                        "to": raw["to"],
                        "label": raw.get("label") or "Conexión sugerida",
                        "verified": bool(raw.get("integration_code")),
                        "integration_code": raw.get("integration_code"),
                    }
                )
            )
        except ValidationError:
            logger.warning("Discarding invalid architecture connection")

    sources: list[ChatSource] = []
    for raw in result.get("sources", []):
        try:
            sources.append(ChatSource(**raw))
        except ValidationError:
            continue

    questions = [q for q in result.get("suggested_questions", []) if isinstance(q, str) and q.strip()]

    return ChatResponse(
        answer=result.get("answer") or "No pude generar una recomendación para esta consulta. Intenta describir tu proyecto con más detalle.",
        sources=sources,
        suggested_questions=questions[:3],
        architecture=ArchitectureProposal(components=components, connections=connections) if components else None,
    )
