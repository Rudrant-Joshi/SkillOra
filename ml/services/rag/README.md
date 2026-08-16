# RAG Service

Implements master prompt §6: Document → Parsing → Chunking → Metadata
Extraction → Embedding → Vector Storage → Retrieval → Reranking → Context
Construction → LLM → Grounded Answer.

## Files

- `../../pipelines/preprocessing/chunking.py` — chunking
- `../../pipelines/ingestion/ingest.py` — ingestion pipeline (parse → chunk → embed → store)
- `vector_store.py` — pluggable vector store (in-memory reference impl)
- `retrieval.py` — retrieval + metadata-filtered authorization boundary + lexical rerank
- `service.py` — query orchestration + grounded answer generation
- `schemas.py` — request/response contracts

## Anti-hallucination design

1. Retrieval requires a minimum similarity (`thresholds.yaml:
   rag.min_similarity_to_retrieve`) to even be considered.
2. Grounding requires a *higher* minimum similarity
   (`rag.min_similarity_to_ground_answer`). If nothing clears it, the
   service returns `grounded: false` and a fixed "not enough information"
   message — it never lets the LLM answer from ungrounded context.
3. The LLM system prompt explicitly requires it to distinguish retrieved
   fact from generated inference, and to say when it's uncertain, per
   master prompt §6.

## Authorization boundary

`retrieval.py::_build_metadata_filter` enforces that private content
(`visibility: company_private` / `user_private`) is only retrievable when
the caller-supplied filter matches an owner field on the chunk. Public
content (`visibility: public`) is always retrievable. This is a
defense-in-depth filter — the caller (gateway) is still responsible for
only forwarding a legitimate `AuthContext`-derived filter, never raw
client input.
