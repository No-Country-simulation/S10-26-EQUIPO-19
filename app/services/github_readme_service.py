import base64
import logging

import httpx

logger = logging.getLogger(__name__)


class GitHubReadmeService:
    BASE_URL = "https://api.github.com"

    def __init__(self, github_token: str):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_readme(self, owner: str, repository: str) -> dict | None:
        url = f"{self.BASE_URL}/repos/{owner}/{repository}/readme"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers=self.headers,
            )

        if response.status_code == 404:
            logger.info("README not found: %s/%s", owner, repository)
            return None

        response.raise_for_status()

        data = response.json()

        content = base64.b64decode(data["content"]).decode("utf-8")

        return {
            "name": data["name"],
            "path": data["path"],
            "sha": data["sha"],
            "html_url": data["html_url"],
            "content": content,
        }
