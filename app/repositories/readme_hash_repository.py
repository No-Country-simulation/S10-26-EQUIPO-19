from supabase import Client

from app.database import get_supabase_client


class READMEHashRepository:

    def __init__(self, supabase: Client | None = None):
        self.supabase = supabase or get_supabase_client()

        if self.supabase is None:
            raise RuntimeError("Supabase client is not available")

    def get_hash(self, repository_id: int) -> str | None:
        response = (
            self.supabase
            .table("repositories")
            .select("readme_hash")
            .eq("id", repository_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            raise ValueError(
                f"Repository {repository_id} not found"
            )

        return response.data[0]["readme_hash"]

    def update_hash(
        self,
        repository_id: int,
        content_hash: str,
    ) -> None:
        response = (
            self.supabase
            .table("repositories")
            .update({"readme_hash": content_hash})
            .eq("id", repository_id)
            .execute()
        )

        if not response.data:
            raise ValueError(
                f"Could not update README hash for repository {repository_id}"
            )
