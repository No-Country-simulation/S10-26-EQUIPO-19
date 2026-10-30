from app.schemas.category import CategoryBase, CategoryResponse
from app.schemas.repository import (
    MetricSummary,
    MetricDetail,
    RelatedRepositoryItem,
    BusinessCaseItem,
    IntegrationSummary,
    RepositoryListItem,
    RepositoryPaginationResponse,
    RepositoryDetailResponse,
)
from app.schemas.assistant import (
    ChatMessage,
    ChatRequest,
    ChatSource,
    ArchitectureComponent,
    ArchitectureConnection,
    ArchitectureProposal,
    ChatResponse,
)
from app.schemas.github import GithubInventoryResponse
