import os
from fastapi import Depends, FastAPI, Request
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
from app.services.risk_evaluator import evaluate_repository_risk

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
        }
    },
)
async def chat_with_assistant(request: ChatRequest):
    """Recibe la consulta del usuario en lenguaje natural y devuelve recomendaciones, fuentes y arquitectura."""

    components = [
        ArchitectureComponent(
            key="docs",
            repository_id=83,
            full_name="Unstructured-IO/unstructured",
            role="Extrae el texto de manuales y PDF",
            license="Apache-2.0",
            health_status="Activo",
            justification="Procesa documentos en Python sin servicios externos.",
        ),
        ArchitectureComponent(
            key="vectores",
            repository_id=25,
            full_name="chroma-core/chroma",
            role="Guarda los embeddings y busca fragmentos similares",
            license="Apache-2.0",
            health_status="Activo",
            justification="Base vectorial ligera, con cliente oficial de Python y configuración mínima.",
        ),
        ArchitectureComponent(
            key="orquestacion",
            repository_id=32,
            full_name="langchain-ai/langchain",
            role="Orquesta la búsqueda y la respuesta",
            license="MIT",
            health_status="Activo",
            justification="Integra Chroma y el modelo de lenguaje en pocas líneas.",
        ),
        ArchitectureComponent(
            key="monitoreo",
            repository_id=54,
            full_name="grafana/grafana",
            role="Paneles para monitorear el uso y la latencia del asistente",
            license="AGPL-3.0",  # Licencia real de Grafana: muestra la alerta de licencia (9.3)
            health_status="Activo",
            justification="Visualiza métricas del flujo de búsqueda y respuesta en un solo panel.",
        ),
    ]


    for component in components:
        component.alerts = evaluate_repository_risk(
            license=component.license,
            health_status=component.health_status,
            is_archived=False,
        ).alerts

    return ChatResponse(
        answer=(
            "Para un entorno donde prima la simplicidad y el uso directo con Python, te recomiendo **Chroma**. "
            "Es ligera, se ejecuta en memoria o cliente/servidor y requiere una configuración mínima. "
            "Si en el futuro necesitas escalar a producción masiva con millones de vectores y alta concurrencia, "
            "**Qdrant** es una excelente alternativa en Rust con cliente oficial de Python. "
            "Para monitorear el uso del asistente puedes sumar **Grafana**; ojo: su licencia es AGPL-3.0."
        ),
        sources=[
            ChatSource(
                repository_id=25,
                name="chroma",
                full_name="chroma-core/chroma",
                url="https://github.com/chroma-core/chroma",
                relevance_score=0.94,
            ),
            ChatSource(
                repository_id=23,
                name="qdrant",
                full_name="qdrant/qdrant",
                url="https://github.com/qdrant/qdrant",
                relevance_score=0.88,
            ),
        ],
        suggested_questions=[
            "¿Cómo integrar Chroma con LangChain?",
            "¿Cuáles son las diferencias de rendimiento entre Qdrant y Chroma?",
        ],
        architecture=ArchitectureProposal(
            components=components,
            connections=[
                ArchitectureConnection(
                    **{
                        "from": "docs",
                        "to": "vectores",
                        "label": "Envía los fragmentos de texto para indexarlos",
                        "verified": True,
                        "integration_code": "INT-047",
                    }
                ),
                ArchitectureConnection(
                    **{
                        "from": "orquestacion",
                        "to": "vectores",
                        "label": "Consulta los fragmentos relevantes para cada pregunta",
                        "verified": False,
                        "integration_code": None,
                    }
                ),
                ArchitectureConnection(
                    **{
                        "from": "orquestacion",
                        "to": "monitoreo",
                        "label": "Envía métricas de uso y latencia de cada respuesta",
                        "verified": False,
                        "integration_code": None,
                    }
                ),
            ],
        ),
    )
