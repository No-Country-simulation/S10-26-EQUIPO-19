from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.category import CategoryResponse


class MetricSummary(BaseModel):
    health_score: int = Field(..., ge=0, le=100, description="Puntuación global de salud de 0 a 100", examples=[91])
    health_status: str | None = Field(default=None, description="Estado de salud ('Activo', 'En riesgo', 'Abandonado' o null)", examples=["Activo"])


class MetricDetail(MetricSummary):
    health_score_details: dict | None = Field(default=None, description="Desglose de componentes: maintenance, commit_activity, popularity, forks")
    commits_last_30_days: int | None = Field(default=None, description="Commits en los últimos 30 días", examples=[42])
    commits_last_90_days: int | None = Field(default=None, description="Commits en los últimos 90 días", examples=[135])
    commits_last_year: int | None = Field(default=None, description="Commits en el último año", examples=[580])
    commit_activity_status: str | None = Field(default=None, description="Disponibilidad de datos de commits ('available' o 'unavailable')", examples=["available"])
    measured_at: datetime | None = Field(default=None, description="Fecha y hora de la última medición")


class RelatedRepositoryItem(BaseModel):
    id: int = Field(..., description="Identificador interno del repositorio relacionado", examples=[201])
    full_name: str = Field(..., description="Propietario y nombre en GitHub", examples=["langchain-ai/langchain"])
    role: str | None = Field(default=None, description="Rol del repositorio en la integración", examples=["Orquestación del flujo RAG"])


class BusinessCaseItem(BaseModel):
    id: int = Field(..., description="Identificador del caso de negocio", examples=[13])
    name: str = Field(..., description="Nombre del caso de negocio", examples=["Un asistente con IA que responde preguntas sobre documentos internos."])


class IntegrationSummary(BaseModel):
    id: int = Field(..., description="Identificador de la integración", examples=[16])
    code: str = Field(..., description="Código único de la idea (ej: INT-016)", examples=["INT-016"])
    purpose: str = Field(..., description="Propósito de la integración")
    integration_type: str = Field(..., description="Tipo de integración (SDK / librería, Docker, API REST, etc.)", examples=["SDK / librería"])
    triggers_or_webhooks: str | None = Field(default=None, description="Disparadores o webhooks que inician el flujo")
    example_snippet: str | None = Field(default=None, description="Snippet de código de ejemplo")
    compatible_stack: list[str] = Field(default=[], description="Tecnologías compatibles con esta integración")
    main_steps: list[str] = Field(default=[], description="Pasos principales ordenados para implementar la integración")
    difficulty: str = Field(..., description="Nivel de dificultad (Baja, Media, Alta)", examples=["Media"])
    role: str | None = Field(default=None, description="Función del repositorio dentro de esta integración")
    documentation_url: str | None = Field(default=None, description="Enlace a la documentación oficial")
    related_repositories: list[RelatedRepositoryItem] = Field(default=[], description="Otros repositorios que participan en la idea")
    business_cases: list[BusinessCaseItem] = Field(default=[], description="Casos de negocio que resuelve la integración")


class RepositoryListItem(BaseModel):
    id: int = Field(..., description="Identificador interno del repositorio", examples=[101])
    github_id: int = Field(..., description="Identificador del repositorio en GitHub", examples=[10567832])
    name: str = Field(..., description="Nombre del repositorio", examples=["qdrant"])
    full_name: str = Field(..., description="Propietario y nombre en GitHub", examples=["qdrant/qdrant"])
    url: str = Field(..., description="URL oficial del repositorio", examples=["https://github.com/qdrant/qdrant"])
    description: str | None = Field(default=None, description="Descripción original en inglés")
    description_es: str | None = Field(default=None, description="Descripción curada en español para mostrar en catálogo")
    language: str | None = Field(default=None, description="Lenguaje principal", examples=["Rust"])
    license: str | None = Field(default=None, description="Licencia declarada", examples=["Apache-2.0"])
    stars: int = Field(..., description="Cantidad de estrellas en GitHub", examples=[19500])
    forks: int = Field(..., description="Cantidad de forks en GitHub", examples=[1400])
    topics: list[str] = Field(default=[], description="Lista de tópicos/etiquetas", examples=[["vector-search", "database", "rust"]])
    last_commit_at: datetime | None = Field(default=None, description="Fecha del último commit en la rama principal")
    pushed_at: datetime | None = Field(default=None, description="Fecha del último push a cualquier rama")
    category: CategoryResponse
    metrics: MetricSummary


class RepositoryPaginationResponse(BaseModel):
    total: int = Field(..., description="Total de repositorios coincidentes", examples=[42])
    page: int = Field(..., description="Página actual", examples=[1])
    page_size: int = Field(..., description="Items por página", examples=[10])
    total_pages: int = Field(..., description="Total de páginas calculadas", examples=[5])
    items: list[RepositoryListItem]


class RepositoryDetailResponse(RepositoryListItem):
    homepage: str | None = Field(default=None, description="Sitio web oficial", examples=["https://qdrant.tech"])
    open_issues: int = Field(default=0, description="Cantidad de issues abiertos", examples=[120])
    has_issues: bool = Field(default=True, description="Indica si usa GitHub Issues")
    issues_url: str | None = Field(default=None, description="URL del sistema de incidencias si no usa GitHub Issues")
    archived: bool = Field(default=False, description="Indica si el repo está archivado")
    maintainer_active: bool = Field(default=True, description="Indica si cumple criterio de actividad")
    synced_at: datetime | None = Field(default=None, description="Fecha de sincronización del pipeline")
    metrics: MetricDetail
    integrations: list[IntegrationSummary] = Field(default=[], description="Ideas de integración asociadas al repositorio")