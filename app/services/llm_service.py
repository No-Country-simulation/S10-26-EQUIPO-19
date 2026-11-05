import logging

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class LLMService:

    DEFAULT_MODEL = "gemini-3.6-flash"

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

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=context,
                config=config,
            )

            content = response.text

            if not content:
                raise RuntimeError("Gemini returned an empty response")

            logger.info(
                "Response generated successfully using Gemini model %s",
                self.model,
            )

            return content.strip()

        except Exception:
            logger.exception(
                "Gemini generation failed | model=%s",
                self.model,
            )
            raise

    async def generate_response(self, context: str) -> str:
        return await self._generate(context)

    async def generate_json_response(self, context: str) -> str:
        return await self._generate(context, json_mode=True)
