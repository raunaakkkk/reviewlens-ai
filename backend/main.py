from fastapi import FastAPI, UploadFile, File, HTTPException

from backend.storage import upload_bytes


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


@app.post("/reviews/upload")
async def upload_review(file: UploadFile = File(...)):
    """
    Upload a review file to Azure Blob Storage.

    Files are stored under:
        reviews/raw/
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    try:
        file_data = await file.read()

        blob_name = f"raw/{file.filename}"

        blob_url = upload_bytes(
            data=file_data,
            blob_name=blob_name
        )

        return {
            "status": "uploaded",
            "filename": file.filename,
            "blob_name": blob_name,
            "blob_url": blob_url
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(exc)}"
        )