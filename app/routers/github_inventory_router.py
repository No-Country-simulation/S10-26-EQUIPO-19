import os
import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.core.rate_limit import github_rate_limiter
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
    summary="Sincronizar inventario de repositorios",
    description="Endpoint protegido para sincronización e ingesta masiva hacia Supabase.",
    dependencies=[Depends(github_rate_limiter)],
)
async def sync_repositories(
    limit: int | None = Query(
        default=None,
        ge=1,
        description="Cantidad máxima de repositorios. Usá 3 para probar.",
    ),
    x_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
        description="Clave de autenticación para operaciones de sincronización",
    ),
):
    # Proteger endpoint contra escrituras y consumo no autorizado (Hallazgo H1)
    sync_secret = os.getenv("SYNC_API_KEY")
    if not sync_secret or not x_api_key or x_api_key != sync_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado: se requiere un encabezado 'X-API-Key' válido y la clave debe estar configurada en el servidor.",
        )

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
