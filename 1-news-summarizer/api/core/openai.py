import openai
from loguru import logger
from openai import AsyncOpenAI


class AOAIClient:
    """Asynchronous OpenAI Client using the official OpenAI Python SDK."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client: AsyncOpenAI = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def response(self, prompt: str) -> str:
        try:
            response = await self.client.responses.create(
                model=self.model,
                input=prompt,
            )
            return response.output_text
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI API connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise
