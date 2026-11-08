import re
import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.rate_limit import github_rate_limiter
from app.services.github_repository_service import (
    get_repository,
)

router = APIRouter(
    prefix="/github",
    tags=["GitHub"],
    dependencies=[Depends(github_rate_limiter)],
)

# Validación estricta para prevenir path traversal (H2) y caracteres inválidos
GITHUB_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]+$")


def _validate_github_identifier(value: str, field_name: str) -> None:
    """Valida que owner o repo no contengan path traversal ('..') ni caracteres de control."""
    if not value or not GITHUB_NAME_PATTERN.match(value) or value in (".", "..") or ".." in value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El valor de '{field_name}' no es válido. Solo se permiten caracteres alfanuméricos, guiones y puntos sin secuencias de navegación.",
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
    _validate_github_identifier(owner, "owner")
    _validate_github_identifier(repo, "repo")
    try:
        return await get_repository(owner, repo)
    except (ValueError, RuntimeError, httpx.HTTPError) as exc:
        _raise_http_error(exc)
