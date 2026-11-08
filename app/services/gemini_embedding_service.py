import asyncio
import logging
import re
from collections import OrderedDict

from google import genai
from google.genai import errors, types

logger = logging.getLogger(__name__)


class GeminiEmbeddingService:

    MODEL = "gemini-embedding-2"
    DIMENSIONS = 768
    # Caché en memoria para consultas repetidas (seguimientos, reintentos).
    CACHE_MAX_ENTRIES = 128
    CACHE_MAX_CHARS = 2000

    def __init__(
        self,
        api_key: str,
        max_retries: int = 3,
        request_delay: float = 2.0,
    ):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")

        self.client = genai.Client(api_key=api_key)
        self.max_retries = max_retries
        self.request_delay = request_delay
        self._cache: OrderedDict[str, list[float]] = OrderedDict()

    def _get_cached(self, key: str) -> list[float] | None:
        if len(key) > self.CACHE_MAX_CHARS:
            return None

        cached = self._cache.get(key)

        if cached is None:
            return None

        self._cache.move_to_end(key)
        return cached

    def _store_cached(self, key: str, embedding: list[float]) -> None:
        if len(key) > self.CACHE_MAX_CHARS:
            return

        self._cache[key] = embedding
        self._cache.move_to_end(key)

        while len(self._cache) > self.CACHE_MAX_ENTRIES:
            self._cache.popitem(last=False)

    @staticmethod
    def _get_retry_delay(exc: errors.APIError, attempt: int) -> float:
        details = getattr(exc, "details", {}) or {}

        error_details = details.get("error", {}).get("details", [])

        for detail in error_details:
            if detail.get("@type", "").endswith("google.rpc.RetryInfo"):
                retry_delay = detail.get("retryDelay", "")

                match = re.fullmatch(r"(\d+(?:\.\d+)?)s", retry_delay)

                if match:
                    return float(match.group(1))

        return min(2 ** attempt, 60)

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

        cached = self._get_cached(content)

        if cached is not None:
            logger.info("Embedding served from cache")
            return cached

        for attempt in range(self.max_retries + 1):
            try:
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

                self._store_cached(content, embedding)

                if self.request_delay > 0:
                    await asyncio.sleep(self.request_delay)

                return embedding

            except errors.APIError as exc:
                if exc.code not in (429, 503):
                    raise

                if attempt >= self.max_retries:
                    logger.error(
                        "Gemini API retries exhausted after %s attempts: %s",
                        attempt + 1,
                        exc,
                    )
                    raise

                delay = self._get_retry_delay(exc, attempt)

                logger.warning(
                    "Gemini API returned %s. Retry %s/%s in %.2f seconds",
                    exc.code,
                    attempt + 1,
                    self.max_retries,
                    delay,
                )

                await asyncio.sleep(delay)

        raise RuntimeError("Unexpected embedding generation failure")
