from backend.rag.search import get_search_client
from backend.database import SessionLocal
from backend.models import Review, Insight, EvidenceLink


SEARCH_PAGE_SIZE = 1000
DELETE_BATCH_SIZE = 500


def get_all_search_document_ids(search_client) -> list[str]:
    """
    Retrieve all document IDs from Azure AI Search.

    The SDK iterator handles pagination beyond 1,000
    documents.
    """

    results = search_client.search(
        search_text="*",
        select=["id"],
        top=SEARCH_PAGE_SIZE,
    )

    document_ids = []

    for result in results:

        document_id = result.get("id")

        if document_id:
            document_ids.append(document_id)

    return document_ids


def delete_search_documents(
    search_client,
    document_ids: list[str],
) -> int:
    """
    Delete Search documents in safe batches.
    """

    deleted = 0

    for start in range(
        0,
        len(document_ids),
        DELETE_BATCH_SIZE,
    ):

        batch_ids = document_ids[
            start:
            start + DELETE_BATCH_SIZE
        ]

        documents = [
            {"id": document_id}
            for document_id in batch_ids
        ]

        results = search_client.delete_documents(
            documents=documents
        )

        for result in results:

            if result.succeeded:
                deleted += 1

            else:
                raise RuntimeError(
                    "Failed to delete Search document "
                    f"{result.key}: "
                    f"{result.error_message}"
                )

        print(
            "[RESET] Deleted Search documents: "
            f"{deleted}/{len(document_ids)}"
        )

    return deleted


def reset_dataset() -> dict:
    """
    Completely reset the current review dataset.

    Deletes:

        Azure AI Search review documents
        PostgreSQL evidence links
        PostgreSQL insights
        PostgreSQL reviews

    Validation and drift history are preserved.
    """

    search_client = get_search_client()

    # =====================================================
    # AZURE AI SEARCH
    # =====================================================

    print(
        "[RESET] Loading Search document IDs..."
    )

    document_ids = get_all_search_document_ids(
        search_client
    )

    print(
        "[RESET] Search documents found: "
        f"{len(document_ids)}"
    )

    deleted_search = delete_search_documents(
        search_client,
        document_ids,
    )

    # =====================================================
    # POSTGRESQL
    # =====================================================

    db = SessionLocal()

    try:

        evidence_deleted = (
            db.query(EvidenceLink)
            .delete(
                synchronize_session=False
            )
        )

        insights_deleted = (
            db.query(Insight)
            .delete(
                synchronize_session=False
            )
        )

        reviews_deleted = (
            db.query(Review)
            .delete(
                synchronize_session=False
            )
        )

        db.commit()

        print(
            "[RESET] PostgreSQL reviews deleted: "
            f"{reviews_deleted}"
        )

        return {
            "status": "success",
            "search_documents_deleted": deleted_search,
            "evidence_links_deleted": evidence_deleted,
            "insights_deleted": insights_deleted,
            "reviews_deleted": reviews_deleted,
        }

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()