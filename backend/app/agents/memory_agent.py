from typing import Any

from app.services.chroma_client import get_memory_collection

MEMORY_COLLECTION_NAME = "keyaz_agent_memory"

class MemoryAgent:
    def __init__(self) -> None:
        self.collection = get_memory_collection(MEMORY_COLLECTION_NAME)

    def save_action(self, task_id: str, prompt: str, action: str, metadata: dict[str, Any]) -> None:
        self.collection.add(
            ids=[f"{task_id}:{prompt}:{action}"],
            documents=[action],
            metadatas=[metadata],
        )

    def query_memory(self, prompt: str, n_results: int = 3) -> list[dict[str, Any]]:
        response = self.collection.query(query_texts=[prompt], n_results=n_results)
        docs = response.get("documents", []) or []
        metadatas = response.get("metadatas", []) or []
        results: list[dict[str, Any]] = []
        for i, doc in enumerate(docs[0] if docs else []):
            results.append({
                "action": doc,
                "metadata": metadatas[0][i] if metadatas and len(metadatas[0]) > i else {},
            })
        return results
