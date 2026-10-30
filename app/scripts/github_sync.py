
import asyncio
import csv
import json
import re
import unicodedata
from pathlib import Path

from app.clients.github_client import github_get
from app.services.github_db_service import save_repositories
from app.services.github_repository_service import _health_score



BASE_DIR = Path(__file__).resolve().parents[2]
CSV_PATH = BASE_DIR / "app" / "data" / "OpenBridge.csv"
OUTPUT_PATH = BASE_DIR / "github_sync_preview.json"

# Para probar con pocos repositorios.
# Cambialo a None para procesar todos.
LIMIT = 3


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


async def get_commit_metrics(
    owner: str,
    repo_name: str,
) -> dict:
    """Obtiene el último commit y la actividad de los últimos 90 días."""
    prefix = f"/repos/{owner}/{repo_name}"

    result = {
        "last_commit_at": None,
        "commits_last_90_days": None,
        "commit_activity_status": "unavailable",
    }

    try:
        commits, _ = await github_get(
            f"{prefix}/commits",
            params={"per_page": 1},
        )

        if isinstance(commits, list) and commits:
            commit = commits[0].get("commit") or {}
            committer = commit.get("committer") or {}
            author = commit.get("author") or {}

            result["last_commit_at"] = (
                committer.get("date") or author.get("date")
            )

    except Exception as exc:
        print(f"No se pudo obtener el último commit: {exc}")

    try:
        activity, _ = await github_get(
            f"{prefix}/stats/commit_activity"
        )

        if isinstance(activity, list):
            weekly_totals = [
                max(0, int(week.get("total", 0)))
                for week in activity[-13:]
                if isinstance(week, dict)
            ]

            result["commits_last_90_days"] = sum(weekly_totals)
            result["commit_activity_status"] = "available"

    except Exception as exc:
        print(f"No se pudo obtener la actividad de commits: {exc}")

    return result


async def sync_repository(repository: dict) -> dict:
    """Obtiene los datos dinámicos de GitHub y conserva la licencia del CSV."""
    full_name = repository["full_name"]
    owner, repo_name = full_name.split("/", maxsplit=1)

    data, _ = await github_get(
        f"/repos/{owner}/{repo_name}"
    )

    commit_metrics = await get_commit_metrics(owner, repo_name)

    score, status, score_details = _health_score({
        **data,
        **commit_metrics,
    })

    return {
        **repository,
        "github_id": data.get("id"),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "updated_at": data.get("updated_at"),
        "pushed_at": data.get("pushed_at"),
        "last_commit_at": commit_metrics["last_commit_at"],
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

    # Guardar en Supabase.
    print("\nGuardando repositorios en Supabase...")

    database_result = save_repositories(results)

    # Generar JSON de preview.
    output = {
        "total": len(inventory),
        "successful": len(results),
        "failed": len(errors),
        "repositories": results,
        "errors": errors,
        "database": database_result,
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
    print(f"Preview generado: {OUTPUT_PATH}")

    if database_result["errors"]:
        print("\nErrores de Supabase:")

        for error in database_result["errors"]:
            print(f"  {error['full_name']}: {error['error']}")


if __name__ == "__main__":
    asyncio.run(main())
