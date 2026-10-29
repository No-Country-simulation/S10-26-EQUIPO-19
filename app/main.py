from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.routers import categories, repositories, github_router, github_inventory_router
from app.schemas import (
    CategoryResponse,
    RepositoryListItem,
    RepositoryPaginationResponse,
    RepositoryDetailResponse,
    MetricSummary,
    MetricDetail,
    RelatedRepositoryItem,
    BusinessCaseItem,
    IntegrationSummary,
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

MOCK_CATEGORIES = [
    CategoryResponse(id=1, name="Búsqueda Vectorial", repositories_count=5),
    CategoryResponse(id=2, name="IA y LLM", repositories_count=8),
    CategoryResponse(id=3, name="Observabilidad y Monitoreo", repositories_count=6),
]

MOCK_REPOSITORIES_LIST = [
    RepositoryListItem(
        id=101,
        github_id=10567832,
        name="qdrant",
        full_name="qdrant/qdrant",
        url="https://github.com/qdrant/qdrant",
        description="Vector Similarity Search Engine and Vector Database",
        description_es="Motor de búsqueda por similitud vectorial y base de datos vectorial para IA de alto rendimiento.",
        language="Rust",
        license="Apache-2.0",
        stars=19500,
        forks=1400,
        topics=["vector-search", "database", "rust", "machine-learning"],
        last_commit_at=datetime.fromisoformat("2026-10-21T12:00:00"),
        pushed_at=datetime.fromisoformat("2026-10-21T18:30:00"),
        category=MOCK_CATEGORIES[0],
        metrics=MetricSummary(health_score=91, health_status="Activo"),
    ),
    RepositoryListItem(
        id=102,
        github_id=23489110,
        name="chroma",
        full_name="chroma-core/chroma",
        url="https://github.com/chroma-core/chroma",
        description="the AI-native open-source embedding database",
        description_es="Base de datos de embeddings nativa para inteligencia artificial, ligera y de fácil integración.",
        language="Python",
        license="Apache-2.0",
        stars=14200,
        forks=1150,
        topics=["embedding", "database", "python", "ai"],
        last_commit_at=datetime.fromisoformat("2026-10-20T12:00:00"),
        pushed_at=datetime.fromisoformat("2026-10-20T14:15:00"),
        category=MOCK_CATEGORIES[0],
        metrics=MetricSummary(health_score=92, health_status="Activo"),
    ),
]


@app.get("/health", tags=["Health Check"])
def health_check():
    """Ruta básica de verificación del estado del servidor."""
    return {"status": "ok", "message": "El backend de OpenBridge está activo y funcionando"}


@app.get(
    "/api/v1/repositories/search",
    response_model=RepositoryPaginationResponse,
    tags=["Repositorios"],
    summary="Búsqueda con filtros de repositorios",
)
def search_repositories(
    q: str | None = Query(default=None, description="Texto a buscar en nombre, descripción o tópicos"),
    category_id: int | None = Query(default=None, description="ID de la categoría a filtrar"),
    language: str | None = Query(default=None, description="Lenguaje principal (ej. Python, Rust, TypeScript)"),
    min_stars: int | None = Query(default=None, ge=0, description="Cantidad mínima de estrellas en GitHub"),
    license: str | None = Query(default=None, description="Licencia declarada (ej. MIT, Apache-2.0)"),
    health_status: str | None = Query(default=None, description="Nivel de mantenimiento: Activo, En riesgo o Abandonado"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
):
    """Permite filtrar el catálogo combinando búsqueda textual y los 5 filtros facetados."""
    return RepositoryPaginationResponse(
        total=len(MOCK_REPOSITORIES_LIST),
        page=page,
        page_size=page_size,
        total_pages=1,
        items=MOCK_REPOSITORIES_LIST,
    )


@app.get(
    "/api/v1/repositories/{id}",
    response_model=RepositoryDetailResponse,
    tags=["Repositorios"],
    summary="Ficha técnica de un repositorio",
)
def get_repository_detail(id: int):
    """Devuelve la ficha completa con métricas detalladas e ideas de integración relacionadas."""
    repo = next((r for r in MOCK_REPOSITORIES_LIST if r.id == id), None)
    if not repo:
        raise HTTPException(status_code=404, detail=f"El repositorio con id {id} no fue encontrado.")

    return RepositoryDetailResponse(
        id=repo.id,
        github_id=repo.github_id,
        name=repo.name,
        full_name=repo.full_name,
        url=repo.url,
        homepage="https://qdrant.tech" if repo.id == 101 else "https://trychroma.com",
        description=repo.description,
        description_es=repo.description_es,
        language=repo.language,
        license=repo.license,
        stars=repo.stars,
        forks=repo.forks,
        open_issues=120,
        has_issues=True,
        issues_url=None,
        archived=False,
        maintainer_active=True,
        topics=repo.topics,
        last_commit_at=repo.last_commit_at,
        pushed_at=repo.pushed_at,
        synced_at=datetime.fromisoformat("2026-10-22T08:00:00"),
        category=repo.category,
        metrics=MetricDetail(
            health_score=repo.metrics.health_score,
            health_status=repo.metrics.health_status,
            health_score_details={
                "maintenance": 30,
                "commit_activity": 21,
                "popularity": 15,
                "forks": 7,
            },
            commits_last_30_days=42,
            commits_last_90_days=135,
            commits_last_year=580,
            commit_activity_status="available",
            measured_at=datetime.fromisoformat("2026-10-22T08:00:00"),
        ),
        integrations=[
            IntegrationSummary(
                id=16,
                code="INT-016",
                purpose="Asistente que responde preguntas sobre documentos internos sin enviar datos a terceros.",
                integration_type="SDK / librería",
                triggers_or_webhooks="Al cargar documentos (indexación) y en cada pregunta del usuario.",
                example_snippet=(
                    'from langchain_ollama import OllamaEmbeddings, ChatOllama\n'
                    'from langchain_qdrant import QdrantVectorStore\n\n'
                    'emb = OllamaEmbeddings(model="nomic-embed-text", base_url="http://ollama:11434")\n'
                    'store = QdrantVectorStore.from_documents(fragmentos, emb,\n'
                    '    url="http://qdrant:6333", collection_name="docs_internos")\n'
                    'llm = ChatOllama(model="llama3.1", base_url="http://ollama:11434")\n\n'
                    'pregunta = "¿Cuál es la política de vacaciones?"\n'
                    'contexto = store.similarity_search(pregunta, k=4)\n'
                    'respuesta = llm.invoke(f"Responde solo con este contexto:\\n{contexto}\\n\\nPregunta: {pregunta}")'
                ),
                compatible_stack=["Python 3.10+", "LangChain", "Ollama", "Qdrant", "Docker"],
                main_steps=[
                    "Extraer y fragmentar los documentos.",
                    "Indexarlos en Qdrant con embeddings de Ollama.",
                    "Recuperar los fragmentos más parecidos a la pregunta.",
                    "Generar la respuesta con el modelo local usando solo ese contexto.",
                ],
                difficulty="Media",
                role="Almacenamiento y búsqueda de los fragmentos de los documentos",
                documentation_url="https://docs.langchain.com/oss/python/integrations/vectorstores/qdrant",
                related_repositories=[
                    RelatedRepositoryItem(
                        id=201,
                        full_name="langchain-ai/langchain",
                        role="Orquestación del flujo RAG",
                    ),
                    RelatedRepositoryItem(
                        id=202,
                        full_name="ollama/ollama",
                        role="Embeddings y respuestas con un modelo local",
                    ),
                ],
                business_cases=[
                    BusinessCaseItem(
                        id=13,
                        name="Un asistente con IA que responde preguntas sobre documentos internos.",
                    ),
                    BusinessCaseItem(
                        id=12,
                        name="Una mesa de ayuda con chat y respuestas automáticas con IA.",
                    ),
                ],
            )
        ],
    )


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
