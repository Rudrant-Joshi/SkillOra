# Skillora ML Layer — Phase 1 MVP

This is the ML/AI intelligence layer for Skillora. It owns models, training,
datasets, pipelines, inference, RAG, evaluation, recommendations, the skill
engine, and ML tests only.

It does **not** own frontend, backend business logic, authentication,
payments, chat infra, or DevOps. Backend remains the authority for identity,
permissions, and any client-supplied `user_id` / `company_id` / `role`.

## Scope of this delivery (Phase 1)

| # | Component | Status |
|---|-----------|--------|
| 1 | ML service foundation (gateway, schemas, config, model router) | ✅ |
| 2 | Code Intelligence (deterministic analysis + LLM review hook) | ✅ |
| 3 | Assessment Evaluation (deterministic MCQ/code + AI-assisted rubric) | ✅ |
| 4 | Skill Estimation Engine (weighted, evidence-backed, Bayesian-ish) | ✅ |
| 5 | Question Recommendation Engine | ✅ |
| 6 | RAG pipeline (chunk → embed → retrieve → rerank → ground) | ✅ |
| 7 | Candidate Scorecard | ✅ |
| 8 | Adaptive Assessment Engine | ✅ |
| 9 | Candidate-Job Matching | ✅ |
| 10 | Integrity Engine | ✅ |
| 11 | AST Code Similarity | ✅ |
| 12 | AI Study Assistant | ✅ |
| 13 | Content Generation (draft) | ✅ |

Everything from Phase 2–4 (adaptive assessment engine, candidate-job
matching, integrity engine, content generation, feed ranking, etc.) is
intentionally **not** built yet — see `ROADMAP.md`. The module boundaries
(`ai_orchestrator`, `model_router`) are already shaped so those slot in later
without a rewrite.

## Architecture

```
Backend
   ↓
ML Gateway (FastAPI)            ml/gateway/
   ↓
AI Orchestrator                 ml/gateway/orchestrator.py
   ↓
ML Services                     ml/services/*
   ↓
Models / Model Router           ml/models/*, ml/shared/model_router.py
   ↓
Vector DB (pluggable) / Data    ml/services/rag/vector_store.py
```

Every service is a plain, independently-importable Python module with a
Pydantic input schema, a Pydantic output schema, and a pure `run()` function.
The FastAPI gateway is a thin HTTP shell over these — services can be called
directly from a worker/job queue without going through HTTP at all.

## Directory layout

```
ml/
├── gateway/              FastAPI app, routes = the ML API Contract (§25)
│   ├── main.py
│   ├── orchestrator.py   routes requests to the right service
│   └── deps.py           auth-context validation (trusts backend, not client)
├── services/
│   ├── code_intelligence/   static analysis + AI review hook
│   ├── evaluation/          deterministic + AI-assisted assessment evaluation
│   ├── skill_engine/        weighted/Bayesian skill estimation
│   ├── recommendation/      question recommendation engine
│   ├── adaptive_assessment/ adaptive question selection within blueprint
│   ├── candidate_matching/  explainable job-candidate match scoring
│   └── rag/                 chunking, embedding, retrieval, reranking, grounding
├── models/
│   ├── embeddings/       embedding model wrapper (pluggable backend)
│   ├── classifiers/      (stub — Phase 3)
│   └── skill_estimation/ skill state math (no I/O)
├── pipelines/
│   ├── ingestion/        RAG document ingestion pipeline
│   ├── preprocessing/    text/code chunking utilities
│   ├── training/         (stub — nothing to train yet in Phase 1)
│   ├── evaluation/       offline eval harness for skill engine & RAG
│   └── inference/        (thin — services ARE the inference layer)
├── shared/
│   ├── schemas/          Pydantic request/response contracts (§25, §30, §41)
│   ├── config/           env-based settings, model registry config
│   ├── logging/          structured logger incl. inference logging (§35)
│   └── utilities/        auth-context validation, PII scrubbing
├── datasets/              sample/fixture data for local dev
├── evaluation/            evaluation reports land here
├── tests/                 unit + integration + model tests
└── configs/               model_registry.yaml, thresholds.yaml
```

## Setup

```bash
cd ml
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Running locally

```bash
uvicorn gateway.main:app --reload --port 8000
```

## Running tests

```bash
pytest tests/ -v
```

## Model management

Models are declared in `configs/model_registry.yaml` and resolved at runtime
by `shared/model_router.py`. Nothing in the service layer imports an LLM SDK
directly — everything goes through `ModelRouter`, so swapping the LLM
provider or embedding model never touches service code (§24).

## API usage

See `docs/API.md` for the full contract of every endpoint (request schema,
response schema, error schema, model version, confidence, latency
expectation, auth assumptions) per §25/§41.

## Troubleshooting

- `MODEL_UNAVAILABLE` errors → check `configs/model_registry.yaml` and that
  the relevant provider API key is set in `.env`.
- `UNAUTHORIZED_SCOPE` errors → the backend must supply a valid
  `AuthContext` (see `shared/schemas/common.py`); ML never trusts a bare
  client-supplied `user_id`/`company_id`.
- Empty RAG answers with `"grounded": false` → the retriever found nothing
  above the similarity floor; this is intentional (see anti-hallucination
  note in `services/rag/README.md`), not a bug.
