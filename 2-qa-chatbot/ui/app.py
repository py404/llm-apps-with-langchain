import asyncio
import os

import streamlit as st
from client import ask_question, ingest_urls

st.set_page_config(page_title="QA Chatbot", layout="wide")


def _init_state() -> None:
    if "history" not in st.session_state:
        st.session_state["history"] = []


def _sidebar() -> None:
    st.sidebar.title("Settings")
    # Allow overriding API base for this UI session (does not persist env)
    api_base_default = os.getenv("QA_API_BASE", "http://localhost:8000")
    st.session_state.setdefault("api_base", api_base_default)
    api_base = st.sidebar.text_input(
        "API Base",
        value=st.session_state["api_base"],
        help="Backend URL for the QA API",
    )
    st.session_state["api_base"] = api_base.rstrip("/") or api_base_default
    st.sidebar.markdown("---")
    # History management
    if st.sidebar.button("Clear history"):
        st.session_state["history"] = []
        st.sidebar.success("History cleared")


def _render_ingest_tab() -> None:
    st.header("Ingest URLs")
    st.caption("Enter one or more URLs (one per line)")
    with st.form("ingest_form"):
        urls_text = st.text_area(
            "URLs",
            placeholder="https://example.com/article\nhttps://example.com/another",
        )
        submitted = st.form_submit_button("Ingest")
    if submitted:
        # Normalize and dedupe URLs
        raw_urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
        urls = []
        seen = set()
        for u in raw_urls:
            if not (u.startswith("http://") or u.startswith("https://")):
                continue
            if u in seen:
                continue
            seen.add(u)
            urls.append(u)
        if not urls:
            st.warning("Please provide at least one URL")
            return
        try:
            with st.spinner("Ingesting..."):
                data = asyncio.run(
                    ingest_urls(urls, base_url=st.session_state["api_base"])
                )
            st.success(f"Ingested {data.get('count', 0)} URL(s)")
            req_id = data.get("request_id")
            if req_id:
                st.caption(f"request_id: {req_id}")
            results = data.get("results") or []
            if results:
                st.subheader("Results")
                ok = 0
                for item in results:
                    status = item.get("status")
                    ok += int(status == "ok")
                    st.write(f"- {item.get('url')}: {status} — {item.get('message')}")
                st.caption(f"Summary: {ok}/{len(results)} succeeded")
        except Exception as ex:
            st.error(f"Ingestion failed: {ex}")


def _render_qa_tab() -> None:
    st.header("Ask a Question")
    with st.form("qa_form"):
        question = st.text_input(
            "Question",
            placeholder="Ask a relevant question about your ingested URL data",
        )
        col1, col2 = st.columns(2)
        with col1:
            top_k = st.number_input("Top K", value=4, min_value=1, max_value=20, step=1)
        with col2:
            max_context = st.number_input(
                "Max context (chars)", value=1800, min_value=200, step=100
            )
        submitted = st.form_submit_button("Ask")
    if submitted:
        if not question.strip():
            st.warning("Please enter a question")
            return
        try:
            with st.spinner("Thinking..."):
                data = asyncio.run(
                    ask_question(
                        question.strip(),
                        top_k=int(top_k),
                        max_context=int(max_context),
                        base_url=st.session_state["api_base"],
                    )
                )
            st.subheader("Answer")
            st.write(data.get("answer", ""))
            sources = data.get("sources") or []
            if sources:
                st.subheader("Sources")
                for s in sources:
                    st.write(f"- {s or 'unknown'}")
            ctx = data.get("context") or ""
            if ctx:
                with st.expander("Context"):
                    st.code(ctx)
            st.session_state["history"].append(
                {
                    "query": data.get("query"),
                    "answer": data.get("answer"),
                    "sources": sources,
                }
            )
        except Exception as ex:
            st.error(f"QA failed: {ex}")

    if st.session_state["history"]:
        st.markdown("---")
        st.subheader("History (this session)")
        for item in reversed(st.session_state["history"][-5:]):
            st.write(f"Q: {item.get('query')}")
            st.write(f"A: {item.get('answer')}")
            st.caption(", ".join([s or "unknown" for s in (item.get("sources") or [])]))


def main() -> None:
    _init_state()
    _sidebar()
    tabs = st.tabs(["Ingest", "QA"])
    with tabs[0]:
        _render_ingest_tab()
    with tabs[1]:
        _render_qa_tab()


if __name__ == "__main__":
    main()
