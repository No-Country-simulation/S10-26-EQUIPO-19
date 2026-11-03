import logging

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiEmbeddingService:

    MODEL = "gemini-embedding-2"
    DIMENSIONS = 768

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")

        self.client = genai.Client(api_key=api_key)

    async def embed_text(
        self,
        text: str,
        title: str | None = None,
    ) -> list[float]:

        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if title:
            content = f"title: {title} | text: {text}"
        else:
            content = text

        response = await self.client.aio.models.embed_content(
            model=self.MODEL,
            contents=content,
            config=types.EmbedContentConfig(
                output_dimensionality=self.DIMENSIONS,
            ),
        )

        if not response.embeddings:
            raise RuntimeError("Gemini returned no embeddings")

        embedding = response.embeddings[0].values

        if len(embedding) != self.DIMENSIONS:
            raise RuntimeError(
                f"Expected {self.DIMENSIONS} dimensions, "
                f"received {len(embedding)}"
            )

        logger.info(
            "Embedding generated successfully: %s dimensions",
            len(embedding),
        )

        return embedding
