"""
Pure-Python linear solver for model weight calibration (master prompt §46:
classical ML where classical is sufficient; no numpy/scipy dependency).

Fits weights w minimizing ||X w - y||^2 + ridge * ||w||^2 via the normal
equations with a small ridge term for numerical stability (the feature
matrices here are small and often near-singular without it).
"""
from __future__ import annotations

from typing import Sequence


def _mat_mul(A, B):
    n, m = len(A), len(B[0])
    k = len(B)
    return [[sum(A[i][p] * B[p][j] for p in range(k)) for j in range(m)] for i in range(n)]


def _mat_transpose(A):
    return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]


def _mat_vec_mul(A, v):
    return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]


def _identity(n, scale=1.0):
    return [[scale if i == j else 0.0 for j in range(n)] for i in range(n)]


def _solve_linear(A, b):
    """Solve A x = b for square A via Gaussian elimination with partial pivoting."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]

    for col in range(n):
        # partial pivot
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[pivot] = M[pivot], M[col]
        pv = M[col][col]
        if abs(pv) < 1e-12:
            continue
        for r in range(n):
            if r == col:
                continue
            factor = M[r][col] / pv
            if factor == 0.0:
                continue
            M[r] = [M[r][k] - factor * M[col][k] for k in range(n + 1)]
    return [M[i][n] / M[i][i] if abs(M[i][i]) > 1e-12 else 0.0 for i in range(n)]


def fit_linear(
    features: Sequence[Sequence[float]],
    targets: Sequence[float],
    ridge: float = 1e-4,
) -> list[float]:
    """Return weights w minimizing ||X w - y||^2 + ridge*||w||^2.

    features: list of feature vectors (all same length d).
    targets:   list of scalar targets.
    """
    X = [list(map(float, row)) for row in features]
    y = list(map(float, targets))
    if not X or not y:
        raise ValueError("features and targets must be non-empty")

    Xt = _mat_transpose(X)
    XtX = _mat_mul(Xt, X)
    d = len(XtX)
    XtX_reg = [XtX[i][j] + (ridge if i == j else 0.0) for i in range(d) for j in range(d)]
    XtX_reg = [[XtX_reg[i * d + j] for j in range(d)] for i in range(d)]
    Xty = _mat_vec_mul(Xt, y)
    w = _solve_linear(XtX_reg, Xty)
    return w


def predict_linear(features: Sequence[Sequence[float]], weights: Sequence[float]) -> list[float]:
    return [_mat_vec_mul([list(map(float, f))], list(weights))[0] for f in features]
