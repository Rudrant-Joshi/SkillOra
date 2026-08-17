"""
RAG query service: retrieval -> reranking -> context construction ->
grounded LLM answer (master prompt §6, second half).

Anti-hallucination measures:
  - If nothing clears `min_similarity_to_ground_answer`, the service
    returns `grounded=false` and a canned "not enough information" answer
    rather than letting the LLM free-associate.
  - The system prompt instructs the model to answer ONLY from provided
    context and to explicitly say when it's uncertain (master prompt §6:
    "distinguish between retrieved facts, generated explanations, and
    uncertain information").
"""
from __future__ import annotations

import time

from services.rag.retrieval import retrieve
from services.rag.schemas import RagAnswerPrediction, RagQueryRequest, RetrievedChunk
from services.rag.vector_store import InMemoryVectorStore
from shared.config.settings import get_thresholds
from shared.logging.logger import log_inference
from shared.model_router import ModelRouter
from shared.schemas.common import MLResponse, new_request_id

SERVICE_VERSION = "rag-v1"

_SYSTEM_PROMPT = """You answer questions using ONLY the provided context
chunks. Rules:
1. If the context does not contain enough information to answer, say so
   explicitly — do not fill gaps from general knowledge.
2. Clearly separate what the context states as fact from any reasoning or
   inference you add.
3. Do not present an inference as a retrieved fact.
4. Be concise."""


def _build_prompt(query: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n---\n\n".join(f"[Chunk {i+1}]\n{c.text}" for i, c in enumerate(chunks))
    return f"""Context:
{context}

Question: {query}

Answer using only the context above."""


_NOT_ENOUGH_INFO = (
    "I don't have enough grounded information to answer that confidently. "
    "Try rephrasing, or this may not be covered by the available material."
)


def query_rag(
    req: RagQueryRequest,
    store: InMemoryVectorStore,
    router: ModelRouter | None = None,
) -> MLResponse[RagAnswerPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()
    thresholds = get_thresholds()["rag"]
    router = router or ModelRouter()

    top_records = retrieve(
        query=req.query,
        filters=req.filters,
        store=store,
        router=router,
        top_k_retrieve=thresholds["top_k_retrieve"],
        top_k_after_rerank=thresholds["top_k_after_rerank"],
        min_similarity=thresholds["min_similarity_to_retrieve"],
    )

    retrieved_chunks = [
        RetrievedChunk(text=r.text, similarity=round(sim, 4), metadata=r.metadata)
        for r, sim in top_records
    ]

    grounded = bool(retrieved_chunks) and retrieved_chunks[0].similarity >= thresholds[
        "min_similarity_to_ground_answer"
    ]

    if not grounded:
        prediction = RagAnswerPrediction(
            answer=_NOT_ENOUGH_INFO, grounded=False, retrieved_chunks=retrieved_chunks,
            uncertain=True,
        )
        confidence = 0.2
        evidence = ["no chunk cleared the grounding similarity threshold"]
    else:
        result = router.complete(
            role="rag_answer_llm",
            system=_SYSTEM_PROMPT,
            prompt=_build_prompt(req.query, retrieved_chunks),
            max_tokens=600,
        )
        prediction = RagAnswerPrediction(
            answer=result.text.strip(), grounded=True, retrieved_chunks=retrieved_chunks,
            uncertain=False,
        )
        confidence = min(0.95, retrieved_chunks[0].similarity)
        evidence = [f"grounded on {len(retrieved_chunks)} retrieved chunk(s)"]

    response = MLResponse(
        request_id=request_id,
        model_version=SERVICE_VERSION,
        prediction=prediction,
        confidence=confidence,
        evidence=evidence,
        metadata={"top_similarity": retrieved_chunks[0].similarity if retrieved_chunks else 0.0},
    )

    log_inference(
        service="rag", model_version=SERVICE_VERSION, request_id=request_id,
        latency_ms=(time.perf_counter() - start) * 1000, confidence=confidence,
        success=True, extra={"grounded": grounded},
    )
    return response
