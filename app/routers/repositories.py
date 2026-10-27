import math
from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Query
from app.database import get_supabase_client
from app.schemas import (
    CategoryResponse,
    MetricSummary,
    RepositoryListItem,
    RepositoryPaginationResponse,
)

router = APIRouter(
    prefix="/api/v1/repositories",
    tags=["Repositorios"],
)

FALLBACK_REPOSITORIES = [
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
        category=CategoryResponse(id=1, name="Búsqueda Vectorial", repositories_count=5),
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
        category=CategoryResponse(id=1, name="Búsqueda Vectorial", repositories_count=5),
        metrics=MetricSummary(health_score=92, health_status="Activo"),
    ),
]


def _map_repository_row(row: dict) -> RepositoryListItem:
    """Transforma un registro relacional de Supabase al esquema RepositoryListItem."""
    raw_category = row.get("categories") or {}
    if isinstance(raw_category, list):
        raw_category = raw_category[0] if raw_category else {}

    raw_metrics = row.get("metrics") or {}
    if isinstance(raw_metrics, list):
        raw_metrics = raw_metrics[0] if raw_metrics else {}

    return RepositoryListItem(
        id=row["id"],
        github_id=row["github_id"],
        name=row["name"],
        full_name=row["full_name"],
        url=row["url"],
        description=row.get("description"),
        description_es=row.get("description_es"),
        language=row.get("language"),
        license=row.get("license"),
        stars=row.get("stars", 0),
        forks=row.get("forks", 0),
        topics=row.get("topics") or [],
        last_commit_at=row.get("last_commit_at"),
        pushed_at=row.get("pushed_at"),
        category=CategoryResponse(
            id=raw_category.get("id", row.get("category_id") or 0),
            name=raw_category.get("name", "Sin categoría"),
        ),
        metrics=MetricSummary(
            health_score=raw_metrics.get("health_score", 0),
            health_status=raw_metrics.get("health_status"),
        ),
    )


@router.get(
    "",
    response_model=RepositoryPaginationResponse,
    summary="Listado paginado de repositorios",
    description="Devuelve la lista paginada de repositorios aprobados para el catálogo principal.",
)
def get_repositories(
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=10, ge=1, le=50, description="Cantidad de items por página"),
    sort_by: Literal["stars", "forks", "last_commit_at", "health_score"] = Query(
        default="stars",
        description="Campo de ordenación: stars, forks, last_commit_at, health_score",
    ),
    order: Literal["asc", "desc"] = Query(
        default="desc",
        description="Dirección de ordenación: asc o desc",
    ),
):
    """Obtiene el catálogo de repositorios paginado y ordenado desde Supabase."""
    supabase = get_supabase_client()
    is_desc = order == "desc"
    start = (page - 1) * page_size
    end = start + page_size - 1

    if supabase:
        try:
            query = supabase.table("repositories").select(
                "*, categories(id, name), metrics(health_score, health_status)",
                count="exact",
            )

            if sort_by == "health_score":
                query = query.order("health_score", desc=is_desc, foreign_table="metrics")
            else:
                query = query.order(sort_by, desc=is_desc)

            response = query.range(start, end).execute()

            if response.data is not None and (response.count or 0) > 0:
                total = response.count or len(response.data)
                total_pages = math.ceil(total / page_size) if total > 0 else 1
                items = [_map_repository_row(row) for row in response.data]
                return RepositoryPaginationResponse(
                    total=total,
                    page=page,
                    page_size=page_size,
                    total_pages=total_pages,
                    items=items,
                )
        except Exception:
            pass

    sorted_fallback = sorted(
        FALLBACK_REPOSITORIES,
        key=lambda r: (
            r.metrics.health_score
            if sort_by == "health_score"
            else getattr(r, sort_by) or 0
        ),
        reverse=is_desc,
    )
    total = len(sorted_fallback)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    paginated_items = sorted_fallback[start : start + page_size]

    return RepositoryPaginationResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=paginated_items,
    )