"""
Code Intelligence service (master prompt Module A, §4-5).

Strategy: run deterministic static analysis first (always). Only call the
LLM for genuinely semantic tasks — explanation in plain language, review
narrative, refactor suggestions that need understanding of intent — never
to re-derive something AST/regex already computed reliably.
"""
from __future__ import annotations

import time

from services.code_intelligence.schemas import (
    CodeAnalysisPrediction,
    CodeAnalysisRequest,
    Issue,
)
from services.code_intelligence.static_analyzers import (
    analyze,
    compute_quality_score,
    overall_severity,
)
from shared.logging.logger import Timer, log_inference
from shared.model_router import ModelRouter
from shared.schemas.common import MLException, MLResponse, ErrorCode, new_request_id

SERVICE_VERSION = "code-intel-v1"

_LLM_SYSTEM_PROMPT = """You are a senior code reviewer. You will be given code
that has ALREADY been checked by static analysis (AST complexity, known
security patterns, code smells) — do not re-derive metrics you're given.
Focus only on semantic issues static analysis cannot catch: unclear intent,
questionable design choices, missing edge-case handling, naming quality,
and whether the code actually does what its context claims. Be concise.
Respond in under 200 words. Do not invent line numbers you cannot verify."""


def _build_llm_prompt(req: CodeAnalysisRequest, static_issues: list[Issue]) -> str:
    static_summary = (
        "\n".join(f"- [{i.severity}] {i.message}" for i in static_issues) or "(none found)"
    )
    return f"""Task: {req.task}
Language: {req.language}
Context: {req.context or "(none provided)"}

Static analysis already found:
{static_summary}

Code:
```{req.language}
{req.code}
```

Give a short semantic review: what does this code do, any design/intent
issues static analysis wouldn't catch, and 1-3 concrete improvement
suggestions."""


def analyze_code(req: CodeAnalysisRequest, use_llm: bool = True) -> MLResponse[CodeAnalysisPrediction]:
    request_id = new_request_id()
    start = time.perf_counter()
    success = True
    error_code = None

    try:
        metrics, static_issues = analyze(req.language, req.code)
        quality_score = compute_quality_score(metrics, static_issues)
        severity = overall_severity(static_issues)
        security_findings = [i for i in static_issues if i.type == "security"]

        suggestions: list[str] = []
        summary = f"{metrics.lines_of_code} lines analyzed via static analysis."
        confidence = 0.9  # deterministic analysis is high-confidence by construction
        evidence = [f"static_analysis:{i.type}:{i.severity}" for i in static_issues[:10]]

        if use_llm and req.task in ("explain", "review"):
            router = ModelRouter()
            try:
                result = router.complete(
                    role="code_review_llm",
                    system=_LLM_SYSTEM_PROMPT,
                    prompt=_build_llm_prompt(req, static_issues),
                    max_tokens=500,
                )
                summary = result.text.strip()
                suggestions.append("See summary for LLM-derived suggestions.")
                evidence.append(f"llm:{result.model}")
                confidence = 0.75  # blended: deterministic + LLM semantic layer
            except MLException:
                # LLM is best-effort on top of deterministic results; a
                # provider outage should not fail the whole analysis.
                summary += " (LLM semantic review unavailable; deterministic results only.)"
                confidence = 0.7

        prediction = CodeAnalysisPrediction(
            summary=summary,
            issues=static_issues,
            severity=severity,
            suggestions=suggestions,
            complexity=metrics,
            security_findings=security_findings,
            quality_score=quality_score,
        )

        return MLResponse(
            request_id=request_id,
            model_version=SERVICE_VERSION,
            prediction=prediction,
            confidence=confidence,
            evidence=evidence,
            metadata={"language": req.language, "task": req.task},
        )
    except MLException as e:
        success = False
        error_code = e.code.value
        raise
    finally:
        log_inference(
            service="code_intelligence",
            model_version=SERVICE_VERSION,
            request_id=request_id,
            latency_ms=(time.perf_counter() - start) * 1000,
            confidence=None,
            success=success,
            error_code=error_code,
        )
