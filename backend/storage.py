import os
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


# Load variables from .env
load_dotenv()


STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

if not STORAGE_ACCOUNT_NAME:
    raise RuntimeError("AZURE_STORAGE_ACCOUNT_NAME is not configured")

if not STORAGE_CONTAINER_NAME:
    raise RuntimeError("AZURE_STORAGE_CONTAINER_NAME is not configured")


ACCOUNT_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"

credential = DefaultAzureCredential()

blob_service_client = BlobServiceClient(
    account_url=ACCOUNT_URL,
    credential=credential,
)

container_client = blob_service_client.get_container_client(
    STORAGE_CONTAINER_NAME
)


def upload_text(text: str, blob_name: str) -> str:
    """
    Upload text content to Azure Blob Storage.
    """

    container_client.upload_blob(
        name=blob_name,
        data=text.encode("utf-8"),
        overwrite=True,
    )

    return f"{ACCOUNT_URL}/{STORAGE_CONTAINER_NAME}/{blob_name}"


def upload_bytes(data: bytes, blob_name: str) -> str:
    """
    Upload binary data to Azure Blob Storage.
    """

    container_client.upload_blob(
        name=blob_name,
        data=data,
        overwrite=True,
    )

    return f"{ACCOUNT_URL}/{STORAGE_CONTAINER_NAME}/{blob_name}"