from pipelines.ingestion.ingest import ingest_document
from pipelines.preprocessing.chunking import chunk_text
from services.rag.schemas import RagFilters, RagQueryRequest
from services.rag.service import query_rag
from services.rag.vector_store import InMemoryVectorStore
from shared.model_router import ModelRouter


def test_chunking_splits_long_text():
    text = ("Paragraph one about SQL joins. " * 10 + "\n\n") * 5
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(len(c.text) <= 250 for c in chunks)  # allow slight overlap slack


def test_chunking_empty_text_returns_no_chunks():
    assert chunk_text("") == []


def test_ingest_requires_visibility_metadata():
    store = InMemoryVectorStore()
    try:
        ingest_document(text="hello world", metadata={}, store=store)
        assert False, "should have raised"
    except ValueError as e:
        assert "visibility" in str(e)


def test_ingest_and_retrieve_roundtrip():
    store = InMemoryVectorStore()
    router = ModelRouter()  # uses hashing fallback embedder if sentence-transformers absent
    ingest_document(
        text="Python list comprehensions provide a concise way to create lists.",
        metadata={"visibility": "public", "topic": "python"},
        store=store,
        router=router,
    )
    assert store.count() >= 1


def test_rag_returns_ungrounded_when_store_empty():
    store = InMemoryVectorStore()
    req = RagQueryRequest(query="What is a Python list comprehension?", filters=RagFilters())
    resp = query_rag(req, store=store)
    assert resp.prediction.grounded is False
    assert resp.prediction.uncertain is True


def test_private_content_not_retrievable_without_matching_owner():
    store = InMemoryVectorStore()
    router = ModelRouter()
    ingest_document(
        text="Confidential company onboarding doc about internal SQL schema.",
        metadata={"visibility": "company_private", "company_id": "acme"},
        store=store,
        router=router,
    )
    # Querying without the matching company_id filter should not ground on it.
    req = RagQueryRequest(
        query="internal SQL schema",
        filters=RagFilters(company_id="other_company"),
    )
    resp = query_rag(req, store=store)
    # Either nothing retrieved, or retrieved-but-not-grounded is acceptable;
    # what must NOT happen is a grounded answer built from acme's private doc.
    if resp.prediction.grounded:
        for chunk in resp.prediction.retrieved_chunks:
            assert chunk.metadata.get("company_id") != "acme"
