from urllib.parse import urlparse

from chromadb import Client
from chromadb.config import Settings

from app.core.config import settings

_chroma_client: Client | None = None

def get_chroma_client() -> Client:
    global _chroma_client
    if _chroma_client is None:
        parsed = urlparse(settings.chroma_url)
        chroma_settings = Settings(
            chroma_server_host=parsed.hostname or "chromadb",
            chroma_server_http_port=parsed.port or 8000,
            chroma_server_api_default_path=parsed.path or "/api/v2",
        )
        _chroma_client = Client(settings=chroma_settings)
    return _chroma_client

def get_memory_collection(name: str = "keyaz_memory"):
    client = get_chroma_client()
    return client.get_or_create_collection(name=name)
