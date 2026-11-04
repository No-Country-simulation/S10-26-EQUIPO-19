import logging

from app.services.github_readme_service import GitHubReadmeService
from app.services.readme_processor import ReadmeProcessor
from app.services.text_chunker import TextChunker
from app.services.gemini_embedding_service import GeminiEmbeddingService
from app.services.embedding_storage_service import EmbeddingStorageService
from app.services.content_hash_service import ContentHashService
from app.repositories.readme_hash_repository import READMEHashRepository

logger = logging.getLogger(__name__)


class ReadmeSyncService:
    def __init__(
        self,
        github: GitHubReadmeService,
        gemini: GeminiEmbeddingService,
        storage: EmbeddingStorageService | None = None,
        hash_repository: READMEHashRepository | None = None,
    ):
        self.github = github
        self.gemini = gemini
        self.storage = storage or EmbeddingStorageService()
        self.hash_repository = (
            hash_repository or READMEHashRepository()
        )
        self.processor = ReadmeProcessor()
        self.chunker = TextChunker()

    async def sync_repository(
        self,
        repository_id: int,
        owner: str,
        repository: str,
    ) -> dict:
        # 1. Obtener README
        readme = await self.github.get_readme(owner, repository)

        if not readme:
            return {
                "status": "not_found",
                "repository_id": repository_id,
            }

        # 2. Calcular hash del contenido original
        new_hash = ContentHashService.generate(
            readme["content"]
        )

        # 3. Comparar con el hash almacenado
        current_hash = self.hash_repository.get_hash(
            repository_id
        )

        if not ContentHashService.has_changed(
            current_hash,
            new_hash,
        ):
            logger.info(
                "README unchanged for %s/%s",
                owner,
                repository,
            )

            return {
                "status": "unchanged",
                "repository_id": repository_id,
                "chunks_saved": 0,
            }

        # 4. Procesar README
        cleaned_content = self.processor.process(
            readme["content"]
        )

        chunks = self.chunker.chunk(cleaned_content)

        if not chunks:
            raise ValueError("README produced no chunks")

        # 5. Generar embeddings
        embeddings = []

        for chunk in chunks:
            embedding = await self.gemini.embed_text(
                chunk["content"],
                title=readme["name"],
            )
            embeddings.append(embedding)

        # 6. Reemplazar chunks y actualizar hash
        saved_count = self.storage.replace_repository_chunks(
            repository_id=repository_id,
            readme_hash=new_hash,
            chunks=chunks,
            embeddings=embeddings,
        )

        logger.info(
            "README synchronized for %s/%s: %s chunks",
            owner,
            repository,
            saved_count,
        )

        return {
            "status": "updated",
            "repository_id": repository_id,
            "chunks_saved": saved_count,
            "readme_hash": new_hash,
        }
