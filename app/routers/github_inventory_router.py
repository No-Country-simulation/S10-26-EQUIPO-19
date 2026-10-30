import httpx
from fastapi import APIRouter, HTTPException, Query

from app.services.github_inventory_service import (
    enrich_github_inventory,
)
from app.schemas.github import GithubInventoryResponse


router = APIRouter(
    prefix="/github",
    tags=["GitHub Inventory"],
)


@router.post(
    "/repositories/sync",
    response_model=GithubInventoryResponse,
)
async def sync_repositories(
    limit: int | None = Query(
        default=None,
        ge=1,
        description="Cantidad máxima de repositorios. Usá 3 para probar.",
    ),
):
    try:
        return await enrich_github_inventory(limit=limit)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="No se pudo completar la consulta a GitHub.",
        ) from exc
