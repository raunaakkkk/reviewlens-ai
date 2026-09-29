import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()


# ============================================================
# AZURE KEY VAULT
# ============================================================

KEY_VAULT_URL = os.getenv(
    "AZURE_KEY_VAULT_URL"
)

if not KEY_VAULT_URL:
    raise RuntimeError(
        "AZURE_KEY_VAULT_URL is not configured."
    )


credential = DefaultAzureCredential()

secret_client = SecretClient(
    vault_url=KEY_VAULT_URL,
    credential=credential,
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

DATABASE_URL = secret_client.get_secret(
    "DATABASE-URL"
).value

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE-URL secret is empty."
    )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()