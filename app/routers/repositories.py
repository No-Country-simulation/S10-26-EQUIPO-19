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
        category=CategoryResponse(id=15, name="Búsqueda Vectorial", repositories_count=5),
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
        category=CategoryResponse(id=15, name="Búsqueda Vectorial", repositories_count=5),
        metrics=MetricSummary(health_score=92, health_status="Activo"),
    ),
    RepositoryListItem(
        id=201,
        github_id=51234890,
        name="langchain",
        full_name="langchain-ai/langchain",
        url="https://github.com/langchain-ai/langchain",
        description="Building applications with LLMs through composability",
        description_es="Framework para desarrollar aplicaciones impulsadas por modelos de lenguaje y flujos RAG.",
        language="Python",
        license="MIT",
        stars=92000,
        forks=14800,
        topics=["llm", "rag", "python", "agents"],
        last_commit_at=datetime.fromisoformat("2026-10-22T09:00:00"),
        pushed_at=datetime.fromisoformat("2026-10-22T10:00:00"),
        category=CategoryResponse(id=4, name="IA y LLM", repositories_count=8),
        metrics=MetricSummary(health_score=95, health_status="Activo"),
    ),
    RepositoryListItem(
        id=202,
        github_id=68912034,
        name="ollama",
        full_name="ollama/ollama",
        url="https://github.com/ollama/ollama",
        description="Get up and running with Llama 3, Mistral, Gemma, and other large language models.",
        description_es="Ejecución local simplificada de modelos de lenguaje de gran tamaño.",
        language="Go",
        license="MIT",
        stars=88000,
        forks=6900,
        topics=["llm", "go", "local-ai", "inference"],
        last_commit_at=datetime.fromisoformat("2026-10-21T16:00:00"),
        pushed_at=datetime.fromisoformat("2026-10-21T17:00:00"),
        category=CategoryResponse(id=4, name="IA y LLM", repositories_count=8),
        metrics=MetricSummary(health_score=94, health_status="Activo"),
    ),
    RepositoryListItem(
        id=301,
        github_id=77412390,
        name="langfuse",
        full_name="langfuse/langfuse",
        url="https://github.com/langfuse/langfuse",
        description="Open source LLM engineering platform: observability, metrics, evals, prompt management",
        description_es="Plataforma open source de observabilidad, trazabilidad y evaluación para aplicaciones LLM.",
        language="TypeScript",
        license="MIT",
        stars=4800,
        forks=490,
        topics=["observability", "llm", "typescript", "tracing"],
        last_commit_at=datetime.fromisoformat("2026-06-15T12:00:00"),
        pushed_at=datetime.fromisoformat("2026-06-15T14:00:00"),
        category=CategoryResponse(id=11, name="Observabilidad y Monitoreo", repositories_count=6),
        metrics=MetricSummary(health_score=74, health_status="En riesgo"),
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


def _filter_in_memory(
    repos: list[RepositoryListItem],
    q: str | None,
    category_id: int | None,
    language: str | None,
    min_stars: int | None,
    license_type: str | None,
    health_status: str | None,
) -> list[RepositoryListItem]:
    """Filtra la colección de repositorios en memoria según los criterios especificados."""
    results = []
    q_clean = q.strip().lower() if q and q.strip() else None
    lang_clean = language.strip().lower() if language and language.strip() else None
    lic_clean = license_type.strip().lower() if license_type and license_type.strip() else None
    status_clean = health_status.strip().lower() if health_status and health_status.strip() else None

    for repo in repos:
        if q_clean:
            match_name = q_clean in repo.name.lower() or q_clean in repo.full_name.lower()
            match_desc = bool(repo.description and q_clean in repo.description.lower())
            match_desc_es = bool(repo.description_es and q_clean in repo.description_es.lower())
            match_topics = any(q_clean in topic.lower() for topic in repo.topics)
            if not (match_name or match_desc or match_desc_es or match_topics):
                continue

        if category_id is not None and repo.category.id != category_id:
            continue

        if lang_clean:
            if not repo.language or repo.language.lower() != lang_clean:
                continue

        if min_stars is not None and repo.stars < min_stars:
            continue

        if lic_clean:
            if not repo.license or lic_clean not in repo.license.lower():
                continue

        if status_clean:
            if not repo.metrics.health_status or repo.metrics.health_status.lower() != status_clean:
                continue

        results.append(repo)

    return results


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


@router.get(
    "/search",
    response_model=RepositoryPaginationResponse,
    summary="Búsqueda con filtros de repositorios",
    description="Permite filtrar el catálogo combinando búsqueda textual y filtros facetados.",
)
def search_repositories(
    q: str | None = Query(default=None, description="Texto a buscar en nombre, descripción o tópicos"),
    category_id: int | None = Query(default=None, ge=1, description="ID de la categoría a filtrar"),
    language: str | None = Query(default=None, description="Lenguaje principal (ej. Python, Rust, TypeScript)"),
    min_stars: int | None = Query(default=None, ge=0, description="Cantidad mínima de estrellas en GitHub"),
    license: str | None = Query(default=None, description="Licencia declarada (ej. MIT, Apache-2.0)"),
    health_status: Literal["Activo", "En riesgo", "Abandonado"] | None = Query(
        default=None,
        description="Nivel de mantenimiento: Activo, En riesgo o Abandonado",
    ),
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=10, ge=1, le=50, description="Cantidad de items por página"),
):
    """Filtra el catálogo combinando búsqueda textual y los 5 filtros facetados."""
    supabase = get_supabase_client()
    start = (page - 1) * page_size
    end = start + page_size - 1

    if supabase:
        try:
            metrics_rel = (
                "metrics!inner(health_score, health_status)"
                if health_status
                else "metrics(health_score, health_status)"
            )
            query = supabase.table("repositories").select(
                f"*, categories(id, name), {metrics_rel}",
                count="exact",
            )

            if q and q.strip():
                clean_q = q.strip()
                query = query.or_(
                    f"name.ilike.%{clean_q}%,"
                    f"full_name.ilike.%{clean_q}%,"
                    f"description.ilike.%{clean_q}%,"
                    f"description_es.ilike.%{clean_q}%"
                )

            if category_id is not None:
                query = query.eq("category_id", category_id)

            if language and language.strip():
                query = query.ilike("language", language.strip())

            if min_stars is not None:
                query = query.gte("stars", min_stars)

            if license and license.strip():
                query = query.ilike("license", f"%{license.strip()}%")

            if health_status:
                query = query.eq("metrics.health_status", health_status)

            query = query.order("stars", desc=True)
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

    filtered = _filter_in_memory(
        repos=FALLBACK_REPOSITORIES,
        q=q,
        category_id=category_id,
        language=language,
        min_stars=min_stars,
        license_type=license,
        health_status=health_status,
    )

    sorted_filtered = sorted(filtered, key=lambda r: r.stars, reverse=True)
    total = len(sorted_filtered)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    paginated_items = sorted_filtered[start : start + page_size]

    return RepositoryPaginationResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=paginated_items,
    )
