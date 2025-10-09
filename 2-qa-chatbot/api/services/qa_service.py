"""Retrieval-augmented QA service implementation backed by LangChain Milvus."""

from __future__ import annotations

from typing import Any

from langchain.prompts import PromptTemplate
from langchain_milvus import Milvus
from langchain_openai.embeddings import OpenAIEmbeddings
from loguru import logger

from api.core.chat_client import ChatClient
from api.core.config import get_settings


class QAService:
    """Coordinate retrieval, prompt construction, and answer generation."""

    def __init__(self, top_k: int = 4, max_context_chars: int = 1800):
        self.settings = get_settings()
        self.top_k = top_k
        self.max_context_chars = max_context_chars

        self.embeddings = OpenAIEmbeddings(
            api_key=self.settings.openai_api_key,
            model=self.settings.openai_embeddings_model,
        )
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            collection_name=self.settings.milvus_collection,
            connection_args={"uri": self.settings.milvus_uri},
        )
        self.chat_client = ChatClient(model="gpt-4o-mini")

    def _retrieve_chunks(self, query: str) -> list[dict[str, Any]]:
        """Query Milvus for similar document chunks and normalize the result set."""

        results = self.vector_store.similarity_search_with_score(query, k=self.top_k)

        if not results:
            logger.debug("No chunks retrieved for query")
            return []

        normalized: list[dict[str, Any]] = []
        seen_ids: set[Any] = set()
        for idx, (document, score) in enumerate(results):
            chunk_id = document.metadata.get("chunk_id", idx)
            if chunk_id in seen_ids:
                continue
            seen_ids.add(chunk_id)
            normalized.append(
                {
                    "id": chunk_id,
                    "score": score,
                    "text": document.page_content,
                    "source": document.metadata.get("source"),
                    "chunk_id": document.metadata.get("chunk_id"),
                }
            )

        return normalized

    def _format_context(self, chunks: list[dict[str, Any]]) -> str:
        """Prepare retrieved chunks for injection into the prompt."""

        if not chunks:
            return "No supporting context available."

        formatted: list[str] = []
        total_chars = 0

        for idx, chunk in enumerate(chunks, start=1):
            snippet = (chunk.get("text", "") or "").strip()
            if not snippet:
                logger.debug(f"Skipping chunk {chunk} due to missing text")
                continue

            source = chunk.get("source") or "unknown"
            score = chunk.get("score")
            chunk_id = chunk.get("chunk_id") or chunk.get("id") or idx

            score_display = f"{score:.3f}" if isinstance(score, (int, float)) else "n/a"
            entry_header = (
                f"[{idx}] Source: {source} | Chunk: {chunk_id} | Score: {score_display}"
            )

            if snippet.startswith("{") and snippet.endswith("}"):
                body = f"```json\n{snippet}\n```"
            else:
                body = snippet

            entry = f"{entry_header}\n{body}"

            total_chars += len(entry)
            if total_chars > self.max_context_chars:
                logger.debug(
                    f"Context truncated after chunk {idx} to respect limit"
                )
                break

            formatted.append(entry)

        if not formatted:
            return "No supporting context available."

        return "\n---\n".join(formatted)

    def _build_prompt(self, context_block: str, query: str) -> str:
        """Assemble a prompt template that grounds the LLM in retrieved context."""

        prompt_template = """
        You are an exceptional customer support chatbot that answers questions gently.

        Use the following context to ground your response:

        {context_block}

        Question: {query}

        Provide a concise answer. If the context does not contain the answer, say so.
        """
        prompt = PromptTemplate(
            input_variables=["context_block", "query"],
            template=prompt_template.strip(),
        )
        return prompt.format(context_block=context_block, query=query)

    async def answer_question(self, query: str) -> dict[str, Any]:
        """Retrieve context, call the LLM asynchronously, and format an answer."""

        retrieved_chunks = self._retrieve_chunks(query)
        context_block = self._format_context(retrieved_chunks)
        prompt = self._build_prompt(context_block, query)

        try:
            llm_response = await self.chat_client.ainvoke(prompt)
            answer_text = getattr(llm_response, "content", str(llm_response))
        except Exception as exc:  # noqa: BLE001
            logger.exception(f"LLM invocation failed: {exc}")
            answer_text = "I’m sorry, I couldn’t generate an answer right now."

        sources = list(dict.fromkeys(chunk.get("source") for chunk in retrieved_chunks))

        return {
            "query": query,
            "answer": answer_text,
            "context": context_block,
            "sources": sources,
        }
