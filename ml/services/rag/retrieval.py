"""
Retrieval + (lightweight) reranking + context construction — the middle of
the RAG pipeline (master prompt §6).

Reranking here is a cheap lexical-overlap re-scorer layered on top of the
vector similarity score. A cross-encoder reranker (configured in
model_registry.yaml as `reranker_model`) is the natural upgrade and can be
dropped in without changing the retrieval contract — kept out of Phase 1
to avoid an extra heavy model dependency for an MVP (§46).
"""
from __future__ import annotations

from services.rag.schemas import RagFilters
from services.rag.vector_store import InMemoryVectorStore, VectorRecord
from shared.model_router import ModelRouter


def _build_metadata_filter(filters: RagFilters):
    filter_dict = {k: v for k, v in filters.model_dump().items() if v is not None}

    def predicate(metadata: dict) -> bool:
        # Visibility/authorization boundary: a chunk is retrievable only if
        # every filter field the caller specified matches, OR the chunk is
        # explicitly public. This keeps company/user-private content from
        # crossing boundaries (master prompt §6: "Never retrieve private
        # company or user information across unauthorized boundaries.")
        if metadata.get("visibility") == "public":
            return True
        for key, value in filter_dict.items():
            if key == "visibility":
                continue
            if metadata.get(key) is not None and metadata.get(key) != value:
                return False
        # private content requires an explicit owner/scope match
        if metadata.get("visibility") in ("company_private", "user_private"):
            owner_keys = {"user_id", "company_id"} & metadata.keys()
            return any(metadata.get(k) == filter_dict.get(k) for k in owner_keys)
        return True

    return predicate


def _lexical_overlap(query: str, text: str) -> float:
    q_tokens = set(query.lower().split())
    t_tokens = set(text.lower().split())
    if not q_tokens:
        return 0.0
    return len(q_tokens & t_tokens) / len(q_tokens)


def retrieve(
    query: str,
    filters: RagFilters,
    store: InMemoryVectorStore,
    router: ModelRouter,
    top_k_retrieve: int,
    top_k_after_rerank: int,
    min_similarity: float,
) -> list[tuple[VectorRecord, float]]:
    embedding = router.embed(role="embedding_model", text=query)
    predicate = _build_metadata_filter(filters)

    candidates = store.query(
        vector=embedding.vector,
        top_k=top_k_retrieve,
        metadata_filter=predicate,
        min_similarity=min_similarity,
    )

    # rerank: blend vector similarity with lexical overlap
    reranked = [
        (record, 0.7 * sim + 0.3 * _lexical_overlap(query, record.text))
        for record, sim in candidates
    ]
    reranked.sort(key=lambda t: t[1], reverse=True)
    return reranked[:top_k_after_rerank]
