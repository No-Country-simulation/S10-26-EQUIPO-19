
import asyncio
import csv
import json
import re
import unicodedata
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.clients.github_client import github_get
from app.services.github_db_service import (
    get_commit_metrics_record,
    sync_repositories,
    update_commit_metrics,
)
from app.services.github_repository_service import _health_score


BASE_DIR = Path(__file__).resolve().parents[2]
CSV_PATH = BASE_DIR / "app" / "data" / "OpenBridge.csv"
OUTPUT_PATH = BASE_DIR / "github_sync_preview.json"

# Para probar con pocos repositorios.
# Cambialo a None para procesar todos.
LIMIT = 3

METRICS_INTERVAL = timedelta(days=7)


def normalize_column(value: str) -> str:
    """Normaliza nombres de columnas del CSV."""
    value = str(value).strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(
        char for char in value
        if not unicodedata.combining(char)
    )
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")


def get_full_name(value: str | None) -> str | None:
    """Extrae owner/repo desde un nombre o una URL de GitHub."""
    if not value:
        return None

    value = value.strip().rstrip("/")

    value = re.sub(
        r"^https?://github\.com/",
        "",
        value,
        flags=re.IGNORECASE,
    )
    value = value.removesuffix(".git")

    parts = value.split("/")

    if len(parts) < 2:
        return None

    owner, repo = parts[0], parts[1]

    if not owner or not repo:
        return None

    if not re.fullmatch(r"[A-Za-z0-9-]+", owner):
        return None

    if not re.fullmatch(r"[A-Za-z0-9._-]+", repo):
        return None

    return f"{owner}/{repo}"


def read_inventory() -> list[dict]:
    """Lee el inventario desde el CSV."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el CSV: {CSV_PATH}"
        )

    with CSV_PATH.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("El CSV no tiene encabezados.")

        columns = [
            normalize_column(column)
            for column in reader.fieldnames
        ]

        if len(columns) != len(set(columns)):
            raise ValueError(
                "Hay columnas duplicadas después de normalizarlas."
            )

        required = {"id", "categoria", "full_name", "licencia"}
        missing = required - set(columns)

        if missing:
            raise ValueError(
                f"Faltan columnas en el CSV: {sorted(missing)}. "
                f"Columnas encontradas: {columns}"
            )

        repositories = []
        seen = set()

        for row in reader:
            normalized_row = {
                normalize_column(key): value
                for key, value in row.items()
                if key is not None
            }

            full_name = get_full_name(
                normalized_row.get("full_name")
            )

            if not full_name or full_name in seen:
                continue

            seen.add(full_name)

            raw_id = (normalized_row.get("id") or "").strip()

            if not raw_id:
                inventory_id = None
            elif re.fullmatch(r"\d+", raw_id):
                inventory_id = int(raw_id)
            else:
                inventory_id = raw_id

            categoria = (
                normalized_row.get("categoria") or ""
            ).strip() or "Sin categorizar"

            licencia = (
                normalized_row.get("licencia") or ""
            ).strip() or None

            repositories.append({
                "inventory_id": inventory_id,
                "categoria": categoria,
                "full_name": full_name,
                "licencia": licencia,
            })

    if LIMIT is not None:
        repositories = repositories[:LIMIT]

    return repositories


async def get_last_commit_at(
    owner: str,
    repo_name: str,
) -> str | None:
    """Obtiene la fecha del último commit."""
    try:
        commits, _ = await github_get(
            f"/repos/{owner}/{repo_name}/commits",
            params={"per_page": 1},
        )

        if isinstance(commits, list) and commits:
            commit = commits[0].get("commit") or {}
            committer = commit.get("committer") or {}
            author = commit.get("author") or {}

            return committer.get("date") or author.get("date")

    except Exception as exc:
        print(f"No se pudo obtener el último commit: {exc}")

    return None


async def get_commit_activity_metrics(
    owner: str,
    repo_name: str,
) -> dict:
    """Obtiene las métricas de actividad de commits."""
    result = {
        "commits_last_30_days": None,
        "commits_last_90_days": None,
        "commits_last_year": None,
        "commit_activity_status": "unavailable",
    }

    try:
        activity, _ = await github_get(
            f"/repos/{owner}/{repo_name}/stats/commit_activity"
        )

        if not isinstance(activity, list):
            return result

        now = datetime.now(UTC)
        days_30 = now - timedelta(days=30)
        days_90 = now - timedelta(days=90)
        days_365 = now - timedelta(days=365)

        commits_30 = 0
        commits_90 = 0
        commits_year = 0

        for week in activity:
            if not isinstance(week, dict):
                continue

            week_timestamp = week.get("week")

            if week_timestamp is None:
                continue

            week_date = datetime.fromtimestamp(
                week_timestamp,
                tz=UTC,
            )

            total = max(0, int(week.get("total", 0)))

            if week_date >= days_30:
                commits_30 += total

            if week_date >= days_90:
                commits_90 += total

            if week_date >= days_365:
                commits_year += total

        result.update({
            "commits_last_30_days": commits_30,
            "commits_last_90_days": commits_90,
            "commits_last_year": commits_year,
            "commit_activity_status": "available",
        })

    except Exception as exc:
        print(
            f"No se pudo obtener la actividad de commits "
            f"de {owner}/{repo_name}: {exc}"
        )

    return result


def should_sync_metrics(metrics_record: dict | None) -> bool:
    """Comprueba si las métricas necesitan actualizarse."""
    if not metrics_record:
        return True

    measured_at = metrics_record.get("measured_at")

    if not measured_at:
        return True

    try:
        measured_at = datetime.fromisoformat(
            measured_at.replace("Z", "+00:00")
        )

        if measured_at.tzinfo is None:
            measured_at = measured_at.replace(tzinfo=UTC)

    except (TypeError, ValueError):
        return True

    return (
        datetime.now(UTC) - measured_at
        >= METRICS_INTERVAL
    )


async def sync_repository(repository: dict) -> dict:
    """Obtiene los datos dinámicos de GitHub."""
    full_name = repository["full_name"]
    owner, repo_name = full_name.split("/", maxsplit=1)

    data, _ = await github_get(
        f"/repos/{owner}/{repo_name}"
    )

    last_commit_at = await get_last_commit_at(
        owner,
        repo_name,
    )

    score, status, score_details = _health_score({
        **data,
        "last_commit_at": last_commit_at,
    })

    return {
        **repository,
        "github_id": data.get("id"),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "updated_at": data.get("updated_at"),
        "pushed_at": data.get("pushed_at"),
        "last_commit_at": last_commit_at,
        "archived": data.get("archived", False),
        "disabled": data.get("disabled", False),
        "health_score": score,
        "health_status": status,
        "health_score_details": score_details,
    }


async def main() -> None:
    inventory = read_inventory()

    results = []
    errors = []

    print(f"Repositorios para procesar: {len(inventory)}")

    for index, repository in enumerate(inventory, start=1):
        full_name = repository["full_name"]

        print(
            f"[{index}/{len(inventory)}] "
            f"Consultando {full_name}..."
        )

        try:
            result = await sync_repository(repository)
            results.append(result)

            print(
                f"  OK - health_score: {result['health_score']}"
            )

        except Exception as exc:
            errors.append({
                "inventory_id": repository["inventory_id"],
                "full_name": full_name,
                "error": str(exc),
            })
            print(f"  ERROR - {exc}")

    # Sincronización general en Supabase.
    print("\nGuardando repositorios en Supabase...")

    database_result = sync_repositories(results)

    # Actualización semanal de métricas de commits.
    print("\nComprobando métricas de commits...")

    saved_by_name = {
        item["full_name"]: item
        for item in database_result["saved"]
    }

    metrics_results = []
    metrics_errors = []

    for repository in results:
        full_name = repository["full_name"]
        saved = saved_by_name.get(full_name)

        if not saved:
            continue

        repository_id = saved["repository_id"]
        owner, repo_name = full_name.split("/", maxsplit=1)

        try:
            metrics_record = get_commit_metrics_record(
                repository_id
            )

            if not should_sync_metrics(metrics_record):
                print(f"  OMITIDO - {full_name}: métricas actualizadas")
                metrics_results.append({
                    "full_name": full_name,
                    "status": "skipped",
                    "measured_at": metrics_record.get("measured_at"),
                })
                continue

            print(f"  ACTUALIZANDO - {full_name}")

            commit_metrics = await get_commit_activity_metrics(
                owner,
                repo_name,
            )

            if commit_metrics["commit_activity_status"] != "available":
                raise RuntimeError(
                    "GitHub no devolvió métricas de actividad disponibles."
                )

            update_commit_metrics(
                repository_id,
                commit_metrics,
            )

            metrics_results.append({
                "full_name": full_name,
                "status": "updated",
                **commit_metrics,
            })

            print(f"  OK - métricas actualizadas para {full_name}")

        except Exception as exc:
            metrics_errors.append({
                "full_name": full_name,
                "error": str(exc),
            })
            print(f"  ERROR en métricas - {exc}")

    # Generar JSON de preview.
    output = {
        "total": len(inventory),
        "successful": len(results),
        "failed": len(errors),
        "repositories": results,
        "errors": errors,
        "database": database_result,
        "commit_metrics": {
            "successful": sum(
                item["status"] == "updated"
                for item in metrics_results
            ),
            "skipped": sum(
                item["status"] == "skipped"
                for item in metrics_results
            ),
            "failed": len(metrics_errors),
            "repositories": metrics_results,
            "errors": metrics_errors,
        },
    }

    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Mostrar resumen.
    print("\nSincronización finalizada.")
    print(f"Correctos en GitHub: {len(results)}")
    print(f"Fallidos en GitHub: {len(errors)}")
    print(f"Guardados en Supabase: {database_result['successful']}")
    print(f"Fallidos en Supabase: {database_result['failed']}")
    print(
        "Métricas actualizadas: "
        f"{output['commit_metrics']['successful']}"
    )
    print(
        "Métricas omitidas: "
        f"{output['commit_metrics']['skipped']}"
    )
    print(
        "Errores de métricas: "
        f"{output['commit_metrics']['failed']}"
    )
    print(f"Preview generado: {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
