import math
from datetime import datetime
from typing import Literal
from fastapi import APIRouter, HTTPException, Query
from app.database import get_supabase_client
from app.schemas import (
    BusinessCaseItem,
    CategoryResponse,
    IntegrationSummary,
    MetricDetail,
    MetricSummary,
    RelatedRepositoryItem,
    RepositoryDetailResponse,
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
        topics=["embedding", "database", "python", "ai", "vector"],
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


def _build_fallback_detail(repo: RepositoryListItem) -> RepositoryDetailResponse:
    """Construye la ficha técnica de respaldo a partir de un item base del catálogo."""
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
        detected_stack=(
            ["Rust", "Docker", "REST API", "gRPC"]
            if repo.id == 101
            else ["Python", "Docker", "REST API"]
        ),
        integration_methods_suggested=["API REST", "SDK / librería", "Docker"],
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


def _map_repository_detail_row(row: dict) -> RepositoryDetailResponse:
    """Transforma un registro relacional completo de Supabase al esquema RepositoryDetailResponse."""
    base_item = _map_repository_row(row)

    raw_metrics = row.get("metrics") or {}
    if isinstance(raw_metrics, list):
        raw_metrics = raw_metrics[0] if raw_metrics else {}

    integrations_list: list[IntegrationSummary] = []
    for rel in row.get("integration_repositories") or []:
        integ = rel.get("integrations")
        if not integ:
            continue

        related_repos: list[RelatedRepositoryItem] = []
        for other_rel in integ.get("integration_repositories") or []:
            other_repo = other_rel.get("repositories")
            if other_repo and other_repo.get("id") != row["id"]:
                related_repos.append(
                    RelatedRepositoryItem(
                        id=other_repo["id"],
                        full_name=other_repo["full_name"],
                        role=other_rel.get("role"),
                    )
                )

        business_cases: list[BusinessCaseItem] = []
        for bc_rel in integ.get("integration_business_cases") or []:
            bc = bc_rel.get("business_cases")
            if bc:
                business_cases.append(
                    BusinessCaseItem(
                        id=bc["id"],
                        name=bc["name"],
                    )
                )

        triggers_val = integ.get("triggers_or_webhooks")
        if isinstance(triggers_val, list):
            triggers_val = ", ".join(str(t) for t in triggers_val)

        integrations_list.append(
            IntegrationSummary(
                id=integ["id"],
                code=integ["code"],
                purpose=integ["purpose"],
                integration_type=integ["integration_type"],
                triggers_or_webhooks=triggers_val,
                example_snippet=integ.get("example_snippet"),
                compatible_stack=integ.get("compatible_stack") or [],
                main_steps=integ.get("main_steps") or [],
                difficulty=integ["difficulty"],
                role=rel.get("role"),
                documentation_url=integ.get("documentation_url"),
                related_repositories=related_repos,
                business_cases=business_cases,
            )
        )

    return RepositoryDetailResponse(
        **base_item.model_dump(exclude={"metrics"}),
        homepage=row.get("homepage"),
        detected_stack=row.get("detected_stack") or [],
        integration_methods_suggested=row.get("integration_methods_suggested") or [],
        open_issues=row.get("open_issues") or 0,
        has_issues=row.get("has_issues", True),
        issues_url=row.get("issues_url"),
        archived=row.get("archived", False),
        maintainer_active=row.get("maintainer_active", True),
        synced_at=row.get("synced_at"),
        metrics=MetricDetail(
            health_score=raw_metrics.get("health_score", 0),
            health_status=raw_metrics.get("health_status"),
            health_score_details=raw_metrics.get("health_score_details"),
            commits_last_30_days=raw_metrics.get("commits_last_30_days"),
            commits_last_90_days=raw_metrics.get("commits_last_90_days"),
            commits_last_year=raw_metrics.get("commits_last_year"),
            commit_activity_status=raw_metrics.get("commit_activity_status"),
            measured_at=raw_metrics.get("measured_at"),
        ),
        integrations=integrations_list,
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
    """Aplica filtros en memoria sobre la lista de repositorios para modo offline o fallback."""
    results = []
    q_clean = q.strip().lower() if q else None
    lang_clean = language.strip().lower() if language else None
    lic_clean = license_type.strip().lower() if license_type else None
    status_clean = health_status.strip().lower() if health_status else None

    for repo in repos:
        if q_clean:
            match_name = q_clean in repo.name.lower() or q_clean in repo.full_name.lower()
            match_desc = repo.description and q_clean in repo.description.lower()
            match_desc_es = repo.description_es and q_clean in repo.description_es.lower()
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
    sort_by: Literal["stars", "forks", "last_commit_at", "health_score"] = Query(
        default="stars",
        description="Campo de ordenación: stars, forks, last_commit_at, health_score",
    ),
    order: Literal["asc", "desc"] = Query(
        default="desc",
        description="Dirección de ordenación: asc o desc",
    ),
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=10, ge=1, le=50, description="Cantidad de items por página"),
):
    """Filtra el catálogo combinando búsqueda textual, filtros facetados y ordenamiento."""
    supabase = get_supabase_client()
    is_desc = order == "desc"
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

    filtered = _filter_in_memory(
        repos=FALLBACK_REPOSITORIES,
        q=q,
        category_id=category_id,
        language=language,
        min_stars=min_stars,
        license_type=license,
        health_status=health_status,
    )

    sorted_filtered = sorted(
        filtered,
        key=lambda r: (
            r.metrics.health_score
            if sort_by == "health_score"
            else getattr(r, sort_by) or 0
        ),
        reverse=is_desc,
    )
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


@router.get(
    "/{id}",
    response_model=RepositoryDetailResponse,
    summary="Ficha técnica de un repositorio",
    description="Devuelve la ficha completa de un repositorio con métricas detalladas e ideas de integración estructuradas.",
)
def get_repository_detail(id: int):
    """Obtiene la ficha técnica completa de un repositorio por su ID interno."""
    supabase = get_supabase_client()

    if supabase:
        try:
            response = (
                supabase.table("repositories")
                .select(
                    "*, categories(id, name), metrics(*), "
                    "integration_repositories(role, integrations(*, "
                    "integration_repositories(role, repositories(id, full_name)), "
                    "integration_business_cases(business_cases(id, name))))"
                )
                .eq("id", id)
                .execute()
            )
            if response.data:
                return _map_repository_detail_row(response.data[0])
        except Exception:
            pass

    fallback_repo = next((r for r in FALLBACK_REPOSITORIES if r.id == id), None)
    if fallback_repo:
        return _build_fallback_detail(fallback_repo)

    raise HTTPException(
        status_code=404,
        detail=f"El repositorio con id {id} no fue encontrado.",
    )