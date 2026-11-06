import logging
import os
import json

from dotenv import load_dotenv

from app.orchestrator.requirements_analyzer import RequirementsAnalyzer
from app.orchestrator.compatibility_engine import CompatibilityEngine
from app.orchestrator.context_builder import ContextBuilder

from app.services.gemini_embedding_service import GeminiEmbeddingService
from app.services.llm_service import LLMService
from app.services.sql_search_service import SQLSearchService
from app.services.vector_search_service import VectorSearchService
from app.services.business_case_search_service import BusinessCaseSearchService

logger = logging.getLogger(__name__)

load_dotenv()


class AssistantOrchestrator:

    def __init__(
        self,
        requirements_analyzer: RequirementsAnalyzer | None = None,
        sql_search: SQLSearchService | None = None,
        vector_search: VectorSearchService | None = None,
        compatibility_engine: CompatibilityEngine | None = None,
        context_builder: ContextBuilder | None = None,
        llm: LLMService | None = None,
        business_case_search: BusinessCaseSearchService | None = None,
    ):
        gemini_api_key = os.getenv("GEMINI_API_KEY")


        if not gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")



        self.requirements_analyzer = (
            requirements_analyzer or RequirementsAnalyzer()
        )

        self.sql_search = sql_search or SQLSearchService()

        if vector_search is None:
            gemini_embedding = GeminiEmbeddingService(
                api_key=gemini_api_key
            )
            vector_search = VectorSearchService(gemini=gemini_embedding)

        self.vector_search = vector_search

        self.compatibility_engine = (
            compatibility_engine or CompatibilityEngine()
        )

        self.context_builder = context_builder or ContextBuilder()

        self.llm = llm or LLMService(
            api_key=gemini_api_key,
            model=os.getenv(
                "GEMINI_MODEL",
                LLMService.DEFAULT_MODEL,
            ),
        )

        self.business_case_search = (
            business_case_search or BusinessCaseSearchService(llm=self.llm)
        )



    async def process_message(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
    ) -> dict:

        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        # No se registra el texto del usuario, solo su largo (privacidad).
        logger.info("Processing assistant query (%s chars)", len(message))

        # 1. Analyze user requirements.
        requirements = self.requirements_analyzer.analyze(message)

        # 1.1 Find relevant business cases.
        business_cases = await self.business_case_search.find_relevant_business_cases(
            query=message,
        )

        logger.info(
            "Relevant business cases found: %s",
            [case["id"] for case in business_cases],
        )

        # 1.2 Retrieve integrations associated with business cases.
        business_case_ids = [
            case["id"]
            for case in business_cases
        ]

        integrations = self.business_case_search.get_integrations_by_business_case_ids(
            business_case_ids=business_case_ids,
        )

        logger.info(
            "Business case integrations found: %s",
            len(integrations),
        )

        # 1.3 Retrieve repositories associated with integrations.
        integration_ids = [
            integration["id"]
            for integration in integrations
        ]

        repositories_by_integration = (
            self.business_case_search.get_repositories_by_integration_ids(
                integration_ids=integration_ids,
            )
        )

        logger.info(
            "Repositories grouped by integration: %s",
            sum(
                len(repositories)
                for repositories in repositories_by_integration.values()
            ),
        )

        # 1.4 Build business integration context.
        integration_context = self.business_case_search.build_integration_context(
            integrations=integrations,
            repositories_by_integration=repositories_by_integration,
        )

        logger.info(
            "Integration context built: %s integrations",
            len(integration_context),
        )

        logger.info("Detected requirements: %s", requirements)

        # 2. Search repositories using SQL filters.
        sql_results = self.sql_search.search_repositories(
            category_slug=requirements.get("category_slug"),
            language=requirements.get("language"),
            license=requirements.get("license"),
            min_stars=requirements.get("min_stars"),
            min_health_score=requirements.get("min_health_score"),
            exclude_archived=requirements.get("exclude_archived", True),
            limit=100,
        )

        logger.info(
            "Vector search parameters: %s",
            {
                "match_threshold": 0.3,
                "match_count": 50,
                "language": requirements.get("language"),
                "category_slug": requirements.get("category_slug"),
                "license": requirements.get("license"),
                "min_stars": requirements.get("min_stars"),
                "min_health_score": requirements.get("min_health_score"),
                "exclude_archived": requirements.get("exclude_archived", True),
            },
        )

        # 3. Search semantically using README embeddings.
        semantic_results = await self.vector_search.search(
            query=message,
            match_threshold=0.3,
            match_count=50,
            language=requirements.get("language"),
            category_slug=requirements.get("category_slug"),
            license=requirements.get("license"),
            technologies=None,
            min_stars=requirements.get("min_stars"),
            min_health_score=requirements.get("min_health_score"),
            exclude_archived=requirements.get("exclude_archived", True),
        )

        logger.info("SQL repositories found: %s", len(sql_results))
        logger.info("Semantic chunks found: %s", len(semantic_results))

        logger.info(
            "SQL repository IDs: %s",
            [repo["id"] for repo in sql_results],
        )

        logger.info(
            "Semantic repository IDs: %s",
            list({
                result["repository_id"]
                for result in semantic_results
            }),
        )

        # 4. Combine SQL repositories with semantic results.
        repositories_by_id = {
            repository["id"]: repository
            for repository in sql_results
        }

        logger.info(
            "Retrieved repositories: %s",
            [
                {
                    "id": repository.get("id"),
                    "full_name": repository.get("full_name"),
                    "category": repository.get("category_slug"),
                }
                for repository in repositories_by_id.values()
            ],
        )

        semantic_repository_ids = {
            result["repository_id"]
            for result in semantic_results
        }

        missing_ids = semantic_repository_ids - repositories_by_id.keys()

        if missing_ids:
            additional_repositories = self.sql_search.get_repositories_by_ids(
                list(missing_ids)
            )

            repositories_by_id.update({
                repository["id"]: repository
                for repository in additional_repositories
            })

            logger.info(
                "Additional repositories recovered from semantic search: %s",
                [
                    repository["full_name"]
                    for repository in additional_repositories
                ],
            )

        for repositories in repositories_by_integration.values():
            for item in repositories:
                repository = item["repository"]
                repository_id = repository["id"]

                existing_repository = repositories_by_id.get(repository_id, {})

                repositories_by_id[repository_id] = {
                    **repository,
                    **existing_repository,
                }

        similarities = {}

        for result in semantic_results:
            repository_id = result["repository_id"]
            similarity = result["similarity"]

            similarities[repository_id] = max(
                similarities.get(repository_id, 0),
                similarity,
            )

        # 5. Evaluate repository compatibility.
        ranked_repositories = self.compatibility_engine.rank(
            repositories=list(repositories_by_id.values()),
            requirements=requirements,
            similarities=similarities,
        )

        # 6. Build LLM context.
        context = self.context_builder.build(
            query=message,
            requirements=requirements,
            repositories=ranked_repositories,
            semantic_results=semantic_results,
            integration_context=integration_context,
        )

        # Historial reciente para las preguntas de seguimiento (máx. 6 mensajes).
        history_text = self._format_history(conversation_history)
        if history_text:
            context = f"CONVERSACIÓN PREVIA:\n{history_text}\n\n{context}"

        logger.debug("Context length: %s", len(context))

        architecture_response = await self.llm.generate_architecture(context)

        try:
            architecture_data = json.loads(architecture_response)
        except json.JSONDecodeError:
            logger.exception("Failed to parse generated architecture JSON")
            architecture_data = {}

        valid_components = []

        for component in architecture_data.get("components", []):
            repository_id = component.get("repository_id")
            repository = repositories_by_id.get(repository_id)

            if not repository:
                logger.warning(
                    "Architecture component references unknown repository: %s",
                    repository_id,
                )
                continue

            if component.get("full_name") != repository.get("full_name"):
                logger.warning(
                    "Architecture component name mismatch for repository ID %s",
                    repository_id,
                )
                continue

            component["license"] = repository.get("license")
            component["health_score"] = repository.get("health_score")
            component["health_status"] = repository.get("health_status")
            component["is_archived"] = bool(repository.get("archived", False))

            logger.info(
                "Validated architecture component: %s",
                component,
            )

            valid_components.append(component)

        architecture_data["components"] = valid_components

        valid_keys = {component["key"] for component in valid_components}

        valid_connections = []

        integration_codes_by_pair = {}

        for integration in integration_context:
            repository_ids = {
                item.get("repository", {}).get("id")
                for item in integration.get("repositories", [])
                if item.get("repository", {}).get("id") is not None
            }

            for repository_id_a in repository_ids:
                for repository_id_b in repository_ids:
                    if repository_id_a >= repository_id_b:
                        continue

                    integration_codes_by_pair[
                        (repository_id_a, repository_id_b)
                    ] = integration.get("integration_code")

        for connection in architecture_data.get("connections", []):
            if (
                connection.get("from") not in valid_keys
                or connection.get("to") not in valid_keys
            ):
                logger.warning(
                    "Discarding connection with invalid references: %s",
                    connection,
                )
                continue

            from_key = connection.get("from")
            to_key = connection.get("to")

            from_component = next(
                component
                for component in valid_components
                if component["key"] == from_key
            )

            to_component = next(
                component
                for component in valid_components
                if component["key"] == to_key
            )

            repository_ids = sorted([
                from_component["repository_id"],
                to_component["repository_id"],
            ])

            connection["integration_code"] = integration_codes_by_pair.get(
                tuple(repository_ids)
            )
            # Solo es verificada si existe una idea del catálogo que une a ambas.
            connection["verified"] = connection["integration_code"] is not None

            valid_connections.append(connection)

        architecture_data["connections"] = valid_connections

        response_context = (
            f"{context}\n\n"
            "ARQUITECTURA TÉCNICA VALIDADA:\n"
            f"{json.dumps(architecture_data, ensure_ascii=False, indent=2)}\n\n"
            "IMPORTANTE: La arquitectura anterior es la propuesta definitiva. "
            "La respuesta textual debe describir exactamente esos componentes. "
            "No agregues alternativas ni repositorios que no formen parte "
            "de la arquitectura validada."
        )

        answer = await self.llm.generate_response(response_context)

        logger.info(
            "Final validated architecture: %s",
            json.dumps(architecture_data, ensure_ascii=False, indent=2),
        )

        if valid_components:
            repository_id = valid_components[0]["repository_id"]
            repository = repositories_by_id[repository_id]

            logger.info(
                "Architecture repository metadata: %s",
                {
                    "license": repository.get("license"),
                    "health_score": repository.get("health_score"),
                    "health_status": repository.get("health_status"),
                },
            )

        # 8. Build response sources.
        # Primero los repositorios que forman parte de la arquitectura propuesta.
        sources = []
        architecture_ids = [
            component["repository_id"] for component in valid_components
        ]
        ordered_repositories = sorted(
            ranked_repositories,
            key=lambda repo: repo.get("repository_id") not in architecture_ids,
        )

        for repository in ordered_repositories:
            repository_id = repository.get("repository_id")

            # Solo incluir repositorios con resultados semánticos.
            if repository_id not in similarities:
                continue

            original_repository = repositories_by_id.get(repository_id)

            if not original_repository:
                continue

            sources.append({
                "repository_id": repository_id,
                "name": original_repository.get("name", ""),
                "full_name": original_repository.get("full_name", ""),
                "url": original_repository.get("url", ""),
                "relevance_score": round(similarities[repository_id], 4),
            })

            if len(sources) >= 5:
                break

        return {
            "answer": answer,
            "sources": sources,
            "suggested_questions": architecture_data.get("suggested_questions", []),
            "architecture": {
                "components": architecture_data.get("components", []),
                "connections": architecture_data.get("connections", []),
            },
        }

    @staticmethod
    def _format_history(conversation_history: list[dict] | None) -> str:
        """Resume los últimos mensajes de la conversación para dar contexto al modelo."""
        if not conversation_history:
            return ""

        lines = []
        for item in conversation_history[-6:]:
            role = "Usuario" if item.get("role") == "user" else "Asistente"
            content = str(item.get("content", "")).strip()
            if content:
                lines.append(f"{role}: {content[:500]}")

        return "\n".join(lines)
