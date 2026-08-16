"""
RAG ingestion pipeline: Document -> Parsing -> Chunking -> Metadata
Extraction -> Embedding -> Vector Storage (master prompt §6, first half).

Parsing is intentionally minimal in Phase 1 (assumes plain text/markdown
input — PDF/HTML extraction is a preprocessing concern that can sit in
front of this function without changing its contract).
"""
from __future__ import annotations

from typing import Any

from pipelines.preprocessing.chunking import chunk_text
from services.rag.vector_store import InMemoryVectorStore
from shared.model_router import ModelRouter

REQUIRED_METADATA_FIELDS = {"visibility"}  # at minimum, every doc must declare visibility


def ingest_document(
    *,
    text: str,
    metadata: dict[str, Any],
    store: InMemoryVectorStore,
    router: ModelRouter | None = None,
) -> list[str]:
    """
    metadata should include the filtering fields from master prompt §6:
    user_id, company_id, repository_id, course_id, topic, skill, language,
    visibility, permission_scope — whichever apply to this document.

    Returns the list of vector-store record ids created.
    """
    missing = REQUIRED_METADATA_FIELDS - metadata.keys()
    if missing:
        raise ValueError(f"Document metadata missing required field(s): {missing}")

    router = router or ModelRouter()
    chunks = chunk_text(text, metadata=metadata)

    record_ids = []
    for chunk in chunks:
        embedding = router.embed(role="embedding_model", text=chunk.text)
        chunk_metadata = {**chunk.metadata, "chunk_index": chunk.chunk_index}
        record_id = store.upsert(vector=embedding.vector, text=chunk.text, metadata=chunk_metadata)
        record_ids.append(record_id)

    return record_ids
