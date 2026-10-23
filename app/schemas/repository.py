from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.category import CategoryResponse

# --- Métricas ---
class MetricSummary(BaseModel):
    health_score: int = Field(..., ge=0, le=100, description="Puntuación global de salud de 0 a 100", examples=[95])
    health_status: str = Field(..., description="Estado de salud ('Activo', 'En riesgo', 'Abandonado')", examples=["Activo"])

class MetricDetail(MetricSummary):
    health_score_details: dict | None = Field(default=None, description="Desglose de los componentes del score")
    commits_last_30_days: int | None = Field(default=None, description="Commits en los últimos 30 días", examples=[42])
    commits_last_90_days: int | None = Field(default=None, description="Commits en los últimos 90 días", examples=[135])
    commits_last_year: int | None = Field(default=None, description="Commits en el último año", examples=[580])
    commit_activity_status: str | None = Field(default=None, description="Estado de disponibilidad de actividad de commits", examples=["Alta frecuencia"])
    measured_at: datetime | None = Field(default=None, description="Fecha y hora de la última medición")

# --- Integraciones relacionadas ---
class IntegrationSummary(BaseModel):
    id: int = Field(..., description="Identificador de la integración", examples=[1])
    code: str = Field(..., description="Código de la idea (ej: INT-001)", examples=["INT-001"])
    purpose: str = Field(..., description="Propósito de la integración")
    integration_type: str = Field(..., description="Tipo de integración (SDK, Docker, API REST, etc.)", examples=["SDK / librería"])
    difficulty: str = Field(..., description="Dificultad (Baja, Media, Alta)", examples=["Media"])
    role: str | None = Field(default=None, description="Rol del repositorio en esta integración", examples=["Almacenamiento de vectores"])

# --- Repositorio para Listados (Liviano) ---
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
    pushed_at: datetime | None = Field(default=None, description="Fecha del último push (última actualización real)")
    category: CategoryResponse
    metrics: MetricSummary

# --- Respuesta Paginada del Catálogo ---
class RepositoryPaginationResponse(BaseModel):
    total: int = Field(..., description="Total de repositorios coincidentes", examples=[42])
    page: int = Field(..., description="Página actual", examples=[1])
    page_size: int = Field(..., description="Items por página", examples=[10])
    total_pages: int = Field(..., description="Total de páginas calculadas", examples=[5])
    items: list[RepositoryListItem]

# --- Ficha Técnica Completa (Detalle por ID) ---
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