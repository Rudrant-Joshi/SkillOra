from __future__ import annotations

import pytest

from services.code_similarity.analyzer import compute_ast_similarity, _jaccard, _tokenize


def test_identical_code_high_similarity():
    code = "def add(a, b):\n    return a + b\n"
    sim = compute_ast_similarity(code, code, "python")
    assert sim >= 0.9


def test_different_code_low_similarity():
    a = "def add(a, b): return a + b\n"
    b = "class Foo:\n    pass\n"
    sim = compute_ast_similarity(a, b, "python")
    assert sim < 0.5


def test_renamed_variables_still_similar():
    a = "def add(x, y):\n    return x + y\n"
    b = "def add(a, b):\n    return a + b\n"
    sim = compute_ast_similarity(a, b, "python")
    assert sim >= 0.7


def test_empty_inputs_return_zero():
    assert compute_ast_similarity("", "def foo(): pass", "python") == 0.0
    assert compute_ast_similarity("def foo(): pass", "", "python") == 0.0


def test_jaccard_basic():
    assert _jaccard(["a", "b"], ["a", "b"]) == 1.0
    assert _jaccard(["a"], ["b"]) == 0.0
    assert _jaccard([], []) == 1.0


def test_common_boilerplate_dampened():
    a = "import os\nimport sys\n\nif __name__ == '__main__':\n    pass\n"
    b = "import os\nimport sys\n\nif __name__ == '__main__':\n    pass\n"
    sim = compute_ast_similarity(a, b, "python")
    assert sim >= 0.8
