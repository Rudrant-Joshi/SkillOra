# Embeddings

Embedding generation is exposed through `shared/model_router.py`
(`ModelRouter.embed(role="embedding_model", text=...)`) rather than through
a class in this directory — the model itself (sentence-transformers, or a
hosted alternative) is a config-level swap, not a code-level one. See
`configs/model_registry.yaml`.

This directory is reserved for any embedding *post-processing* Phase 2+
needs (e.g. dimensionality reduction, code-specific embedding
fine-tuning artifacts) that doesn't belong in the router itself.
