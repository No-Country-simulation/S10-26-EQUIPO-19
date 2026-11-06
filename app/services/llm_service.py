import logging
import asyncio
import random

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class LLMService:

    DEFAULT_MODEL = "gemini-3.1-flash-lite"
    FALLBACK_MODEL = "gemini-3.5-flash-lite"
    MAX_RETRIES = 3
    RETRY_DELAY = 1.5

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.3,
        max_output_tokens: int = 8192,
    ):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")

        if not model:
            raise ValueError("Model cannot be empty")

        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")

        if max_output_tokens < 1:
            raise ValueError("max_output_tokens must be positive")

        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    async def _generate(
        self,
        context: str,
        json_mode: bool = False,
    ) -> str:

        if not context or not context.strip():
            raise ValueError("Context cannot be empty")

        config = types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            response_mime_type="application/json" if json_mode else "text/plain",
        )

        models = [self.model, self.FALLBACK_MODEL]

        for model_index, model in enumerate(models):
            for attempt in range(self.MAX_RETRIES + 1):
                try:
                    response = await self.client.aio.models.generate_content(
                        model=model,
                        contents=context,
                        config=config,
                    )

                    content = response.text

                    if not content:
                        raise RuntimeError("Gemini returned an empty response")

                    logger.info(
                        "Response generated successfully using Gemini model %s",
                        model,
                    )

                    return content.strip()

                except Exception as exc:
                    error_message = str(exc).upper()

                    retryable = any(
                        indicator in error_message
                        for indicator in (
                            "503",
                            "429",
                            "UNAVAILABLE",
                            "RESOURCE_EXHAUSTED",
                        )
                    )

                    if not retryable:
                        logger.exception(
                            "Gemini generation failed | model=%s",
                            model,
                        )
                        raise

                    if attempt == self.MAX_RETRIES:
                        if model_index == len(models) - 1:
                            logger.exception(
                                "All Gemini models exhausted | model=%s",
                                model,
                            )
                            raise

                        logger.warning(
                            "Model %s exhausted retries. Switching to fallback: %s",
                            model,
                            self.FALLBACK_MODEL,
                        )
                        break

                    delay = self.RETRY_DELAY + random.uniform(0, 0.5)

                    logger.warning(
                        "Gemini temporarily unavailable | model=%s | "
                        "retry in %.2f seconds | attempt %s/%s",
                        model,
                        delay,
                        attempt + 1,
                        self.MAX_RETRIES,
                    )

                    await asyncio.sleep(delay)

    async def generate_response(self, context: str) -> str:
        return await self._generate(context)

    async def generate_json_response(self, context: str) -> str:
        return await self._generate(context, json_mode=True)
