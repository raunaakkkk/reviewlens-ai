import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


load_dotenv()

vault_url = os.getenv("AZURE_KEY_VAULT_URL")

if not vault_url:
    raise RuntimeError(
        "AZURE_KEY_VAULT_URL is not configured."
    )

credential = DefaultAzureCredential()

client = SecretClient(
    vault_url=vault_url,
    credential=credential,
)

secret = client.get_secret("DATABASE-URL")

if not secret.value:
    raise RuntimeError(
        "DATABASE-URL secret is empty."
    )

print("============================================================")
print("REVIEWLENS AI - KEY VAULT TEST")
print("============================================================")
print()
print("Key Vault connection : SUCCESS")
print("Secret found         : DATABASE-URL")
print("Secret value         : [HIDDEN]")
print("Secret enabled       :", secret.properties.enabled)
print()
print("Key Vault test passed.")