from supabase import Client

from app.database import get_supabase_client


class SQLSearchService:

    def __init__(self, supabase: Client | None = None):
        self.supabase = supabase or get_supabase_client()

        if self.supabase is None:
            raise RuntimeError("Supabase client is not available")

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

        query = self.supabase.table("repositories").select("*")

        # Category filter: resolve slug to category ID.
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

        # Metadata filters.
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

        # Ordering and pagination.
        response = (
            query
            .order("health_score", desc=True)
            .order("stars", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return response.data or []
