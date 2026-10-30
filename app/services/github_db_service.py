
from datetime import UTC, datetime

from app.database import get_supabase_client


def _get_category_id(category_name: str | None) -> int | None:
    """Obtiene el ID de una categoría por su nombre."""
    if not category_name:
        return None

    supabase = get_supabase_client()

    if supabase is None:
        raise RuntimeError("Supabase no está configurado.")

    response = (
        supabase.table("categories")
        .select("id")
        .eq("name", category_name)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise ValueError(
            f"No existe la categoría '{category_name}' en Supabase."
        )

    return response.data[0]["id"]


def _build_repository_payload(repository: dict) -> dict:
    """Prepara los datos que se guardarán en repositories."""
    full_name = repository.get("full_name")

    if not full_name or "/" not in full_name:
        raise ValueError(
            f"Nombre de repositorio inválido: {full_name}"
        )

    owner, repo_name = full_name.split("/", maxsplit=1)

    github_id = repository.get("github_id")

    if github_id is None:
        raise ValueError(
            f"El repositorio {full_name} no tiene github_id."
        )

    return {
        "github_id": github_id,
        "name": repository.get("name") or repo_name,
        "owner": owner,
        "full_name": full_name,
        "url": repository.get("url"),
        "description": repository.get("description"),
        "license": (
            repository.get("license")
            or repository.get("licencia")
        ),
        "language": repository.get("language"),
        "topics": repository.get("topics") or [],
        "homepage": repository.get("homepage"),
        "stars": repository.get("stars", 0),
        "forks": repository.get("forks", 0),
        "open_issues": repository.get("open_issues", 0),
        "last_commit_at": repository.get("last_commit_at"),
        "updated_at": repository.get("updated_at"),
        "pushed_at": repository.get("pushed_at"),
        "archived": repository.get("archived", False),
        "maintainer_active": repository.get(
            "maintainer_active",
            True,
        ),
        "health_score": repository.get("health_score", 0),
        "detected_stack": repository.get("detected_stack") or [],
        "integration_methods_suggested": (
            repository.get("integration_methods_suggested") or []
        ),
        "category_id": _get_category_id(
            repository.get("categoria")
        ),
        "synced_at": datetime.now(UTC).isoformat(),
    }


def _build_metrics_payload(
    repository_id: int,
    repository: dict,
) -> dict:
    """Prepara las métricas del repositorio."""
    return {
        "repository_id": repository_id,
        "health_score": int(repository.get("health_score") or 0),
        "health_status": repository.get("health_status"),
        "health_score_details": (
            repository.get("health_score_details")
        ),
        "commits_last_30_days": (
            repository.get("commits_last_30_days")
        ),
        "commits_last_90_days": (
            repository.get("commits_last_90_days")
        ),
        "commits_last_year": (
            repository.get("commits_last_year")
        ),
        "commit_activity_status": (
            repository.get("commit_activity_status")
        ),
        "measured_at": datetime.now(UTC).isoformat(),
    }


def save_repository(repository: dict) -> dict:
    """Inserta o actualiza un repositorio y sus métricas."""
    supabase = get_supabase_client()

    if supabase is None:
        raise RuntimeError("Supabase no está configurado.")

    repository_payload = _build_repository_payload(repository)

    supabase.table("repositories").upsert(
        repository_payload,
        on_conflict="github_id",
    ).execute()

    response = (
        supabase.table("repositories")
        .select("id")
        .eq("github_id", repository_payload["github_id"])
        .single()
        .execute()
    )

    repository_id = response.data["id"]

    metrics_payload = _build_metrics_payload(
        repository_id,
        repository,
    )

    supabase.table("metrics").upsert(
        metrics_payload,
        on_conflict="repository_id",
    ).execute()

    return {
        "repository_id": repository_id,
        "github_id": repository_payload["github_id"],
        "full_name": repository_payload["full_name"],
        "status": "saved",
    }


def save_repositories(repositories: list[dict]) -> dict:
    """Guarda una lista de repositorios y devuelve un resumen."""
    successful = []
    failed = []

    for repository in repositories:
        full_name = repository.get("full_name", "unknown")

        try:
            result = save_repository(repository)
            successful.append(result)

        except Exception as exc:
            failed.append({
                "full_name": full_name,
                "error": str(exc),
            })

    return {
        "total": len(repositories),
        "successful": len(successful),
        "failed": len(failed),
        "saved": successful,
        "errors": failed,
    }


def _build_sync_repository_payload(repository: dict) -> dict:
    """Prepara únicamente los campos dinámicos de sincronización."""
    full_name = repository.get("full_name")

    if not full_name or "/" not in full_name:
        raise ValueError(f"Nombre de repositorio inválido: {full_name}")

    github_id = repository.get("github_id")

    if github_id is None:
        raise ValueError(
            f"El repositorio {full_name} no tiene github_id."
        )

    return {
        "github_id": github_id,
        "stars": repository.get("stars", 0),
        "forks": repository.get("forks", 0),
        "last_commit_at": repository.get("last_commit_at"),
        "updated_at": repository.get("updated_at"),
        "pushed_at": repository.get("pushed_at"),
        "archived": repository.get("archived", False),
        "health_score": repository.get("health_score", 0),
        "synced_at": datetime.now(UTC).isoformat(),
    }


def sync_repository(repository: dict) -> dict:
    """Actualiza únicamente los campos obtenidos por GitHub Sync."""
    supabase = get_supabase_client()

    if supabase is None:
        raise RuntimeError("Supabase no está configurado.")

    payload = _build_sync_repository_payload(repository)

    response = (
        supabase.table("repositories")
        .select("id")
        .eq("github_id", payload["github_id"])
        .limit(1)
        .execute()
    )

    if response.data:
        repository_id = response.data[0]["id"]

        supabase.table("repositories").update(
            payload
        ).eq("id", repository_id).execute()

        status = "updated"

    else:
        response = (
            supabase.table("repositories")
            .insert(payload)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                f"No se pudo insertar {repository['full_name']}."
            )

        repository_id = response.data[0]["id"]
        status = "inserted"

    return {
        "repository_id": repository_id,
        "github_id": payload["github_id"],
        "full_name": repository["full_name"],
        "status": status,
    }


def sync_repositories(repositories: list[dict]) -> dict:
    """Sincroniza una lista sin sobrescribir otros campos."""
    successful = []
    failed = []

    for repository in repositories:
        full_name = repository.get("full_name", "unknown")

        try:
            successful.append(sync_repository(repository))

        except Exception as exc:
            failed.append({
                "full_name": full_name,
                "error": str(exc),
            })

    return {
        "total": len(repositories),
        "successful": len(successful),
        "failed": len(failed),
        "saved": successful,
        "errors": failed,
    }


def get_commit_metrics_record(repository_id: int) -> dict | None:
    """Obtiene las métricas de commits y su fecha de medición."""
    supabase = get_supabase_client()

    if supabase is None:
        raise RuntimeError("Supabase no está configurado.")

    response = (
        supabase.table("metrics")
        .select(
            "commits_last_30_days, commits_last_90_days, "
            "commits_last_year, commit_activity_status, measured_at"
        )
        .eq("repository_id", repository_id)
        .limit(1)
        .execute()
    )

    return response.data[0] if response.data else None


def update_commit_metrics(
    repository_id: int,
    commit_metrics: dict,
) -> None:
    """Actualiza únicamente las métricas de commits."""
    supabase = get_supabase_client()

    if supabase is None:
        raise RuntimeError("Supabase no está configurado.")

    payload = {
        "repository_id": repository_id,
        "commits_last_30_days": (
            commit_metrics.get("commits_last_30_days")
        ),
        "commits_last_90_days": (
            commit_metrics.get("commits_last_90_days")
        ),
        "commits_last_year": (
            commit_metrics.get("commits_last_year")
        ),
        "commit_activity_status": (
            commit_metrics.get("commit_activity_status")
        ),
        "measured_at": datetime.now(UTC).isoformat(),
    }

    supabase.table("metrics").upsert(
        payload,
        on_conflict="repository_id",
    ).execute()
