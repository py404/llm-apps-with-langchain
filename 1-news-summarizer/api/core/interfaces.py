from abc import ABC, abstractmethod
from typing import List

from langchain.schema import Document


class SummarizerInterface(ABC):
    @abstractmethod
    async def summarize(self, docs: List[Document]) -> str:
        """
        Generate a concise summary from a list of Document objects.

        Args:
            docs (List[Document]): List of LangChain Document objects to summarize.

        Returns:
            str: The summarized text.
        """
        pass
