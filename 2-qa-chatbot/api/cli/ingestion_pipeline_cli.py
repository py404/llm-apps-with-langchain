"""Command-line helpers for the QA chatbot project."""

import argparse
import sys
from pathlib import Path
from typing import Sequence

# Ensure the project root is on sys.path when executed as a script
CURRENT_FILE = Path(__file__).resolve()
CLI_DIR = CURRENT_FILE.parent
API_ROOT = CLI_DIR.parent
PROJECT_ROOT = API_ROOT.parent
for path_candidate in (PROJECT_ROOT, API_ROOT):
    path_str = str(path_candidate)
    if path_str not in sys.path:
        sys.path.append(path_str)

from api.services.run_ingestion_pipeline import run_ingestion_pipeline  # noqa: E402


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the document ingestion pipeline for one or more URLs.",
    )
    parser.add_argument(
        "-a",
        "--urls",
        nargs="+",
        help="One or more article URLs to ingest.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    run_ingestion_pipeline(args.urls)


if __name__ == "__main__":
    main()
