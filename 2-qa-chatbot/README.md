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
  - `milvus_uri` (URI string understood by `langchain-milvus`). Examples:
    - Milvus server: `http://localhost:19530`
    - Milvus Lite file (if supported): `file:///absolute/path/to/milvus.db`
  - `milvus_collection` — collection name to store embeddings
  - `milvus_vector_dim` — dimensions (match embedding model)

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
- Format a context block (deduped, score shown, JSON fenced where applicable)
- Build a prompt and call the LLM asynchronously
- Print question, answer, context, and sources

## Troubleshooting

- Invalid Milvus URI
  - Ensure `milvus_uri` is a valid HTTP(S) server URL or a supported `file:///` path for Lite.
- Empty or generic answers
  - Re‑run ingestion for the target URL; ask more context‑anchored questions; adjust `--top-k` / `--max-context`.
- Selenium loader issues
  - Ensure a compatible browser/driver is installed or increase waits for dynamic content.

# QA Chatbot – Streamlit UI

A minimal Streamlit interface to drive the QA Chatbot API.

- Ingest: submit one or more URLs to the backend.
- QA: ask a question against the ingested corpus and view answer, context, and sources.

## Prerequisites

- Python 3.12+
- A running API (default at `http://localhost:8000`). See `README.md` in `api` folder for API setup.
- Environment (optional):
  - `QA_API_BASE` (defaults to `http://localhost:8000`)

## Install

```bash
cd 2-qa-chatbot/ui
uv sync
```

## Run

```bash
# Optionally point the UI to a different API base
export QA_API_BASE=http://localhost:8000

# Start Streamlit
uv run streamlit run app.py
```

## Usage

- Ingest tab
  - Paste one URL per line and click Ingest
  - Shows per‑URL status and a short summary
- QA tab
  - Enter a question, set `Top K` and `Max context`, click `Ask`
  - Shows the answer, deduped sources, and a collapsible context block

The sidebar displays/overrides the API base and lets you clear the in‑session history.

## Notes

- The UI uses `httpx` library with short‑lived async clients to avoid event‑loop issues in Streamlit reruns.
- API errors are surfaced inline; verify the API is reachable and that you’ve ingested URLs first.

## API Examples (curl)

POST /ingest
```
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com/a", "https://example.com/b"]}' \
  http://localhost:8000/ingest
```

POST /qa
```
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the article say about logging?", "top_k": 4, "max_context": 1800}' \
  http://localhost:8000/qa
```

## .env Example (API)

Place a `.env` in `2-qa-chatbot/api` (pydantic-settings will pick it up):
```
OPENAI_API_KEY=sk-...

# Milvus Lite (default for this project)
milvus_uri=file:///absolute/path/to/milvus.db
milvus_collection=qa_chunks
milvus_vector_dim=1536

# Chunking
chunk_size=800
chunk_overlap=120
```

Notes:
- This project defaults to Milvus Lite with a file URI. If you run a Milvus server, use an HTTP(S) URI like `http://localhost:19530` instead.
- Ensure the embedding dimension matches your embeddings model output.
