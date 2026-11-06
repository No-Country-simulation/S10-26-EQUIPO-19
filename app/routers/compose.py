import re
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from app.core.rate_limit import repositories_rate_limiter
from app.services.compose_generator import ComposeGeneratorService

router = APIRouter(prefix="/api/v1", tags=["Compose Generator"])

REPO_REGEX = re.compile(r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$")


class ComposeRequest(BaseModel):
    repositories: List[str] = Field(
        ...,
        description="Herramientas del stack recomendado (full_name)",
        examples=[["keycloak/keycloak", "traccar/traccar", "saleor/saleor"]],
    )


generator_service = ComposeGeneratorService()


@router.post("/compose", dependencies=[Depends(repositories_rate_limiter)])
def generate_compose(payload: ComposeRequest):
    repos = payload.repositories

    if len(repos) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La lista de repositorios no puede estar vacía."
        )

    if len(repos) > 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se pueden solicitar más de 10 repositorios simultáneamente."
        )

    for repo in repos:
        if not isinstance(repo, str) or not REPO_REGEX.match(repo):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El formato del repositorio '{repo}' es inválido. Debe ser 'owner/repo'."
            )

    return generator_service.generate(repos)
