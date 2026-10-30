from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    categories,
    repositories,
    github_router,
    github_inventory_router,
)
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ChatSource,
    ArchitectureComponent,
    ArchitectureConnection,
    ArchitectureProposal,
)

app = FastAPI(
    title="OpenBridge API",
    description="Catálogo inteligente de herramientas Open Source y Asistente RAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
)
def chat_with_assistant(request: ChatRequest):
    """Recibe la consulta del usuario en lenguaje natural y devuelve recomendaciones, fuentes y arquitectura."""
    return ChatResponse(
        answer=(
            "Para un entorno donde prima la simplicidad y el uso directo con Python, te recomiendo **Chroma**. "
            "Es ligera, se ejecuta en memoria o cliente/servidor y requiere una configuración mínima. "
            "Si en el futuro necesitas escalar a producción masiva con millones de vectores y alta concurrencia, "
            "**Qdrant** es una excelente alternativa en Rust con cliente oficial de Python."
        ),
        sources=[
            ChatSource(
                repository_id=102,
                name="chroma",
                full_name="chroma-core/chroma",
                url="https://github.com/chroma-core/chroma",
                relevance_score=0.94,
            ),
            ChatSource(
                repository_id=101,
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
            components=[
                ArchitectureComponent(
                    key="docs",
                    repository_id=203,
                    full_name="Unstructured-IO/unstructured",
                    role="Extrae el texto de manuales y PDF",
                    license="Apache-2.0",
                    health_status="Activo",
                    justification="Procesa documentos en Python sin servicios externos.",
                ),
                ArchitectureComponent(
                    key="vectores",
                    repository_id=102,
                    full_name="chroma-core/chroma",
                    role="Guarda los embeddings y busca fragmentos similares",
                    license="Apache-2.0",
                    health_status="Activo",
                    justification="Base vectorial ligera, con cliente oficial de Python y configuración mínima.",
                ),
                ArchitectureComponent(
                    key="orquestacion",
                    repository_id=201,
                    full_name="langchain-ai/langchain",
                    role="Orquesta la búsqueda y la respuesta",
                    license="MIT",
                    health_status="Activo",
                    justification="Integra Chroma y el modelo de lenguaje en pocas líneas.",
                ),
            ],
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
            ],
        ),
    )