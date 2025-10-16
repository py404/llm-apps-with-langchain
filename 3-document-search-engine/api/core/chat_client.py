"""Wrappers around chat model clients used by the document search engine."""

from langchain_openai.chat_models import ChatOpenAI

from api.core.config import get_settings


class ChatClient:
    """Thin wrapper around `ChatOpenAI` exposing sync/async helpers."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.0):
        settings = get_settings()
        self._client = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=model,
            temperature=temperature,
        )

    def invoke(self, prompt: str, **kwargs):
        """Synchronously invoke the chat model."""

        return self._client.invoke(prompt, **kwargs)

    async def ainvoke(self, prompt: str, **kwargs):
        """Asynchronously invoke the chat model and return the response."""

        return await self._client.ainvoke(prompt, **kwargs)

    def stream(self, prompt: str, **kwargs):
        """Stream responses from the chat model (generator)."""

        return self._client.stream(prompt, **kwargs)
