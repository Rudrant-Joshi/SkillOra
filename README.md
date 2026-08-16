# Skillora

A unified developer platform where your coding activity — code you push,problems
you solve,and contributions you make — automatically builds your public
developer profile. No separate "write your bio" step: the profile is *earned*, not
authored.

This repo is the **ML/AI intelligence layer** (see [`ml/`](ml/)). It owns models,
pipelines, inference, RAG, evaluation, recommendations, the skill engine, feed
ranking, difficulty estimation, learning paths, and reputation scoring. The
backend remains the authority for identity, permissions, and any
client-supplied `user_id` / `company_id` / `role`.

## What the ML layer does

- **Profile Intelligence** — auto-generates profile summaries, infers skills from
  raw activity, and scores profile completeness (the "activity is your profile"
  connective tissue).
- **Activity Feed** — personalizes the social feed (recency + social graph +
  skill relevance + engagement), detects trending skills/topics, and suggests
  who to follow.
- **Problem Difficulty** — estimates and calibrates judge problem difficulty from
  text features and aggregate submission outcomes.
- **Learning Path** — builds prerequisite-aware study plans and recommends the
  next milestone from a learner's current skills.
- **Developer Reputation** — an explainable, auditable trust score composed of
  transparent factors, plus per-activity quality scoring.
- Plus: code intelligence, assessment evaluation, skill estimation, question
  recommendation, RAG, adaptive assessment, candidate-job matching, integrity,
  code similarity, AI study assistant, and content generation.

## Quick start

```bash
cd ml
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn gateway.main:app --reload --port 8000
```

## Tests

```bash
pytest tests/ -v
```

See [`ml/README.md`](ml/README.md) for architecture and
[`ml/docs/API.md`](ml/docs/API.md) for the full endpoint contract.
