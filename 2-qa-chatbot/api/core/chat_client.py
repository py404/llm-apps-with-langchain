"""Wrappers around chat model clients used by the QA chatbot."""

from langchain_openai.chat_models import ChatOpenAI

from api.core.config import get_settings


class ChatClient:
    """Thin wrapper for the chat completion model configuration."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.0):
        settings = get_settings()
        self.client = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=model,
            temperature=temperature,
        )

    # TODO: expose methods as the conversational layer is implemented.
