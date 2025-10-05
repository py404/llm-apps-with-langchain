"""CLI for running QA queries against the vector store."""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Sequence

from loguru import logger

CURRENT_FILE = Path(__file__).resolve()
CLI_DIR = CURRENT_FILE.parent
API_ROOT = CLI_DIR.parent
PROJECT_ROOT = API_ROOT.parent
for candidate in (PROJECT_ROOT, API_ROOT):
    path_str = str(candidate)
    if path_str not in sys.path:
        sys.path.append(path_str)

from api.services.qa_service import QAService  # noqa: E402


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query the QA service with a natural language question.",
    )
    parser.add_argument("question", help="Question to ask the QA service")
    parser.add_argument(
        "--top-k",
        type=int,
        default=4,
        help="Number of chunks to retrieve from the vector store (default: 4)",
    )
    parser.add_argument(
        "--max-context",
        type=int,
        default=1800,
        help="Maximum number of characters to include in the context block.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])

    service = QAService(top_k=args.top_k, max_context_chars=args.max_context)
    result = asyncio.run(service.answer_question(args.question))

    logger.info("Question:\n{}", result["query"])  # noqa: T201
    logger.info("Answer:\n{}", result["answer"])  # noqa: T201
    logger.info("Context:\n{}", result["context"])  # noqa: T201

    sources = []
    seen = set()
    for src in result["sources"]:
        label = src or "unknown"
        if label in seen:
            continue
        seen.add(label)
        sources.append(label)

    sources_output = "\n".join(sources) if sources else "No sources returned."
    logger.info("Sources:\n{}", sources_output)  # noqa: T201


if __name__ == "__main__":  # pragma: no cover
    main()
