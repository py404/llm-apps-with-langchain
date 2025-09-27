import asyncio

import httpx
import streamlit as st

API_URL = "http://localhost:8000/summarize"


async def summarize_article_async(url: str):
    """Asynchronous function to call the summarization API."""
    payload = {"url": url}
    try:
        # Use the async httpx client to perform the request
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.HTTPError as e:
        st.error(f"HTTP error occurred: {e}")
    except httpx.TimeoutException:
        st.error("The request timed out. Please try again.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    return None


def main():
    st.title("News Articles Summarizer")
    st.write("Enter a news article URL to get a concise summary.")

    url = st.text_input("Article URL")

    if st.button("Summarize"):
        if not url:
            st.warning("Please enter a valid URL.")
            return

        with st.spinner("Summarizing..."):
            # Use asyncio.run() to execute the async function within the sync context
            result = asyncio.run(summarize_article_async(url))

            if result and "summary" in result:
                # st.subheader("Summary")
                st.write(result["summary"])

                # Display structured keywords as tags if available
                structured = result.get("structured_summary") or {}
                keywords = None

                # structured may be a dict (from API) or a JSON-string in some setups; we handle dicts here
                if isinstance(structured, dict):
                    keywords = structured.get("keywords")
                    tl_dr = structured.get("tl_dr")
                else:
                    # fallback: try top-level fields
                    keywords = result.get("keywords")
                    tl_dr = result.get("tl_dr")

                # show TL;DR if present
                if tl_dr:
                    st.markdown("**TL;DR:**")
                    st.write(tl_dr)

                if keywords:
                    # ensure keywords is a list
                    if isinstance(keywords, str):
                        # comma separated fallback
                        keywords_list = [k.strip() for k in keywords.split(",") if k.strip()]
                    else:
                        keywords_list = list(keywords)

                    # Build simple badge-like HTML for keywords
                    tags_html = " ".join(
                        f'<span style="display:inline-block;background:#EEF2FF;color:#0b53ff;border-radius:999px;padding:4px 8px;margin:3px;font-size:0.9em">{kw}</span>'
                        for kw in keywords_list
                    )
                    st.markdown("<div style='margin-top:6px'>" + tags_html + "</div>", unsafe_allow_html=True)
            else:
                st.error("Failed to get summary.")


if __name__ == "__main__":
    main()
