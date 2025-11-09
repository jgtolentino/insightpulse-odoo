from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple


class VectorBackend(Protocol):
    """
    Minimal protocol for a vector backend (e.g. Qdrant, pgvector).

    Concrete implementations can live here or in a separate file and
    be selected via configuration or environment variables.
    """

    def upsert(self, points: List[Dict[str, Any]]) -> None:
        ...

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        ...


@dataclass
class MemoryRecord:
    id: str
    text: str
    metadata: Dict[str, Any]


class AgentMemory:
    """
    Unified interface for agent memory / RAG retrieval.

    Depending on configuration, this can connect to:
    - Qdrant
    - pgvector
    - Any other supported backend

    Connection details come from environment variables:
    - QDRANT_URL
    - QDRANT_API_KEY
    - PGVECTOR_DSN
    (or similar — adapt to your final choice)
    """

    def __init__(
        self,
        backend: Optional[VectorBackend] = None,
        *,
        collection_name: str = "insightpulse_memory",
    ) -> None:
        self.backend = backend
        self.collection_name = collection_name

        # Placeholder for connection parameters. Actual wiring is done
        # in your concrete backend implementation.
        self.qdrant_url = os.getenv("QDRANT_URL", "")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        self.pgvector_dsn = os.getenv("PGVECTOR_DSN", "")

    # ------------------------------------------------------------------ #
    # Public API for agents
    # ------------------------------------------------------------------ #

    def add_records(self, records: List[MemoryRecord]) -> None:
        """
        Add or update records in the vector store.

        A separate embedding service is assumed. This method expects
        embeddings to be precomputed or delegates to a helper you plug in.
        """
        if self.backend is None:
            # No-op if not configured; safe for dev / tests.
            return

        points: List[Dict[str, Any]] = []
        for record in records:
            # NOTE: embedding generation is intentionally not implemented here.
            # You can plug in your embedding pipeline as needed.
            # For now, we only pass metadata; actual vector is backend-specific.
            points.append(
                {
                    "id": record.id,
                    "payload": {
                        "text": record.text,
                        **record.metadata,
                    },
                    # "vector": [...],  # add when embeddings are provided
                }
            )
        self.backend.upsert(points)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant records.

        - In production, this will:
          - Use an embedding model (OpenAI, Anthropic, etc.) to embed `query`.
          - Call the backend's `search` method.
        - For now, this method returns an empty list if no backend is configured.
        """
        if self.backend is None:
            return []

        query_vector = self._embed_query(query)
        return self.backend.search(query_vector=query_vector, top_k=top_k)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _embed_query(self, query: str) -> List[float]:
        """
        Placeholder for query embedding.

        You will typically:
        - Call a hosted embedding API using something like OPENAI_API_KEY
          or ANTHROPIC_API_KEY.
        - Or call a local embedding service behind your own endpoint.

        Env placeholders only — no direct secrets here.
        """
        # TODO: implement actual embedding logic.
        # For now, return a dummy vector to satisfy type expectations.
        return [0.0] * 768  # adjust dimensionality to match your chosen model
