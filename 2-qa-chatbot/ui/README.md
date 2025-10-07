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
