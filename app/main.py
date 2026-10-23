from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Importo los esquemas que cree en la carpeta schemas
from app.schemas import (
    CategoryResponse,
    RepositoryListItem,
    RepositoryPaginationResponse,
    RepositoryDetailResponse,
    MetricSummary,
    MetricDetail,
    IntegrationSummary,
    ChatRequest,
    ChatResponse,
    ChatSource,
)

# 1. Instanciamos la aplicación FastAPI
app = FastAPI(
    title="OpenBridge API",
    description="Catálogo inteligente de herramientas Open Source y Asistente RAG",
    version="1.0.0",
)

# 2. Habilitamos CORS para que el frontend (Next.js) pueda consultar la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo permitimos todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATOS DE PRUEBA (MOCKS) ---
MOCK_CATEGORIES = [
    CategoryResponse(id=1, name="Bases de Datos Vectoriales", repositories_count=5),
    CategoryResponse(id=2, name="Frameworks de IA & LLMs", repositories_count=8),
    CategoryResponse(id=3, name="Herramientas de Observabilidad", repositories_count=4),
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
        pushed_at=datetime.fromisoformat("2026-10-21T18:30:00"),
        category=MOCK_CATEGORIES[0],
        metrics=MetricSummary(health_score=95, health_status="Activo"),
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
        pushed_at=datetime.fromisoformat("2026-10-20T14:15:00"),
        category=MOCK_CATEGORIES[0],
        metrics=MetricSummary(health_score=92, health_status="Activo"),
    ),
]


# --- ENDPOINTS DEL SISTEMA ---

@app.get("/health", tags=["Health Check"])
def health_check():
    """Ruta básica de verificación del estado del servidor."""
    return {"status": "ok", "message": "El backend de OpenBridge está activo y funcionando"}


# --- ENDPOINTS DEL CONTRATO DE API (/api/v1) ---

@app.get(
    "/api/v1/categories",
    response_model=list[CategoryResponse],
    tags=["Categorías"],
    summary="Listar categorías del catálogo",
)
def get_categories():
    """Obtiene la lista de todas las categorías disponibles con su conteo de repositorios."""
    return MOCK_CATEGORIES


@app.get(
    "/api/v1/repositories",
    response_model=RepositoryPaginationResponse,
    tags=["Repositorios"],
    summary="Listado paginado de repositorios",
)
def get_repositories(
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=10, ge=1, le=50, description="Cantidad de items por página"),
    sort_by: str = Query(default="stars", description="Campo de ordenación: stars, forks, pushed_at, health_score"),
    order: str = Query(default="desc", regex="^(asc|desc)$", description="Dirección: asc o desc"),
):
    """Devuelve el catálogo de repositorios paginado según los criterios de ordenamiento."""
    return RepositoryPaginationResponse(
        total=len(MOCK_REPOSITORIES_LIST),
        page=page,
        page_size=page_size,
        total_pages=1,
        items=MOCK_REPOSITORIES_LIST,
    )


@app.get(
    "/api/v1/repositories/search",
    response_model=RepositoryPaginationResponse,
    tags=["Repositorios"],
    summary="Búsqueda con filtros de repositorios",
)
def search_repositories(
    q: str | None = Query(default=None, description="Término de búsqueda libre"),
    category_id: int | None = Query(default=None, description="Filtrar por ID de categoría"),
    language: str | None = Query(default=None, description="Filtrar por lenguaje principal"),
    min_stars: int | None = Query(default=None, ge=0, description="Mínimo de estrellas GitHub"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
):
    """Permite filtrar el catálogo combinando búsqueda de texto y filtros facetados."""
    # En este mock devolvemos los datos de prueba
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
    """Devuelve el detalle exhaustivo de una herramienta open source por su ID interno."""
    # Buscamos en el mock
    repo = next((r for r in MOCK_REPOSITORIES_LIST if r.id == id), None)
    if not repo:
        raise HTTPException(status_code=404, detail=f"El repositorio con id {id} no fue encontrado.")

    # Retornamos la ficha técnica completa con métricas detalladas e ideas de integración
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
        pushed_at=repo.pushed_at,
        synced_at=datetime.fromisoformat("2026-10-22T08:00:00"),
        category=repo.category,
        metrics=MetricDetail(
            health_score=repo.metrics.health_score,
            health_status=repo.metrics.health_status,
            health_score_details={
                "commit_frequency_score": 30,
                "stars_popularity_score": 25,
                "maintenance_status_score": 25,
                "issue_resolution_score": 15,
            },
            commits_last_30_days=42,
            commits_last_90_days=135,
            commits_last_year=580,
            commit_activity_status="Alta frecuencia",
            measured_at=datetime.fromisoformat("2026-10-22T08:00:00"),
        ),
        integrations=[
            IntegrationSummary(
                id=1,
                code="INT-001",
                purpose="Búsqueda semántica sobre documentos almacenados en Postgres usando embeddings",
                integration_type="SDK / librería",
                difficulty="Media",
                role="Almacenamiento y consulta de vectores",
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
    """Recibe la consulta del usuario en lenguaje natural y responde con recomendaciones y fuentes."""
    return ChatResponse(
        answer=(
            f"Para tu consulta sobre '{request.message}', una de las herramientas más recomendadas "
            "por su simplicidad y compatibilidad con Python es **Chroma**. "
            "Si requerís alta escalabilidad en producción con Rust, **Qdrant** es la alternativa ideal."
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
    )