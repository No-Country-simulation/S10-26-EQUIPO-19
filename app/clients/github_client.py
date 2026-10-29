import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

GITHUB_API_URL = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

_token = os.getenv("GITHUB_TOKEN")
if _token:
    HEADERS["Authorization"] = f"Bearer {_token}"


def get_rate_limit_headers(response: httpx.Response) -> dict:
    """Extrae los encabezados de cuota de GitHub."""
    return {
        "limit": response.headers.get("X-RateLimit-Limit"),
        "remaining": response.headers.get("X-RateLimit-Remaining"),
        "reset": response.headers.get("X-RateLimit-Reset"),
    }


async def github_get(endpoint: str, params: dict | None = None):
    """Realiza un GET a GitHub y devuelve (JSON, encabezados de cuota)."""
    async with httpx.AsyncClient(headers=HEADERS, timeout=25.0) as client:
        response = await client.get(
            f"{GITHUB_API_URL}{endpoint}",
            params=params,
        )

    if response.status_code == 404:
        raise ValueError("No se encontró el recurso solicitado en GitHub.")
    if response.status_code in (403, 429):
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining == "0":
            raise RuntimeError(
                "Se agotó la cuota de GitHub. "
                "Consultá /github/rate-limit para ver el reinicio."
            )
        raise RuntimeError(
            "GitHub rechazó la solicitud. Revisá el token o los límites de la API."
        )

    response.raise_for_status()
    return response.json(), get_rate_limit_headers(response)


async def get_commit_activity(owner: str, repo_name: str) -> dict:
    """Consulta y resume las estadísticas de actividad de commits."""
    result = {
        "commits_last_30_days": None,
        "commits_last_90_days": None,
        "commits_last_year": None,
        "commit_activity_status": "unavailable",
    }

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=25.0,
        base_url=GITHUB_API_URL,
    ) as client:
        for attempt in range(2):
            try:
                response = await client.get(
                    f"/repos/{owner}/{repo_name}/stats/commit_activity"
                )

                if response.status_code == 202:
                    result["commit_activity_status"] = "pending"
                    if attempt == 0:
                        await asyncio.sleep(3)
                        continue
                    break

                if response.status_code == 204:
                    result["commit_activity_status"] = "no_data"
                    break

                response.raise_for_status()
                weekly_activity = response.json()
                if not isinstance(weekly_activity, list):
                    break

                totals = [
                    max(0, int(week.get("total", 0)))
                    for week in weekly_activity[-52:]
                    if isinstance(week, dict)
                ]
                result.update({
                    "commits_last_30_days": sum(totals[-4:]),
                    "commits_last_90_days": sum(totals[-13:]),
                    "commits_last_year": sum(totals),
                    "commit_activity_status": "available",
                })
                break

            except (httpx.HTTPError, ValueError, TypeError) as exc:
                print(
                    f"Error en estadísticas de {owner}/{repo_name}: "
                    f"{type(exc).__name__}"
                )
                break

    return result
