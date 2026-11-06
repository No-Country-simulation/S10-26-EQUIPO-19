from supabase import Client

from app.database import get_supabase_client


class SQLSearchService:

    def __init__(self, supabase: Client | None = None):
        self.supabase = supabase or get_supabase_client()

        if self.supabase is None:
            raise RuntimeError("Supabase client is not available")

    @staticmethod
    def _attach_health_status(repositories: list[dict]) -> list[dict]:
        for repository in repositories:
            metrics = repository.get("metrics") or {}

            if isinstance(metrics, list):
                metrics = metrics[0] if metrics else {}

            repository["health_status"] = metrics.get("health_status")

        return repositories

    def get_repositories_by_ids(
        self,
        repository_ids: list[int],
    ) -> list[dict]:

        if not repository_ids:
            return []

        response = (
            self.supabase
            .table("repositories")
            .select("*, metrics(health_status)")
            .in_("id", repository_ids)
            .execute()
        )

        return self._attach_health_status(response.data or [])

    def search_repositories(
        self,
        category_slug: str | None = None,
        language: str | None = None,
        license: str | None = None,
        technologies: list[str] | None = None,
        min_stars: int | None = None,
        min_health_score: float | None = None,
        exclude_archived: bool = True,
        limit: int = 10,
        offset: int = 0,
    ) -> list[dict]:

        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        query = (
            self.supabase
            .table("repositories")
            .select("*, metrics(health_status)")
        )

        if category_slug:
            category_response = (
                self.supabase
                .table("categories")
                .select("id")
                .eq("slug", category_slug)
                .limit(1)
                .execute()
            )

            if not category_response.data:
                return []

            category_id = category_response.data[0]["id"]
            query = query.eq("category_id", category_id)

        if language:
            query = query.eq("language", language)

        if license:
            query = query.eq("license", license)

        if technologies:
            query = query.contains("detected_stack", technologies)

        if min_stars is not None:
            query = query.gte("stars", min_stars)

        if min_health_score is not None:
            query = query.gte("health_score", min_health_score)

        if exclude_archived:
            query = query.eq("archived", False)

        response = (
            query
            .order("health_score", desc=True)
            .order("stars", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return self._attach_health_status(response.data or [])
