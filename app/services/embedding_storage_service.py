import hashlib
import logging

from supabase import Client

from app.database import get_supabase_client

logger = logging.getLogger(__name__)


class EmbeddingStorageService:
    def __init__(self, supabase: Client | None = None):
        self.supabase = supabase or get_supabase_client()

        if self.supabase is None:
            raise RuntimeError("Supabase client is not available")

    @staticmethod
    def _generate_content_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _build_records(
        self,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> list[dict]:
        if len(chunks) != len(embeddings):
            raise ValueError(
                "The number of chunks and embeddings must match"
            )

        records = []

        for chunk, embedding in zip(chunks, embeddings):
            if len(embedding) != 768:
                raise ValueError(
                    f"Expected 768 dimensions, received {len(embedding)}"
                )

            content = chunk["content"]

            records.append({
                "source_text": content,
                "embedding": embedding,
                "chunk_index": chunk["chunk_index"],
                "content_hash": self._generate_content_hash(content),
                "metadata": {
                    "section": chunk.get("section"),
                    "section_path": chunk.get("section_path"),
                    "token_count": chunk.get("token_count"),
                },
            })

        return records

    def save_repository_chunks(
        self,
        repository_id: int,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> int:
        if not chunks:
            return 0

        records = self._build_records(chunks, embeddings)

        response = (
            self.supabase
            .table("embeddings")
            .upsert(
                [
                    {
                        **record,
                        "repository_id": repository_id,
                        "integration_id": None,
                        "content_type": "readme_chunk",
                    }
                    for record in records
                ],
                on_conflict="repository_id,content_type,chunk_index",
            )
            .execute()
        )

        saved_count = len(response.data or [])

        logger.info(
            "Saved %s README chunks for repository %s",
            saved_count,
            repository_id,
        )

        return saved_count

    def replace_repository_chunks(
        self,
        repository_id: int,
        readme_hash: str,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> int:
        if not chunks:
            raise ValueError("Cannot replace README with empty chunks")

        records = self._build_records(chunks, embeddings)

        response = self.supabase.rpc(
            "replace_repository_readme_chunks",
            {
                "p_repository_id": repository_id,
                "p_readme_hash": readme_hash,
                "p_chunks": records,
            },
        ).execute()

        saved_count = response.data

        logger.info(
            "Replaced %s README chunks for repository %s",
            saved_count,
            repository_id,
        )

        return saved_count
