"""
Vector store abstraction for RAG (master prompt §5, §6: "Store embeddings
in the platform vector database. The embedding layer must be replaceable
without changing the overall application architecture.")

Ships an in-memory cosine-similarity store (dependency-free, good for
local dev/tests) behind the same interface a real FAISS/Pinecone/pgvector
backend would implement, so swapping the backend is a one-class change.

CRITICAL: every stored vector carries a metadata dict used for permission
filtering at query time (user_id, company_id, repository_id, course_id,
topic, skill, language, visibility, permission_scope — master prompt §6).
This module enforces filtering by metadata; it does NOT determine what a
caller is *allowed* to query for — that's the AuthContext check upstream.
"""
from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class VectorRecord:
    id: str
    vector: list[float]
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1e-9
    norm_b = math.sqrt(sum(y * y for y in b)) or 1e-9
    return dot / (norm_a * norm_b)


class InMemoryVectorStore:
    """
    Reference implementation of the vector store interface. Real deployments
    swap this for FAISS (local ANN index) or a hosted vector DB — callers
    only depend on `upsert` / `query`, both of which any real backend can
    implement identically.
    """

    def __init__(self) -> None:
        self._records: dict[str, VectorRecord] = {}

    def upsert(self, vector: list[float], text: str, metadata: dict[str, Any]) -> str:
        record_id = str(uuid.uuid4())
        self._records[record_id] = VectorRecord(id=record_id, vector=vector, text=text, metadata=metadata)
        return record_id

    def query(
        self,
        vector: list[float],
        top_k: int = 12,
        metadata_filter: Callable[[dict[str, Any]], bool] | None = None,
        min_similarity: float = 0.0,
    ) -> list[tuple[VectorRecord, float]]:
        scored = []
        for record in self._records.values():
            if metadata_filter and not metadata_filter(record.metadata):
                continue
            sim = _cosine_similarity(vector, record.vector)
            if sim >= min_similarity:
                scored.append((record, sim))
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:top_k]

    def count(self) -> int:
        return len(self._records)
