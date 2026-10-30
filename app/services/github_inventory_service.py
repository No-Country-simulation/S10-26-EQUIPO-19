import csv
import re
import unicodedata
from pathlib import Path

import httpx

from app.services.github_repository_service import get_repository
from app.services.github_db_service import (
    save_repositories,
)


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "OpenBridge.csv"


def normalize_column(column: str) -> str:
    """Normaliza nombres de columnas del CSV."""
    column = str(column).strip().lower()
    column = unicodedata.normalize("NFKD", column)
    column = "".join(
        char for char in column
        if not unicodedata.combining(char)
    )
    return re.sub(r"\s+", "_", column)


def read_csv(limit: int | None = None) -> dict:
    """Lee el inventario desde un CSV."""
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

        original_columns = reader.fieldnames
        normalized_columns = [
            normalize_column(column)
            for column in original_columns
        ]

        if len(normalized_columns) != len(set(normalized_columns)):
            raise ValueError(
                "Hay nombres de columnas duplicados después "
                "de normalizarlos."
            )

        required = {"id", "categoria", "full_name", "licencia"}
        missing = required - set(normalized_columns)

        if missing:
            raise ValueError(
                f"Faltan columnas: {sorted(missing)}. "
                f"Columnas detectadas: {normalized_columns}"
            )

        repositories = []
        seen_repositories = set()

        for row in reader:
            normalized_row = {
                normalize_column(key): value
                for key, value in row.items()
                if key is not None
            }

            full_name = (
                normalized_row.get("full_name") or ""
            ).strip()

            if not full_name:
                continue

            parts = full_name.split("/")

            if len(parts) != 2 or not all(parts):
                continue

            if full_name in seen_repositories:
                continue

            seen_repositories.add(full_name)

            raw_id = (normalized_row.get("id") or "").strip()

            if not raw_id:
                inventory_id = None
            elif re.fullmatch(r"\d+", raw_id):
                inventory_id = int(raw_id)
            else:
                inventory_id = raw_id

            category = (
                normalized_row.get("categoria") or ""
            ).strip()

            if not category:
                category = "Sin categorizar"

            repositories.append({
                "inventory_id": inventory_id,
                "categoria": category,
                "full_name": full_name,
                "licencia": (
                    (normalized_row.get("licencia") or "").strip()
                    or None
                ),
            })

    if limit is not None:
        repositories = repositories[:limit]

    return {
        "total": len(repositories),
        "repositories": repositories,
    }


async def enrich_github_inventory(
    limit: int | None = None,
) -> dict:
    """Enriquece el inventario con información de GitHub."""
    source = read_csv(limit=limit)
    results = []

    for repository in source["repositories"]:
        owner, repo_name = repository["full_name"].split("/", 1)

        try:
            response = await get_repository(
                owner,
                repo_name,
                license_from_inventory=repository.get("licencia"),
            )
            data = dict(response["data"])

            github_id = data.pop("id", None)

            results.append({
                **data,
                **repository,
                "github_id": github_id,
                "enrichment_status": "success",
                "enrichment_error": None,
            })

        except (ValueError, RuntimeError, httpx.HTTPError) as exc:
            results.append({
                **repository,
                "licencia": None,
                "enrichment_status": "error",
                "enrichment_error": str(exc),
            })

    # Guardar en Supabase solamente los enriquecimientos exitosos.
    successful_repositories = [
        repository
        for repository in results
        if repository["enrichment_status"] == "success"
    ]

    database_result = save_repositories(successful_repositories)

    return {
        "total": len(results),
        "successful": len(successful_repositories),
        "failed": len(results) - len(successful_repositories),
        "repositories": results,
        "database": database_result,
    }
