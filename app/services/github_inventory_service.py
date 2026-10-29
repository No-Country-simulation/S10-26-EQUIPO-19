import re
import unicodedata
from pathlib import Path

import httpx
import pandas as pd

from app.services.github_repository_service import get_repository


BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL_PATH = BASE_DIR / "data" / "OpenBridge.xlsx"


def normalize_column(column: str) -> str:
    column = str(column).strip().lower()
    column = unicodedata.normalize("NFKD", column)
    column = "".join(
        char for char in column
        if not unicodedata.combining(char)
    )
    return re.sub(r"\s+", "_", column)


def read_excel(limit: int | None = None) -> dict:
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el Excel: {EXCEL_PATH}"
        )

    df = pd.read_excel(EXCEL_PATH)
    df.columns = [normalize_column(col) for col in df.columns]

    required = {"id", "categoria", "full_name"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Faltan columnas: {sorted(missing)}. "
            f"Columnas detectadas: {list(df.columns)}"
        )

    df = df.dropna(subset=["full_name"]).copy()
    df["full_name"] = df["full_name"].astype(str).str.strip()
    df = df[df["full_name"] != ""]
    df = df.drop_duplicates(subset=["full_name"], keep="first")

    repositories = []

    for _, row in df.iterrows():
        full_name = str(row["full_name"]).strip()
        parts = full_name.split("/")

        if len(parts) != 2 or not all(parts):
            continue

        raw_id = row["id"]

        if pd.isna(raw_id):
            inventory_id = None
        elif (
            isinstance(raw_id, (int, float))
            and float(raw_id).is_integer()
        ):
            inventory_id = int(raw_id)
        else:
            inventory_id = str(raw_id).strip()

        category = row["categoria"]

        if pd.isna(category) or not str(category).strip():
            category = "Sin categorizar"
        else:
            category = str(category).strip()

        repositories.append({
            "inventory_id": inventory_id,
            "categoria": category,
            "full_name": full_name,
        })

    if limit is not None:
        repositories = repositories[:limit]

    return {
        "total": len(repositories),
        "repositories": repositories,
    }


async def enrich_github_inventory(limit: int | None = None) -> dict:
    source = read_excel(limit=limit)
    results = []

    for repository in source["repositories"]:
        owner, repo_name = repository["full_name"].split("/", 1)

        try:
            response = await get_repository(owner, repo_name)
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
                "enrichment_status": "error",
                "enrichment_error": str(exc),
            })

    return {
        "total": len(results),
        "successful": sum(
            item["enrichment_status"] == "success"
            for item in results
        ),
        "failed": sum(
            item["enrichment_status"] == "error"
            for item in results
        ),
        "repositories": results,
    }
