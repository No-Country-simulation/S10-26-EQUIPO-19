from supabase import Client

from app.database import get_supabase_client
from app.services.llm_service import LLMService


class BusinessCaseSearchService:

    def __init__(
        self,
        llm: LLMService,
        supabase: Client | None = None,
    ):
        self.llm = llm
        self.supabase = supabase or get_supabase_client()

        if self.supabase is None:
            raise RuntimeError("Supabase client is not available")

    def search_business_cases(
        self,
        limit: int = 10,
    ) -> list[dict]:

        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")

        response = (
            self.supabase
            .table("business_cases")
            .select("*")
            .limit(limit)
            .execute()
        )

        return response.data or []

    def get_integrations_by_business_case_ids(
        self,
        business_case_ids: list[int],
    ) -> list[dict]:

        if not business_case_ids:
            return []

        relations_response = (
            self.supabase
            .table("integration_business_cases")
            .select("integration_id, business_case_id")
            .in_("business_case_id", business_case_ids)
            .execute()
        )

        relations = relations_response.data or []

        business_case_ids_by_integration = {}

        for relation in relations:
            integration_id = relation["integration_id"]
            business_case_id = relation["business_case_id"]

            business_case_ids_by_integration.setdefault(
                integration_id,
                [],
            ).append(business_case_id)

        integration_ids = list(business_case_ids_by_integration)

        if not integration_ids:
            return []

        integrations_response = (
            self.supabase
            .table("integrations")
            .select("*")
            .in_("id", integration_ids)
            .execute()
        )

        integrations = integrations_response.data or []

        for integration in integrations:
            integration["business_case_ids"] = (
                business_case_ids_by_integration.get(
                    integration["id"],
                    [],
                )
            )

        return integrations

    def get_repositories_by_integration_ids(
        self,
        integration_ids: list[int],
    ) -> dict[int, list[dict]]:

        if not integration_ids:
            return {}

        relations_response = (
            self.supabase
            .table("integration_repositories")
            .select("integration_id, repository_id, role")
            .in_("integration_id", integration_ids)
            .execute()
        )

        relations = relations_response.data or []

        repository_ids = list({
            relation["repository_id"]
            for relation in relations
        })

        if not repository_ids:
            return {}

        repositories_response = (
            self.supabase
            .table("repositories")
            .select("*, metrics(health_status)")
            .in_("id", repository_ids)
            .execute()
        )

        repositories_by_id = {
            repository["id"]: repository
            for repository in repositories_response.data or []
        }

        for repository in repositories_by_id.values():
            metrics = repository.get("metrics") or {}

            if isinstance(metrics, list):
                metrics = metrics[0] if metrics else {}

            repository["health_status"] = metrics.get("health_status")

        grouped_repositories = {
            integration_id: []
            for integration_id in integration_ids
        }

        for relation in relations:
            repository = repositories_by_id.get(
                relation["repository_id"]
            )

            if repository:
                grouped_repositories[
                    relation["integration_id"]
                ].append({
                    "repository": repository,
                    "role": relation["role"],
                })

        return grouped_repositories

    def get_integrations_between_repositories(
        self,
        repository_ids: list[int],
    ) -> dict[tuple[int, int], dict]:
        """Ideas del catálogo que unen a dos o más repositorios del stack.

        Devuelve {(id_menor, id_mayor): {"code": ..., "purpose": ...}}.
        """

        repository_ids = list({rid for rid in repository_ids if rid is not None})

        if len(repository_ids) < 2:
            return {}

        relations_response = (
            self.supabase
            .table("integration_repositories")
            .select("integration_id, repository_id")
            .in_("repository_id", repository_ids)
            .execute()
        )

        repos_by_integration: dict[int, set[int]] = {}
        for relation in relations_response.data or []:
            repos_by_integration.setdefault(
                relation["integration_id"], set()
            ).add(relation["repository_id"])

        shared_ids = [
            integration_id
            for integration_id, repos in repos_by_integration.items()
            if len(repos) >= 2
        ]

        if not shared_ids:
            return {}

        integrations_response = (
            self.supabase
            .table("integrations")
            .select("id, code, purpose")
            .in_("id", shared_ids)
            .execute()
        )

        pairs: dict[tuple[int, int], dict] = {}
        for integration in integrations_response.data or []:
            repos = sorted(repos_by_integration.get(integration["id"], set()))
            for i, repo_a in enumerate(repos):
                for repo_b in repos[i + 1:]:
                    pairs.setdefault(
                        (repo_a, repo_b),
                        {"code": integration.get("code"), "purpose": integration.get("purpose")},
                    )

        return pairs

    def build_integration_context(
        self,
        integrations: list[dict],
        repositories_by_integration: dict[int, list[dict]],
    ) -> list[dict]:

        result = []

        for integration in integrations:
            integration_id = integration["id"]

            integration_context = {
                **integration,
                "integration_code": f"INT-{integration_id:03d}",
                "business_case_ids": integration.get("business_case_ids", []),
                "repositories": [
                    {
                        "repository_id": item["repository"]["id"],
                        "full_name": item["repository"]["full_name"],
                        "description": item["repository"]["description"],
                        "language": item["repository"]["language"],
                        "url": item["repository"]["url"],
                        "license": item["repository"].get("license"),
                        "health_score": item["repository"].get("health_score"),
                        "role": item["role"],
                    }
                    for item in repositories_by_integration.get(
                        integration_id,
                        [],
                    )
                ],
            }

            result.append(integration_context)

        return result

    async def find_relevant_business_cases(
        self,
        query: str,
        limit: int = 3,
    ) -> list[dict]:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if limit < 1 or limit > 10:
            raise ValueError("limit must be between 1 and 10")

        business_cases = self.search_business_cases(limit=100)

        if not business_cases:
            return []

        cases_context = "\n".join(
            (
                f"ID: {case['id']}\n"
                f"Nombre: {case['name']}\n"
                f"Descripción: {case['description']}"
            )
            for case in business_cases
        )

        prompt = f"""
    Sos un experto en arquitectura de software.

    Tu tarea es identificar qué casos de negocio existentes
    son más relevantes para la necesidad del usuario.

    Consulta del usuario:
    {query}

    Casos de negocio disponibles:
    {cases_context}

    Instrucciones:
    - Seleccioná únicamente casos realmente relacionados.
    - Considerá el contexto completo del negocio, no solo palabras coincidentes.
    - No inventes casos ni IDs.
    - Si ningún caso es suficientemente relevante, devolvé una lista vacía.
    - Devolvé como máximo {limit} casos.
    - Ordená los resultados por relevancia.

    Respondé exclusivamente en JSON con este formato:

    {{
        "business_case_ids": [1, 5]
    }}
    """

        response = await self.llm.generate_json_response(prompt)

        import json

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            return []

        selected_ids = result.get("business_case_ids", [])

        if not isinstance(selected_ids, list):
            return []

        cases_by_id = {
            case["id"]: case
            for case in business_cases
        }

        selected_cases = []

        for case_id in selected_ids:
            if case_id in cases_by_id and cases_by_id[case_id] not in selected_cases:
                selected_cases.append(cases_by_id[case_id])

            if len(selected_cases) >= limit:
                break

        return selected_cases
