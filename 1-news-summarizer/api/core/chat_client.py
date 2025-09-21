from fastapi import Depends
from langchain_openai import ChatOpenAI


class ChatClient:
    """Wrapper class for LangChain's ChatOpenAI client."""

    def __init__(
        self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0
    ):
        self.client = ChatOpenAI(api_key=api_key, model=model, temperature=temperature)
