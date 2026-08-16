# ML Roadmap

## Phase 1 — completed
1. ML service foundation
2. Code analysis
3. Assessment evaluation
4. Skill estimation
5. Question recommendation
6. RAG
7. Candidate scorecard

## Phase 2 — in progress
8. Adaptive assessment engine (question selection *within* an
    approved blueprint — must never alter duration/question count/skills/
    scoring rules, only pick among approved questions) ✅
9. Candidate-job matching (semantic match, explainable, no sensitive
    characteristics) ✅
10. AI study assistant (explanations, flashcards, study plans)
11. AI question generation + validation (must run generated code through
    the secure execution sandbox before approval — sandbox is backend/DevOps
    owned, ML only produces + validates the draft)
12. Learning/feed recommendation engine

## Phase 3 — in progress
13. Integrity model (rule engine + ML risk model, never auto-reject) ✅
14. AST-based code similarity engine ✅
15. AI study assistant (explanations, study plans, flashcards) ✅
16. AI question generation + validation (draft only; backend sandbox + recruiter approval required) ✅
17. Feed ranking (deferred — low priority for MVP)

## Phase 4 — not built yet
18. Model optimization / ONNX export
19. Continuous learning
20. Advanced analytics
21. Large-scale recommendation infra
22. Multimodal AI

## Explicit non-goals (per master prompt §40)
- No frontend, dashboards, or UI of any kind
- No auth, payments, chat infra
- No automatic hiring decisions or automatic candidate rejection
- No use of sensitive/protected characteristics
- No silent publishing of AI-generated assessments
- No training on unauthorized private data
- No single hard-coded model provider

