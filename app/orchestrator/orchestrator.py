import logging
import os

from dotenv import load_dotenv

from app.orchestrator.requirements_analyzer import RequirementsAnalyzer
from app.orchestrator.compatibility_engine import CompatibilityEngine
from app.orchestrator.context_builder import ContextBuilder

from app.services.gemini_embedding_service import GeminiEmbeddingService
from app.services.llm_service import LLMService
from app.services.sql_search_service import SQLSearchService
from app.services.vector_search_service import VectorSearchService

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



    async def process_message(self, message: str) -> dict:

        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        logger.info("Processing assistant query: %s", message)

        # 1. Analyze user requirements.
        requirements = self.requirements_analyzer.analyze(message)

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
                "query": message,
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

        if missing_ids:
            logger.warning(
                "Semantic results contain repositories not found in SQL results: %s",
                missing_ids,
            )

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
        )

        # 7. Generate final answer.
        answer = await self.llm.generate_response(context)

        # 8. Build response sources.
        sources = []

        for repository in ranked_repositories:
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
            "suggested_questions": [],
            "architecture": None,
        }
