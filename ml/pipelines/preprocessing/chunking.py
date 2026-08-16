"""
Chunking step of the RAG pipeline (master prompt §6: Document -> Parsing ->
Chunking -> Metadata Extraction -> Embedding -> ...).

Simple, dependency-free sliding-window chunker over whitespace/paragraphs.
Language-aware code chunking (split on function/class boundaries via
tree-sitter/AST) is a natural upgrade point — kept out of Phase 1 to avoid
over-engineering (§46), but the function signature already returns
metadata-rich chunks so a smarter chunker can be swapped in later without
touching the rest of the pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    text: str
    chunk_index: int
    metadata: dict[str, Any] = field(default_factory=dict)


def chunk_text(
    text: str,
    *,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    metadata: dict[str, Any] | None = None,
) -> list[Chunk]:
    """
    Splits on paragraph boundaries first, then packs paragraphs into
    windows up to `chunk_size` characters with `chunk_overlap` characters
    of trailing context carried into the next chunk (keeps retrieval from
    losing context at a hard cut).
    """
    if not text.strip():
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[Chunk] = []
    current = ""
    idx = 0

    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(Chunk(text=current, chunk_index=idx, metadata=dict(metadata or {})))
            idx += 1
            overlap_tail = current[-chunk_overlap:] if chunk_overlap else ""
            current = f"{overlap_tail}\n\n{para}".strip()
        else:
            # single paragraph longer than chunk_size: hard-split it
            for i in range(0, len(para), chunk_size - chunk_overlap):
                piece = para[i : i + chunk_size]
                chunks.append(Chunk(text=piece, chunk_index=idx, metadata=dict(metadata or {})))
                idx += 1
            current = ""

    if current:
        chunks.append(Chunk(text=current, chunk_index=idx, metadata=dict(metadata or {})))

    return chunks
