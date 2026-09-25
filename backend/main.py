from fastapi import FastAPI

app = FastAPI(
    title="ReviewLens AI",
    description="Azure-Powered Feedback & Review Analyzer",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "project": "ReviewLens AI",
        "status": "running",
        "message": "ReviewLens AI backend is ready."
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }