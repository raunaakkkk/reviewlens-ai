from backend.rag.search import get_search_client


DOCUMENT_ID = "5ab2206d-0487-4f4c-8f94-10fcf152de7d"


if __name__ == "__main__":

    search_client = get_search_client()

    print("\n" + "=" * 60)
    print("REVIEWLENS AI - REMOVE OLD TEST DOCUMENT")
    print("=" * 60)

    print("\nDocument to delete:")
    print(DOCUMENT_ID)

    confirmation = input(
        "\nType DELETE to confirm: "
    )

    if confirmation != "DELETE":
        print("\nDeletion cancelled.")
        raise SystemExit

    result = search_client.delete_documents(
        documents=[
            {
                "id": DOCUMENT_ID
            }
        ]
    )

    print("\nDocument deletion requested.")

    print("Result:")
    print(result)

    print("\n" + "=" * 60)