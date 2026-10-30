import base64
import re
from datetime import datetime, UTC
from math import log10


import httpx

from app.clients.github_client import github_get, get_commit_activity


MANIFEST_LABELS = {
    "pyproject.toml": "Python (pyproject.toml)",
    "requirements.txt": "Python (requirements.txt)",
    "Pipfile": "Python (Pipfile)",
    "package.json": "Node.js / JavaScript / TypeScript (package.json)",
    "pnpm-lock.yaml": "Node.js (pnpm)",
    "yarn.lock": "Node.js (Yarn)",
    "package-lock.json": "Node.js (npm)",
    "go.mod": "Go (go.mod)",
    "Cargo.toml": "Rust (Cargo.toml)",
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java/Kotlin (Gradle)",
    "Gemfile": "Ruby (Gemfile)",
    "composer.json": "PHP (Composer)",
    "Dockerfile": "Docker",
    "docker-compose.yml": "Docker Compose",
    "compose.yaml": "Docker Compose",
    "Makefile": "Makefile",
}


async def _get_optional_detail(
    endpoint: str,
    params: dict | None = None,
):
    """Consulta un endpoint secundario; si falla, devuelve None."""
    try:
        data, _ = await github_get(endpoint, params=params)
        return data
    except (ValueError, httpx.HTTPError, RuntimeError):
        return None


async def _get_last_commit_at(
    owner: str,
    repo_name: str,
    default_branch: str | None,
) -> str | None:
    """Obtiene la fecha del último commit de la rama por defecto."""
    if not default_branch:
        return None

    commits = await _get_optional_detail(
        f"/repos/{owner}/{repo_name}/commits",
        params={
            "sha": default_branch,
            "per_page": 1,
        },
    )

    if not isinstance(commits, list) or not commits:
        return None

    commit_data = commits[0].get("commit") or {}
    committer = commit_data.get("committer") or {}
    author = commit_data.get("author") or {}

    return committer.get("date") or author.get("date")


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _health_score(repo: dict) -> tuple[int, str, dict]:
    """Calcula el health score normalizado de 0 a 100."""
    last_commit = _parse_date(repo.get("last_commit_at"))

    days_since_commit = (
        max(
            0,
            (datetime.now(UTC) - last_commit).days,
        )
        if last_commit
        else None
    )

    archived = repo.get("archived", False)
    disabled = repo.get("disabled", False)

    if archived or disabled:
        return 0, "Abandonado", {
            "maintenance": 0,
            "commit_activity": 0,
            "popularity": 0,
            "forks": 0,
            "raw_score": 0,
            "max_raw_score": 80,
        }

    # Mantenimiento: máximo 30 puntos.
    if days_since_commit is None:
        maintenance = 5
    elif days_since_commit <= 30:
        maintenance = 30
    elif days_since_commit <= 90:
        maintenance = 26
    elif days_since_commit <= 180:
        maintenance = 20
    elif days_since_commit <= 365:
        maintenance = 14
    elif days_since_commit <= 730:
        maintenance = 7
    else:
        maintenance = 2

    # Actividad de commits: máximo 25 puntos.
    commits_90d = repo.get("commits_last_90_days")

    if (
        isinstance(commits_90d, (int, float))
        and not isinstance(commits_90d, bool)
        and commits_90d >= 0
        and repo.get("commit_activity_status") == "available"
    ):
        activity_points = min(
            25,
            round(log10(commits_90d + 1) / 3 * 25),
        )
    else:
        activity_points = 0

    # Popularidad: máximo 15 puntos.
    stars = max(0, int(repo.get("stargazers_count") or 0))
    popularity = min(
        15,
        round(log10(stars + 1) / 5 * 15),
    )

    # Reutilización: máximo 10 puntos.
    forks = max(0, int(repo.get("forks_count") or 0))
    reuse = min(
        10,
        round(log10(forks + 1) / 4 * 10),
    )

    raw_score = (
        maintenance
        + activity_points
        + popularity
        + reuse
    )

    score = round(raw_score / 80 * 100)

    if days_since_commit is None:
        status = "Sin datos"
    elif days_since_commit <= 90:
        status = "Activo"
    elif days_since_commit <= 180:
        status = "En riesgo"
    else:
        status = "Abandonado"

    details = {
        "maintenance": maintenance,
        "commit_activity": activity_points,
        "popularity": popularity,
        "forks": reuse,
        "raw_score": raw_score,
        "max_raw_score": 80,
    }

    return score, status, details


def simplify_repository(
    repo: dict,
    extra: dict | None = None,
    license_from_inventory: str | None = None,
) -> dict:
    """Devuelve solo los campos principales del repositorio."""
    combined = {**repo, **(extra or {})}

    score, status, score_details = _health_score(combined)
    commits_90d = combined.get("commits_last_90_days")

    maintainer_active = (
        not combined.get("archived", False)
        and isinstance(commits_90d, (int, float))
        and not isinstance(commits_90d, bool)
        and commits_90d > 0
        and combined.get("commit_activity_status") == "available"
    )

    license_value = (
        license_from_inventory.strip()
        if license_from_inventory and license_from_inventory.strip()
        else None
    )

    result = {
        # Identificación
        "id": repo.get("id"),
        "name": repo.get("name"),
        "full_name": repo.get("full_name"),
        "url": repo.get("html_url"),

        # Información general
        "description": repo.get("description"),
        "license": license_value,
        "language": repo.get("language"),
        "topics": repo.get("topics", []),
        "homepage": repo.get("homepage"),

        # Popularidad
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),

        # Actividad y mantenimiento
        "last_commit_at": combined.get("last_commit_at"),
        "pushed_at": repo.get("pushed_at"),
        "updated_at": repo.get("updated_at"),
        "open_issues": repo.get("open_issues_count", 0),
        "archived": repo.get("archived", False),
        "maintainer_active": maintainer_active,

        # Health score
        "health_score": score,
        "health_status": status,
        "health_score_details": score_details,
    }

    for key in (
        "commits_last_30_days",
        "commits_last_90_days",
        "commits_last_year",
        "commit_activity_status",
        "detected_languages",
        "detected_stack",
        "integration_methods_suggested",
    ):
        if key in combined:
            result[key] = combined[key]

    return result


async def _repository_enrichment(
    owner: str,
    repo_name: str,
) -> dict:
    """Obtiene lenguajes, archivos raíz y README para heurísticas sin IA."""
    prefix = f"/repos/{owner}/{repo_name}"

    languages = await _get_optional_detail(
        f"{prefix}/languages"
    )
    root_contents = await _get_optional_detail(
        f"{prefix}/contents"
    )
    readme_data = await _get_optional_detail(
        f"{prefix}/readme"
    )

    commit_metrics = await get_commit_activity(
        owner,
        repo_name,
    )

    files = set()

    if isinstance(root_contents, list):
        files = {
            item.get("name", "")
            for item in root_contents
            if isinstance(item, dict)
        }

    detected_stack = [
        label
        for filename, label in MANIFEST_LABELS.items()
        if filename in files
    ]

    if isinstance(languages, dict):
        language_names = sorted(
            languages.keys(),
            key=lambda name: languages[name],
            reverse=True,
        )
    else:
        language_names = []

    readme_text = ""

    if isinstance(readme_data, dict):
        encoded = readme_data.get("content")

        if (
            encoded
            and readme_data.get("encoding") == "base64"
        ):
            try:
                readme_text = (
                    base64.b64decode(encoded)
                    .decode("utf-8", errors="replace")[:150_000]
                )
            except (ValueError, TypeError):
                readme_text = ""

    searchable = readme_text.lower()
    integration_methods = []

    checks = [
        (
            "REST API",
            r"\brest(?:ful)?\s+api\b|\bhttp api\b|\bopenapi\b",
        ),
        ("GraphQL", r"\bgraphql\b"),
        (
            "SDK o cliente",
            (
                r"\bsdk\b|\bclient library\b|\bclient for\b"
                r"|\bpython client\b|\bjavascript client\b"
            ),
        ),
        ("Webhooks", r"\bwebhooks?\b"),
        (
            "CLI",
            r"\bcommand[- ]line interface\b|\bcli\b",
        ),
    ]

    for label, pattern in checks:
        if re.search(pattern, searchable):
            integration_methods.append(label)

    if "Dockerfile" in files:
        integration_methods.append("Docker")

    if (
        "docker-compose.yml" in files
        or "compose.yaml" in files
    ):
        integration_methods.append("Docker Compose")

    return {
        "detected_languages": language_names,
        "detected_stack": detected_stack,
        "integration_methods_suggested": integration_methods,
        **commit_metrics,
    }


async def get_repository(
    owner: str,
    repo: str,
    license_from_inventory: str | None = None,
) -> dict:
    """Obtiene y prepara toda la información del repositorio."""
    data, rate_limit = await github_get(
        f"/repos/{owner}/{repo}"
    )

    extra = await _repository_enrichment(owner, repo)

    extra["last_commit_at"] = await _get_last_commit_at(
        owner,
        repo,
        data.get("default_branch"),
    )

    return {
        "data": simplify_repository(
            data,
            extra,
            license_from_inventory=license_from_inventory,
        ),
        "rate_limit_headers": rate_limit,
    }


async def get_rate_limit() -> dict:
    """Devuelve los límites actuales de la API de GitHub."""
    data, _ = await github_get("/rate_limit")
    resources = data.get("resources", {})

    output = {}

    for name in ("core", "search"):
        quota = resources.get(name, {})
        output[name] = {
            "limit": quota.get("limit"),
            "remaining": quota.get("remaining"),
            "reset": quota.get("reset"),
        }

    return output
