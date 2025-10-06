# QA Chatbot (API)

A minimal Retrieval-Augmented Generation (RAG) backend built with:

- FastAPI core backend
- LangChain for loaders, splitters, embeddings
- Milvus vector store via `langchain-milvus`
- OpenAI embeddings and chat completions

It supports:

- Ingesting one or more article URLs
- Splitting into chunks and storing with metadata (source, chunk_id)
- Retrieving relevant chunks and generating grounded answers
- CLI tools to run ingestion and QA services locally

## Project Layout

- `api/core`
  - `config.py` — environment-driven pydantic settings (OpenAI, Milvus, chunking)
  - `chat_client.py` — async/sync chat wrapper around LangChain’s OpenAI client
- `api/services`
  - `document_ingestion.py` — URL → clean → split → add_documents to Milvus
  - `qa_service.py` — retrieve top‑k chunks, build prompt, async LLM answer
  - `run_ingestion_pipeline.py` — helper to run ingestion programmatically
- `api/cli`
  - `ingestion_pipeline_cli.py` — run ingestion from the command line
  - `qa_service_cli.py` — run a QA query from the command line

## Prerequisites

- Python 3.12+
- Env vars:
  - `OPENAI_API_KEY`
- Milvus config (via `api/core/config.py`):
  - `milvus_uri` (URI string understood by `langchain-milvus`) - this is our database name
  - `milvus_collection` - a collection name to store embeddings
  - `milvus_vector_dim` (should match embedding model) - dimensions of your vectors

## Setup

Go to `2-qa-chatbot/api` folder and install dependencies with `uv sync` command

```shell
cd 2-qa-chatbot/api
uv sync
```

## Configuration

Rename `.env.example` file to `.env` in the `api` folder and add the following environment variables.

> Except for your own API key for OpenAI, all are set with default values.

- `OPENAI_API_KEY` - mandatory
- Embeddings model: `text-embedding-3-small` (default)
- Milvus: `milvus_uri`, `milvus_collection`, `milvus_vector_dim`
- Chunking: `chunk_size` (default 800), `chunk_overlap` (default 120)

## Ingestion: Load URLs into Milvus

You can run the ingestion pipeline as a CLI script.

```shell
cd 2-qa-chatbot/api

# Help output of the CLI
uv run python cli/ingestion_pipeline_cli.py -h

# Pass URLs
uv run python cli/ingestion_pipeline_cli.py --urls https://science.nasa.gov/exoplanets/what-is-the-universe/ https://science.nasa.gov/universe/stars/
```

What happens now:

- Fetch page content via `SeleniumURLLoader`
- Split text with `RecursiveCharacterTextSplitter`
- Store content as embeddings in Milvus with metadata: `source`, `chunk_id`

## QA: Ask a Question

From the `api` directory:

```shell
cd 2-qa-chatbot/api

# Help output of the CLI
uv run python cli/qa_service_cli.py -h
```

CLI options:

- `--top-k` — number of chunks to retrieve (default: 4)
- `--max-context` — limit context block size (default: 1800 chars)

Try the following sample questions to see in action:

- what is universe
- what happens when a star dies?

```shell
# Sample queries to try
uv run python cli/qa_service_cli.py --top-k 3 --max-context 500 "what is universe"
uv run python cli/qa_service_cli.py --top-k 3 --max-context 500 "what happens when a star dies?"
```

What happens:

- Retrieve `top‑k` chunks via `similarity_search_with_score`
- Format a context block
- Build a prompt and call the LLM asynchronously
- Print question, answer, context, and sources
