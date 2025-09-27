from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from loguru import logger
from openai import OpenAIError

from core.interfaces import SummarizerInterface
from core.models import StructuredSummary


class NewsArticleSummarizer(SummarizerInterface):
    """Summarizer class that returns both a human-readable summary and a structured Pydantic object."""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=StructuredSummary)
        format_instructions = self.parser.get_format_instructions()

        # Prompt instructing the model to output JSON following the parser format instructions
        self.prompt_template = PromptTemplate(
            input_variables=["text", "format_instructions"],
            template=(
                "You are an advanced AI assistant that summarizes online articles into a structured JSON format.\n\n"
                "Follow the output format instructions exactly:\n"
                "{format_instructions}\n\n"
                "Here's the article you need to summarize.\n\n"
                "==================\n"
                "{text}\n"
                "==================\n\n"
                "Provide only the structured JSON response that conforms to the instructions."
            ),
        )
        self.chain = self.prompt_template | self.llm

    async def summarize(self, article_title: str, article_text: str):
        """
        Summarize the article and return a tuple (human_readable_summary, structured_summary).
        The structured summary is an instance of StructuredSummary (Pydantic model).
        """
        if not self.llm:
            raise Exception("LLM client is not initialized.")

        combined_text = f"Title: {article_title}\n\n{article_text}"
        try:
            # Ensure we pass a mapping of variables to the chain
            result = await self.chain.ainvoke(
                {"text": combined_text, "format_instructions": self.parser.get_format_instructions()}
            )

            # LangChain may return a message-like object or raw string; normalize to text
            content = getattr(result, "content", result)

            # Parse the model output into the Pydantic model
            parsed: StructuredSummary = self.parser.parse(content)

            # Build a simple human-readable summary from the parsed bullets (fallback to tl_dr)
            if parsed.bullets and len(parsed.bullets) > 0:
                human_summary = "\n".join(f"- {b}" for b in parsed.bullets)
            elif parsed.tl_dr:
                human_summary = parsed.tl_dr
            else:
                # If parsing produced no useful fields, return the raw content as the human summary
                human_summary = str(content)

            return human_summary, parsed

        except OpenAIError as e:
            logger.error(f"OpenAI API error during summarization: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during summarization: {e}")
            raise e
