"""
AST-based code similarity (master prompt §16).

Strategy:
  1. For Python: parse AST, normalize identifiers/literals, compute
     tree-edit-like similarity by comparing node-type sequences.
  2. For other languages: token-based similarity fallback.
  3. Blend AST/structural score with token overlap to dampen false
     positives from common boilerplate patterns.
"""
from __future__ import annotations

import ast
import hashlib
import math
import re
from collections import Counter


def _normalize_python_ast(code: str) -> list[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return _tokenize(code)

    tokens: list[str] = []

    def visit(node: ast.AST):
        tokens.append(type(node).__name__)
        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)
    return tokens


def _tokenize(code: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+|[+\-*/%=<>!&|^~]+|[()\[\]{}.,;:@]", code)
    return [t.lower() for t in tokens]


def _jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _structural_similarity(candidate: str, reference: str, language: str) -> float:
    lang = language.lower()
    if lang == "python":
        cand_tokens = _normalize_python_ast(candidate)
        ref_tokens = _normalize_python_ast(reference)
    else:
        cand_tokens = _tokenize(candidate)
        ref_tokens = _tokenize(reference)

    if not cand_tokens or not ref_tokens:
        return 0.0

    return _jaccard(cand_tokens, ref_tokens)


def _token_overlap_similarity(candidate: str, reference: str) -> float:
    cand_tokens = _tokenize(candidate)
    ref_tokens = _tokenize(reference)
    return _jaccard(cand_tokens, ref_tokens)


def compute_ast_similarity(candidate_code: str, reference_code: str, language: str = "python") -> float:
    """
    Returns similarity in 0..1 range.
    Blends structural similarity with token overlap:
      - high structural + high token overlap = high confidence plagiarism signal
      - high token overlap but low structural = likely shared boilerplate
    """
    if not candidate_code.strip() or not reference_code.strip():
        return 0.0

    structural = _structural_similarity(candidate_code, reference_code, language)
    token_ov = _token_overlap_similarity(candidate_code, reference_code)

    # Weighted blend: structural similarity matters more, but token overlap
    # confirms whether the similar structure is semantically meaningful.
    blended = 0.7 * structural + 0.3 * token_ov

    # Dampen if token overlap is high but structural is low — common boilerplate.
    if token_ov > 0.6 and structural < 0.3:
        blended *= 0.5

    return max(0.0, min(1.0, blended))
