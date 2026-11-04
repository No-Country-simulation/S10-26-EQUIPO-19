from supabase import Client

from app.database import get_supabase_client
from app.services.gemini_embedding_service import GeminiEmbeddingService
from collections import Counter


class VectorSearchService:

    def __init__(
        self,
        gemini: GeminiEmbeddingService,
        supabase: Client | None = None,
    ):
        self.gemini = gemini
        self.supabase = supabase or get_supabase_client()

        if self.supabase is None:
            raise RuntimeError("Supabase client is not available")

    async def search(
        self,
        query: str,
        match_threshold: float = 0.5,
        match_count: int = 10,
        language: str | None = None,
        category_slug: str | None = None,
        license: str | None = None,
        technologies: list[str] | None = None,
        min_stars: int | None = None,
        min_health_score: float | None = None,
        exclude_archived: bool = True,
    ) -> list[dict]:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not 0 <= match_threshold <= 1:
            raise ValueError("match_threshold must be between 0 and 1")

        if match_count < 1 or match_count > 100:
            raise ValueError("match_count must be between 1 and 100")

        if min_stars is not None and min_stars < 0:
            raise ValueError("min_stars cannot be negative")

        if min_health_score is not None and min_health_score < 0:
            raise ValueError("min_health_score cannot be negative")

        query_embedding = await self.gemini.embed_text(query)

        candidate_count = min(match_count * 10, 1000)
        max_chunks_per_repository = 2

        response = self.supabase.rpc(
            "match_repository_embeddings_hybrid",
            {
                "query_embedding": query_embedding,
                "match_threshold": match_threshold,
                "match_count": candidate_count,
                "p_language": language,
                "p_category_slug": category_slug,
                "p_license": license,
                "p_technologies": technologies,
                "p_min_stars": min_stars,
                "p_min_health_score": min_health_score,
                "p_exclude_archived": exclude_archived,
            },
        ).execute()

        candidates = response.data or []

        results = []
        repository_counts = {}

        for candidate in candidates:
            repository_id = candidate["repository_id"]

            count = repository_counts.get(repository_id, 0)

            if count >= max_chunks_per_repository:
                continue

            results.append(candidate)
            repository_counts[repository_id] = count + 1

        results.sort(
            key=lambda result: result["similarity"],
            reverse=True,
        )

        return results[:match_count]
