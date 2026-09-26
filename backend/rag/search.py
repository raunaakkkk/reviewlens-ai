import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

load_dotenv()

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
INDEX_NAME = "reviewlens-reviews"

if not SEARCH_ENDPOINT:
    raise RuntimeError("AZURE_SEARCH_ENDPOINT is not configured.")

credential = DefaultAzureCredential()

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=credential,
)


def get_search_client() -> SearchClient:
    return search_client