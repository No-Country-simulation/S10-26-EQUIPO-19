from typing import Any

from pydantic import BaseModel


class GithubInventoryResponse(BaseModel):
    total: int
    successful: int
    failed: int
    repositories: list[dict[str, Any]]
