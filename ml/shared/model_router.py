"""
ModelRouter — the single abstraction between services and model providers
(master prompt §24).

Services never import an LLM SDK or embedding library directly. They call
`ModelRouter.complete(role=...)` or `ModelRouter.embed(role=...)`. The role
is resolved against configs/model_registry.yaml, so switching providers or
models is a config change, not a code change, and each capability
(LLM / embedding / reranker) can be swapped independently.

This file intentionally ships with a real Anthropic backend for `complete`
(since Claude is already available in this environment) and a clearly
marked local/pluggable backend for `embed`, so the RAG pipeline is runnable
without any external embedding API. Swap `_embed_local` for a hosted
embedding provider by adding a branch keyed on `provider` — no caller
changes required.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any, Optional

from shared.config.settings import get_model_registry, get_settings
from shared.schemas.common import ErrorCode, MLException


@dataclass
class CompletionResult:
    text: str
    model: str
    provider: str
    raw: Optional[dict[str, Any]] = None


@dataclass
class EmbeddingResult:
    vector: list[float]
    model: str
    provider: str
    dimensions: int


class ModelRouter:
    def __init__(self) -> None:
        self._registry = get_model_registry()
        self._settings = get_settings()

    def _resolve(self, role: str) -> dict:
        entry = self._registry.get(role)
        if entry is None:
            raise MLException(
                ErrorCode.MODEL_UNAVAILABLE, f"No model registered for role '{role}'."
            )
        return entry

    # ---- LLM completion -------------------------------------------------

    def complete(
        self,
        role: str,
        system: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.2,
    ) -> CompletionResult:
        entry = self._resolve(role)
        provider = entry["provider"]

        if provider == "anthropic":
            return self._complete_anthropic(entry, system, prompt, max_tokens, temperature)

        raise MLException(
            ErrorCode.MODEL_UNAVAILABLE, f"LLM provider '{provider}' has no adapter configured."
        )

    def _complete_anthropic(
        self, entry: dict, system: str, prompt: str, max_tokens: int, temperature: float
    ) -> CompletionResult:
        try:
            import anthropic
        except ImportError as e:
            raise MLException(
                ErrorCode.MODEL_UNAVAILABLE,
                "anthropic package not installed. `pip install anthropic`.",
            ) from e

        if not self._settings.llm_api_key:
            raise MLException(
                ErrorCode.MODEL_UNAVAILABLE,
                "LLM_API_KEY is not set; cannot call Anthropic provider.",
            )

        client = anthropic.Anthropic(api_key=self._settings.llm_api_key)
        response = client.messages.create(
            model=entry["model"],
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        return CompletionResult(
            text=text, model=entry["model"], provider="anthropic", raw=response.model_dump()
        )

    # ---- Embeddings -------------------------------------------------------

    def embed(self, role: str, text: str) -> EmbeddingResult:
        entry = self._resolve(role)
        provider = entry["provider"]

        if provider == "sentence-transformers":
            return self._embed_sentence_transformers(entry, text)

        raise MLException(
            ErrorCode.MODEL_UNAVAILABLE,
            f"Embedding provider '{provider}' has no adapter configured.",
        )

    def _embed_sentence_transformers(self, entry: dict, text: str) -> EmbeddingResult:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            # Deterministic local fallback so the pipeline is runnable/testable
            # without the (fairly heavy) sentence-transformers dependency.
            # This is NOT a semantic embedding — it's a hashed bag-of-words
            # projection used only so RAG/tests can run end-to-end offline.
            # Swap in a real provider by installing sentence-transformers,
            # or add a hosted-API branch above.
            return self._embed_hashing_fallback(entry, text)

        model = _get_sentence_transformer(entry["model"])
        vector = model.encode(text, normalize_embeddings=True).tolist()
        return EmbeddingResult(
            vector=vector, model=entry["model"], provider="sentence-transformers",
            dimensions=len(vector),
        )

    def _embed_hashing_fallback(self, entry: dict, text: str) -> EmbeddingResult:
        dims = entry.get("dimensions", 384)
        vector = [0.0] * dims
        tokens = text.lower().split()
        for token in tokens:
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            vector[h % dims] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        vector = [v / norm for v in vector]
        return EmbeddingResult(
            vector=vector, model="hashing-fallback", provider="local-fallback", dimensions=dims
        )


_st_model_cache: dict[str, Any] = {}


def _get_sentence_transformer(model_name: str):
    if model_name not in _st_model_cache:
        from sentence_transformers import SentenceTransformer

        _st_model_cache[model_name] = SentenceTransformer(model_name)
    return _st_model_cache[model_name]
