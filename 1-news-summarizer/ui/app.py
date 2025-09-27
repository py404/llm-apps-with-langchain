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
            else:
                st.error("Failed to get summary.")


if __name__ == "__main__":
    main()
