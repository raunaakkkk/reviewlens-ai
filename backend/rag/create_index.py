import os

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SimpleField,
    SearchableField,
)

load_dotenv()

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
INDEX_NAME = "reviewlens-reviews"

if not SEARCH_ENDPOINT:
    raise RuntimeError("AZURE_SEARCH_ENDPOINT is not configured.")

credential = DefaultAzureCredential()

index_client = SearchIndexClient(
    endpoint=SEARCH_ENDPOINT,
    credential=credential,
)

fields = [
    SimpleField(
        name="id",
        type=SearchFieldDataType.String,
        key=True,
    ),

    SearchableField(
        name="review_text",
        type=SearchFieldDataType.String,
    ),

    SearchableField(
        name="redacted_text",
        type=SearchFieldDataType.String,
    ),

    SimpleField(
        name="sentiment",
        type=SearchFieldDataType.String,
        filterable=True,
    ),

    SearchField(
        name="positive_score",
        type=SearchFieldDataType.Double,
    ),

    SearchField(
        name="neutral_score",
        type=SearchFieldDataType.Double,
    ),

    SearchField(
        name="negative_score",
        type=SearchFieldDataType.Double,
    ),

    SimpleField(
        name="review_hash",
        type=SearchFieldDataType.String,
        filterable=True,
    ),

    SearchField(
        name="embedding",
        type=SearchFieldDataType.Collection(
            SearchFieldDataType.Single
        ),
        searchable=True,
        vector_search_dimensions=384,
        vector_search_profile_name="review-vector-profile",
    ),
]

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="review-hnsw"
        )
    ],
    profiles=[
        VectorSearchProfile(
            name="review-vector-profile",
            algorithm_configuration_name="review-hnsw",
        )
    ],
)

index = SearchIndex(
    name=INDEX_NAME,
    fields=fields,
    vector_search=vector_search,
)

result = index_client.create_or_update_index(index)

print("Azure AI Search index created successfully.")
print("Index name:", result.name)
print("Vector dimensions: 384")