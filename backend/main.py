import os

from dotenv import load_dotenv

load_dotenv()

from azure.monitor.opentelemetry import configure_azure_monitor

application_insights_connection_string = os.getenv(
    "APPLICATIONINSIGHTS_CONNECTION_STRING"
)

if application_insights_connection_string:
    configure_azure_monitor(
        connection_string=application_insights_connection_string
    )

from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
import threading
import tempfile
import os
from backend.analysis.drift import calculate_drift
from backend.storage import upload_bytes
from backend.database import SessionLocal
from backend.models import (
    Review,
    Insight,
    EvidenceLink,
    ValidationResult,
)
from backend.agent.rag_agent import answer_question
from backend.ingestion.batch import ingest_csv
from backend.database_sync import sync_search_to_database
from backend.insight_sync import sync_insights
from backend.dataset_reset import reset_dataset

# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="ReviewLens AI",
    description="Azure-Powered Feedback & Review Analyzer",
    version="0.7.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://reviewlens-web-260925.azurewebsites.net",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# BACKGROUND INSIGHT GENERATION
# =========================================================

def generate_background_insights():
    """
    Run Qwen3 insight generation in an independent thread.

    The upload request does not wait for Qwen3 to finish.
    """
    analysis_status["status"] = "processing"
    analysis_status["message"] = "Generating fresh AI insights."
    print("\n========================================")
    print("BACKGROUND INSIGHT GENERATION STARTED")
    print("========================================")

    try:

        result = sync_insights()
        analysis_status["status"] = "completed"
        analysis_status["message"] = "Fresh AI insights generated successfully."
        print("\n========================================")
        print("BACKGROUND INSIGHT GENERATION COMPLETE")
        print("========================================")

        print(
            "Status         :",
            result.get("status"),
        )

        print(
            "Created        :",
            result.get("created"),
        )

        print(
            "Skipped        :",
            result.get("skipped"),
        )

        print(
            "Evidence links :",
            result.get("evidence_links"),
        )

    except Exception as exc:
        analysis_status["status"] = "failed"
        analysis_status["message"] = str(exc)
        print("\n========================================")
        print("BACKGROUND INSIGHT GENERATION FAILED")
        print("========================================")

        print(
            "Error:",
            repr(exc),
        )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "project": "ReviewLens AI",
        "status": "running",
        "message": "ReviewLens AI backend is ready.",
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
    }


# =========================================================
# UPLOAD REVIEWS
# =========================================================

@app.post("/reviews/upload")
async def upload_review(
    file: UploadFile = File(...),
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if not file.filename.lower().endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    temp_path = None

    try:

        # -------------------------------------------------
        # Read uploaded file
        # -------------------------------------------------

        file_data = await file.read()

        if not file_data:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        # -------------------------------------------------
        # Upload raw CSV to Azure Blob Storage
        # -------------------------------------------------

        blob_name = f"raw/{file.filename}"

        blob_url = upload_bytes(
            data=file_data,
            blob_name=blob_name,
        )

        # -------------------------------------------------
        # Create temporary local CSV
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv",
        ) as temp_file:

            temp_file.write(file_data)
            temp_path = temp_file.name

        # -------------------------------------------------
        # REPLACE PREVIOUS DATASET
        #
        # The uploaded CSV becomes the new active dataset.
        # Previous Search + PostgreSQL review data is removed.
        # -------------------------------------------------

        reset_result = reset_dataset()

        # -------------------------------------------------
        # Process new CSV
        #
        # Cleaning
        # PII Redaction
        # Sentiment
        # Embeddings
        # Azure AI Search
        # -------------------------------------------------

        ingestion_result = ingest_csv(
            temp_path,
        )

        # -------------------------------------------------
        # Synchronize Azure AI Search → PostgreSQL
        # -------------------------------------------------

        database_result = sync_search_to_database()

        # -------------------------------------------------
        # Calculate drift for the NEW active dataset
        # -------------------------------------------------

        drift_result = calculate_drift()

        # -------------------------------------------------
        # Start Qwen3 insight generation
        #
        # Runs independently from HTTP request.
        # -------------------------------------------------

        insight_thread = threading.Thread(
            target=generate_background_insights,
            daemon=True,
        )

        insight_thread.start()

        # -------------------------------------------------
        # Return immediately
        # -------------------------------------------------

        return {
            "status": "processed",
            "filename": file.filename,
            "blob_name": blob_name,
            "blob_url": blob_url,
            "reset": reset_result,
            "ingestion": ingestion_result,

            "database": database_result,
            "drift": drift_result,

            "insights": {
                "status": "queued",
                "message": (
                    "Insight generation has "
                    "started in the background."
                ),
            },
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Upload processing failed: {str(exc)}"
            ),
        )

    finally:

        # -------------------------------------------------
        # Remove temporary CSV
        # -------------------------------------------------

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)

            except OSError:
                pass
# =========================================================
# ANALYSIS STATUS
# =========================================================

analysis_status = {
    "status": "idle",
    "message": "No analysis is currently running.",
}


@app.get("/analysis/status")
def get_analysis_status():

    return analysis_status

# =========================================================
# GET REVIEWS
# =========================================================

@app.get("/reviews")
def get_reviews():

    db = SessionLocal()

    try:

        reviews = db.execute(
            select(Review).order_by(
                Review.created_at.desc()
            )
        ).scalars().all()

        return {
            "count": len(reviews),

            "reviews": [
                {
                    "id": review.id,
                    "review_hash": review.review_hash,
                    "review_text": review.review_text,
                    "redacted_text": review.redacted_text,
                    "sentiment": review.sentiment,
                    "positive_score": review.positive_score,
                    "neutral_score": review.neutral_score,
                    "negative_score": review.negative_score,
                    "created_at": (
                        review.created_at.isoformat()
                    ),
                }
                for review in reviews
            ],
        }

    finally:

        db.close()


# =========================================================
# GET DASHBOARD REVIEWS
# =========================================================

@app.get("/dashboard/reviews")
def get_dashboard_reviews():

    db = SessionLocal()

    try:

        reviews = db.execute(
            select(
                Review.id,
                Review.review_text,
                Review.redacted_text,
                Review.sentiment,
                Review.created_at,
            ).order_by(
                Review.created_at.desc()
            )
        ).all()

        return {
            "count": len(reviews),

            "reviews": [
                {
                    "id": review.id,
                    "review_text": review.review_text,
                    "redacted_text": review.redacted_text,
                    "sentiment": review.sentiment,
                    "created_at": (
                        review.created_at.isoformat()
                    ),
                }
                for review in reviews
            ],
        }

    finally:

        db.close()


# =========================================================
# GET INSIGHTS
# =========================================================

@app.get("/insights")
def get_insights():

    db = SessionLocal()

    try:

        insights = db.execute(
            select(Insight).order_by(
                Insight.id
            )
        ).scalars().all()

        return {
            "count": len(insights),

            "insights": [
                {
                    "id": insight.id,
                    "type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "created_at": (
                        insight.created_at.isoformat()
                    ),
                }
                for insight in insights
            ],
        }

    finally:

        db.close()


# =========================================================
# GET EVIDENCE
# =========================================================

@app.get("/evidence")
def get_evidence():

    db = SessionLocal()

    try:

        links = db.execute(
            select(EvidenceLink).order_by(
                EvidenceLink.id
            )
        ).scalars().all()

        return {
            "count": len(links),

            "evidence": [
                {
                    "id": link.id,
                    "insight_id": link.insight_id,
                    "review_id": link.review_id,
                    "reason": link.reason,
                    "search_score": link.search_score,
                }
                for link in links
            ],
        }

    finally:

        db.close()


# =========================================================
# GET SENTIMENT VALIDATION
# =========================================================

@app.get("/validation")
def get_validation():

    db = SessionLocal()

    try:

        validation = (
            db.query(ValidationResult)
            .order_by(
                ValidationResult.created_at.desc()
            )
            .first()
        )

        if not validation:

            return {
                "status": "no_data",
                "validation": None,
            }

        return {
            "status": "success",

            "validation": {
                "type": "labelled_benchmark",
                "id": validation.id,
                "sample_size": (
                    validation.sample_size
                ),

                "accuracy": (
                    validation.accuracy
                ),

                "precision": (
                    validation.precision
                ),

                "recall": (
                    validation.recall
                ),

                "f1": (
                    validation.f1_score
                ),

                "created_at": (
                    validation.created_at.isoformat()
                ),
            },
        }

    finally:

        db.close()
@app.get("/drift")
def get_drift():
    db = SessionLocal()

    try:
        from backend.models import DriftResult

        drift = (
            db.query(DriftResult)
            .order_by(
                DriftResult.created_at.desc()
            )
            .first()
        )

        if not drift:
            return {
                "status": "no_data",
                "drift": None,
            }

        return {
            "status": "success",
            "drift": {
                "id": drift.id,
                "current_period": drift.current_period,
                "baseline_period": drift.baseline_period,
                "baseline_negative_rate": (
                    drift.baseline_negative_rate
                ),
                "current_negative_rate": (
                    drift.current_negative_rate
                ),
                "negative_rate_change": (
                    drift.negative_rate_change
                ),
                "drift_detected": (
                    drift.drift_detected
                ),
                "created_at": (
                    drift.created_at.isoformat()
                ),
            },
        }

    finally:
        db.close()

# =========================================================
# AI ASSISTANT
# =========================================================

@app.post("/assistant")
def ask_assistant(request: dict):

    question = request.get(
        "question",
        "",
    ).strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question is required.",
        )

    try:

        result = answer_question(
            question=question,
            top_k=4,
        )

        return {
            "question": result["question"],
            "answer": result["answer"],
            "sources": result["sources"],
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Assistant request failed: {str(exc)}"
            ),
        )