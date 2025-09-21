from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from core.interfaces import SummarizerInterface


class NewsArticleSummarizer(SummarizerInterface):
    """Summarizer class to generate concise summaries of news articles."""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            input_variables=["text"],
            template=(
                "You are an advanced AI assistant that summarizes online articles into bulleted lists.\n\n"
                "Here's the article you need to summarize.\n\n"
                "==================\n"
                "{text}\n"
                "==================\n\n"
                "Now, provide a summarized version of the article in a bulleted list format."
            ),
        )
        self.chain = self.prompt_template | self.llm

    async def summarize(self, article_title: str, article_text: str) -> str:
        if not self.llm:
            raise Exception("LLM client is not initialized.")

        combined_text = f"Title: {article_title}\n\n{article_text}"

        summary = await self.chain.ainvoke(combined_text)
        return summary.content
