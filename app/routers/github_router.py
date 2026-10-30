import httpx
from fastapi import APIRouter, HTTPException

from app.services.github_repository_service import (
    get_rate_limit,
    get_repository,
)

router = APIRouter(
    prefix="/github",
    tags=["GitHub"],
)


def _raise_http_error(exc: Exception) -> None:
    """Convierte errores del servicio en respuestas HTTP."""
    if isinstance(exc, ValueError):
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if isinstance(exc, RuntimeError):
        raise HTTPException(
            status_code=429,
            detail=str(exc),
        ) from exc

    if isinstance(exc, httpx.HTTPStatusError):
        raise HTTPException(
            status_code=502,
            detail="GitHub devolvió un error al procesar la solicitud.",
        ) from exc

    if isinstance(exc, httpx.HTTPError):
        raise HTTPException(
            status_code=502,
            detail="No se pudo conectar con GitHub.",
        ) from exc

    raise HTTPException(
        status_code=500,
        detail="Ocurrió un error interno al consultar GitHub.",
    ) from exc


@router.get("/repository/{owner}/{repo}")
async def repository_endpoint(
    owner: str,
    repo: str,
):
    """Obtiene la información enriquecida de un repositorio."""
    try:
        return await get_repository(owner, repo)
    except (ValueError, RuntimeError, httpx.HTTPError) as exc:
        _raise_http_error(exc)


@router.get("/rate-limit")
async def rate_limit_endpoint():
    """Consulta los límites de uso de la API de GitHub."""
    try:
        return await get_rate_limit()
    except (ValueError, RuntimeError, httpx.HTTPError) as exc:
        _raise_http_error(exc)
