from fastapi import FastAPI

app = FastAPI(
    title="News Summarizer API",
    description="An API to summarize news articles using LangChain and LLMs.",
    version="0.1.0",
    docs_url="/docs",
)


@app.get("/")
def index():
    return {"message": "Hello, FastAPI!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
