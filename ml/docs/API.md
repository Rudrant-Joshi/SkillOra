# ML API Documentation

All endpoints share the standard success/error envelope (master prompt §25/§41).

**Success (`MLResponse`)**
```json
{
  "request_id": "req_...",
  "model_version": "service-name-v1",
  "prediction": { "...": "service-specific" },
  "confidence": 0.87,
  "evidence": ["..."],
  "metadata": { "...": "..." }
}
```

**Error (`MLErrorResponse`)**
```json
{ "request_id": "req_...", "error": { "code": "MODEL_UNAVAILABLE", "message": "..." } }
```

Error codes: `MODEL_UNAVAILABLE`, `VALIDATION_ERROR`, `UNAUTHORIZED_SCOPE`,
`NOT_FOUND`, `RATE_LIMITED`, `INTERNAL_ERROR`, `UNSUPPORTED_LANGUAGE`, `CONTENT_POLICY`.

**Auth headers** (every request, backend-attested — never raw client input):
`X-User-Id`, `X-Role`, `X-Company-Id` (optional), `X-Permission-Scopes`
(comma-separated), `X-Repository-Ids` (comma-separated), `X-Company-Ids-Allowed`
(comma-separated).

---

## POST /ml/code/analyze · /ml/code/explain · /ml/code/review

**Input** (`CodeAnalysisRequest`): `language`, `repository?`, `file?`, `code`, `context?`, `task`.

**Output prediction** (`CodeAnalysisPrediction`): `summary`, `issues[]`,
`severity`, `suggestions[]`, `complexity{}`, `security_findings[]`,
`quality_score` (0-100), `duplicate_code_hints[]`.

**Model**: `code-intel-v1`. Deterministic static analysis (AST for Python,
regex heuristics elsewhere) always runs; LLM (`code_review_llm` role) is
called only for `explain`/`review` tasks and only adds semantic narrative
on top of static results — it never re-derives complexity/security
findings the static pass already computed.

**Latency**: static-only ~<100ms; with LLM call, ~1-4s (network + generation bound).

**Auth**: any authenticated caller; `repository`/`file` values are opaque
identifiers, not used to authorize — the backend must have already checked
the caller can access that repo/file before calling this endpoint.

---

## POST /ml/assessment/evaluate

**Input** (`EvaluateRequest`): `question_id`, `question_type`
(`mcq|multi_select|sql|coding|short_answer|system_design`), plus
type-specific fields (`correct_options`/`submitted_options` for MCQ,
`test_results` for coding/sql, `prompt`/`submitted_answer`/`rubric` for
short_answer/system_design).

**Output prediction** (`EvaluationPrediction`): `score` (0-100),
`evaluation_method` (`deterministic|ai_assisted|hybrid`), `strengths[]`,
`weaknesses[]`, `reasoning`, `needs_human_review`.

**Model**: `evaluation-v1`. `mcq`/`multi_select`/`coding`/`sql` are scored
deterministically (confidence always 1.0). `short_answer`/`system_design`
use `assessment_grading_llm`; confidence is lower and `needs_human_review`
is set when the rubric is missing or the answer is very short.

**Critical**: never pass hidden test cases or reference solutions into a
prompt whose text could be echoed back — `ai_assisted.py` only ever grades
the candidate's own submission against a rubric string.

**Latency**: deterministic <10ms; AI-assisted ~1-3s.

---

## POST /ml/assessment/select-question · /ml/recommendations

**Input** (`RecommendQuestionRequest`): `candidate_id`,
`candidate_profile.skills` (map of skill → 0..1 level),
`approved_question_pool[]` (the recruiter-approved blueprint pool — the ML
layer selects *within* this only), `target_skills[]`, `exclude_question_ids[]`, `top_k`.

**Output prediction** (`RecommendQuestionPrediction`):
`recommendations[]`, each `{question_id, selection_score, reason}`.

**Model**: `recommendation-v1`. Deterministic scoring: 55% weight on
targeting a weak/target skill, 45% weight on difficulty proximity to
estimated candidate level. Enforces `max_question_reexposure` from
`thresholds.yaml`.

**Critical rule enforced**: this endpoint never changes duration, question
count, allowed skills, question types, difficulty distribution, or scoring
rules — it only ranks/selects among `approved_question_pool` as supplied
by the caller.

**Latency**: <50ms for pools up to a few thousand questions (pure Python scoring).

---

## POST /ml/assessment/scorecard

**Input** (`ScorecardRequest`): `candidate_id`, `assessment_id`,
`dimension_scores[]` (each `{dimension, score, confidence, question_id}` —
typically the output of repeated `/ml/assessment/evaluate` calls).

**Output prediction** (`ScorecardPrediction`): `overall_score`,
`dimensions{}` (per-dimension confidence-weighted average),
`dimension_confidence{}`.

**Model**: `scorecard-v1`. Pure aggregation, deterministic.

**Important**: decision-support only. This is not a hiring recommendation
and must not be used for automatic accept/reject (master prompt §13, §40).

---

## POST /ml/skill/estimate · /ml/skill/estimate-batch

**Input** (`SkillEstimateRequest`): `user_id`, `skill`, `evidence[]` (each
`{source, observed_value, timestamp, weight_override?, detail?}`).
Batch variant takes `skills: {skill_name: evidence[]}`.

**Output prediction** (`SkillEstimatePrediction`): `skill`,
`estimated_level` (0..1), `confidence` (0..1), `evidence_count`.

**Model**: `skill-v1`. Weighted/recency-decayed Bayesian-style update (see
`models/skill_estimation/estimator.py`) — explicitly not a simple average
(master prompt §8). Confidence grows with accumulated *reliable* evidence
mass, capped at 0.95; floors at a configurable minimum with no evidence.

**Latency**: <10ms (pure computation, no model call).

---

## POST /ml/rag/query

**Input** (`RagQueryRequest`): `query`, `filters` (all optional:
`user_id`, `company_id`, `repository_id`, `course_id`, `topic`, `skill`,
`language`, `visibility`), `top_k`.

**Output prediction** (`RagAnswerPrediction`): `answer`, `grounded`
(bool), `retrieved_chunks[]` (`{text, similarity, metadata}`), `uncertain`.

**Model**: `rag-v1`. Retrieval + lexical rerank + `rag_answer_llm`
grounded generation. If no chunk clears `rag.min_similarity_to_ground_answer`,
returns `grounded: false` with a fixed "not enough information" answer
rather than letting the LLM guess.

**Latency**: retrieval <50ms (in-memory store); with LLM generation ~1-4s.

**Auth**: `filters` should be populated from the caller's `AuthContext` by
the backend before this call — the retrieval layer enforces that private
(`company_private`/`user_private`) chunks only match when an owner field
in `filters` matches the chunk's metadata.

---

## POST /ml/assessment/adaptive/select-question (Phase 2)

**Input** (`AdaptiveSelectRequest`): `candidate_id`, `assessment_id`,
`blueprint` (`QuestionBlueprintConstraints`: `total_questions`,
`allowed_skills`, `allowed_question_types`, `difficulty_distribution`,
`max_duration_seconds?`, `coding_languages`), `skill_profile` (map of
`SkillEstimateInput` per skill), `answered_questions[]`,
`remaining_approved_pool[]` (caller-supplied approved pool),
`target_skills[]`, `top_k`.

**Output prediction** (`AdaptiveSelectPrediction`): `next_question`
(`RecommendedAdaptiveQuestion` or `null`), `current_skill_estimates`,
`updated_confidence`, `questions_answered`, `questions_remaining`,
`blueprint_progress`.

**Model**: `adaptive-assessment-v1`. Deterministic selection. Does NOT
modify duration, question count, allowed skills, question types,
difficulty distribution, or scoring rules — only ranks questions within
the caller-supplied `remaining_approved_pool`.

**Critical**: this endpoint never changes the examination. It only picks
the next question among already-approved items.

**Latency**: <50ms for pools up to a few thousand questions.

---

## POST /ml/candidate/match (Phase 2)

**Input** (`CandidateJobMatchRequest`): `job` (`JobRequirement`:
`job_id`, `title`, `required_skills[]`, `preferred_skills[]`,
`min_experience_years?`, `description?`), `candidate` (`CandidateProfile`:
`candidate_id`, `skills{}`, `experience_years?`, `summary?`),
`assessment_results?`, `shared_repository_ids[]`, `shared_project_ids[]`,
`top_k`.

**Output prediction** (`CandidateJobMatchPrediction`): `match_score`
(0..1), `matched_skills[]`, `missing_skills[]`, `evidence[]`,
`confidence` (0..1).

**Model**: `candidate-matching-v1`. Deterministic, explainable scoring
over job-relevant evidence only. No sensitive personal characteristics
are used. Decision-support only — not a hiring decision.

**Latency**: <10ms (pure computation, no model call).

---

## POST /ml/integrity/analyze (Phase 3)

**Input** (`AnalyzeIntegrityRequest`): `candidate_id`, `assessment_id`,
`signals[]` (proctoring signal events: `type`, `timestamp?`, optional
payload), `submitted_code?`, `reference_solution?`, `language?`.

**Output prediction** (`IntegrityPrediction`): `integrity_score` (0..100),
`band` (`clean`|`minor_flags`|`suspicious`|`high_risk`), `flags[]`,
`ast_similarity?`, `explanation`, `confidence` (0..1).

**Model**: `integrity-v1`. Hybrid rule engine + statistical anomaly detection.
Never auto-reject. Decision-support only.

**Latency**: <20ms (pure computation).

---

## POST /ml/code/similarity (Phase 3)

**Input** (`CodeSimilarityRequest`): `candidate_code`, `reference_code?`,
`language`, `comparison_type` (`reference_solution`|`candidate_vs_candidate`|`corpus`).

**Output prediction** (`CodeSimilarityPrediction`): `similarity` (0..1),
`method` (`ast+embedding`), `comparison`, `confidence` (0..1).

**Model**: `code-similarity-v1`. AST normalization + token overlap blend.
Dampens false positives from common boilerplate patterns.

**Latency**: <50ms for typical code snippets.

---

## POST /ml/study/assist (Phase 3)

**Input** (`StudyAssistRequest`): `user_id`, `query`, `skill_profile?`
(skill → level map), `context?`, `mode` (`explain`|`study_plan`|`flashcard`).

**Output prediction** (`StudyAssistPrediction`): `answer`, `mode`,
`grounded` (bool), `sources[]`, `confidence` (0..1).

**Model**: `study-assistant-v1`. LLM-powered tutor. Returns `grounded=false`
when no retrieval context is provided.

**Latency**: ~1-4s (LLM bound).

---

## POST /ml/assessment/generate (Phase 3)

**Input** (`GenerateQuestionRequest`): `skill`, `topic`, `difficulty`
(0..1), `question_type` (`mcq`|`coding`|...), `language?`, `job_role?`,
`assessment_blueprint?`.

**Output prediction** (`GenerateQuestionPrediction`): `draft`
(`GeneratedQuestionDraft`), `confidence` (0..1).

**Model**: `question-generation-v1`. AI-generated draft only.
`requires_human_review=true` always. Backend must validate (including
running generated code in the secure sandbox) and a recruiter must
approve before publishing.

**Critical**: AI must not silently publish an assessment.

**Latency**: ~1-3s (LLM bound).

---

## POST /ml/profile/summary · /ml/profile/infer-skills · /ml/profile/completeness (Phase 1.5)

The DevConnect connective-tissue ML: a developer's profile is earned from
activity, not written. These endpoints turn raw activity (snippets, problem
submissions, follows) into an auto-generated profile.

### POST /ml/profile/infer-skills

**Input** (`InferSkillsFromActivityRequest`): `user_id`,
`activities[]` (each `{activity_type, title, description?, language?, skills_mentioned[], created_at}`),
`current_skills` (map).

**Output prediction** (`InferredSkillsPrediction`): `inferred_skills[]`
(`{skill, inferred_level 0..1, confidence, evidence[]}`), `new_skills_detected[]`, `confidence`.

**Model**: `profile-intelligence-v1`. Deterministic: language → primary skill,
framework keywords → framework skill, problem topics → algorithm/concept
skills. Each signal feeds the Bayesian `estimate_skill` (§8) so inferred
levels carry confidence and decay with age.

### POST /ml/profile/summary

**Input** (`GenerateProfileSummaryRequest`): `user_id`, `username`, `bio?`,
`activities[]`, `current_skills`.
**Output prediction** (`ProfileSummaryPrediction`): `summary`, `top_skills[]`,
`suggested_headline`, `activity_count`, `profile_strength`
(`empty|emerging|active|established`).
**Model**: `profile-intelligence-v1`. Deterministic summary + headline; uses
`profile_summary_llm` role when available, degrades to templated summary.

### POST /ml/profile/completeness

**Input** (`ScoreProfileCompletenessRequest`): `user_id`, `username`, `bio?`,
`activities[]`, `current_skills`.
**Output prediction** (`ProfileCompletenessPrediction`): `completeness_score`
(0-100), `band`, `missing_fields[]`, `suggestions[]`, `verification_eligible`.

**Latency**: <10ms (pure computation).

---

## POST /ml/feed/rank · /ml/feed/trending · /ml/connections/suggest (Phase 1.5)

Activity feed intelligence for the social graph.

### POST /ml/feed/rank

**Input** (`RankFeedRequest`): `viewer_id`, `viewer_skills`, `followed_user_ids[]`,
`candidate_pool[]` (`FeedActivityInput`), `top_k`.
**Output prediction** (`RankFeedPrediction`): `ranked_items[]`
(`{activity_id, user_id, activity_type, score, reason}`), `total_scored`, `diversity_applied`.

**Model**: `activity-feed-v1` / `feed-ranking-model`. Weighted blend of
recency (0.25), social-graph (0.30, followed users boosted), skill relevance
(0.25, overlap with viewer skills), engagement (0.20). A per-type cap enforces
feed diversity when the pool is large.

### POST /ml/feed/trending

**Input** (`DetectTrendingRequest`): `window_days`, `category`
(`skills|topics|languages`), `recent_activities[]`, `top_k`.
**Output prediction** (`TrendingPrediction`): `trending_items[]`
(`{item, score, velocity, category}`).

**Model**: `trending-detector-model`. Velocity-based: compares recent-half vs
early-half counts within the window.

### POST /ml/connections/suggest

**Input** (`SuggestConnectionsRequest`): `user_id`, `viewer_skills`,
`candidate_users[]` (`{user_id, username, skills[]}`), `limit`.
**Output prediction** (`SuggestConnectionsPrediction`): `suggestions[]`
(`{user_id, username, match_score, reason, shared_skills[]}`).

**Latency**: <20ms.

---

## POST /ml/problem/difficulty/estimate · /ml/problem/difficulty/calibrate (Phase 1.5)

Difficulty estimation for the judge problem bank.

### POST /ml/problem/difficulty/estimate

**Input** (`EstimateDifficultyRequest`): `title`, `description`,
`starter_code?`, `language?`, `test_cases_count?`, `constraints_count?`, `topics[]`.
**Output prediction** (`DifficultyPrediction`): `difficulty` (0-1),
`difficulty_label` (`easy|medium|hard`), `confidence`, `reasoning`, `signal_scores{}`.

**Model**: `problem-difficulty-model`. Heuristic from description length,
hard/easy keywords, test-case density, constraint count, starter complexity.

### POST /ml/problem/difficulty/calibrate

**Input** (`CalibrateDifficultyRequest`): `problem_id`, `title`,
`submission_outcomes[]` (`{passed, runtime_ms?, attempts}`), `prior_difficulty`.
**Output prediction** (`CalibratedDifficultyPrediction`): `calibrated_difficulty`,
`difficulty_label`, `confidence`, `sample_size`, `pass_rate`, `reasoning`.

**Model**: `problem-difficulty-model`. Blends prior with submission-derived
difficulty; trust grows with sample size (full trust at
`problem_difficulty.trust_full_at_n` submissions).

**Latency**: <10ms.

---

## POST /ml/learning/path · /ml/learning/next-milestone (Phase 1.5)

Personalized learning guidance built on top of the skill engine.

### POST /ml/learning/path

**Input** (`GeneratePathRequest`): `user_id`, `current_skills`,
`target_skills[]`, `time_budget_weeks?`, `max_steps`, `include_problems?`.
**Output prediction** (`LearningPathPrediction`): `steps[]`
(`{step_number, skill, current_level, target_level, difficulty, estimated_hours, reason, prerequisites[]}`),
`total_estimated_hours`, `weeks_estimate`, `prerequisites_warning?`.

**Model**: `learning-path-planner-model`. Orders skills so prerequisites
precede targets; estimates hours from current→target gap (≈12h per 0.1 skill);
`weeks_estimate` equals `time_budget_weeks` when provided, else hours/10.

### POST /ml/learning/next-milestone

**Input** (`RecommendNextMilestoneRequest`): `user_id`, `current_skills`,
`completed_milestones[]`, `candidate_skills[]`.
**Output prediction** (`MilestonePrediction`): `next_skill`, `difficulty`,
`estimated_hours`, `reason`, `readiness_score` (0-1).

**Latency**: <10ms.

---

## POST /ml/reputation/compute · /ml/reputation/activity-quality (Phase 1.5)

Explainable trust scoring for public profiles (reputation substitutes for a
self-reported resume, master prompt §13 decision-support only).

### POST /ml/reputation/compute

**Input** (`ComputeReputationRequest`): `user_id`,
`activity` (`ReputationActivitySummary`: snippets_pushed, problems_solved,
problems_attempted, followers_count, profile_completeness, avg_code_quality,
account_age_days), `verified_skills[]`.
**Output prediction** (`ReputationPrediction`): `reputation_score` (0-100),
`band` (`newcomer|contributor|trusted|elite`), `factors[]`
(`{name, contribution, detail}`), `confidence`, `verification_eligible`.

**Model**: `reputation-scorer-model`. Six transparent, bounded factors:
activity volume (25), problem-solving ratio (25), code quality (20), network
(15), profile completeness (10), verified skills (10). Every factor is
auditable in the response.

### POST /ml/reputation/activity-quality

**Input** (`ComputeActivityQualityRequest`): `activity_type`,
`code_quality_score`, `test_pass_rate`, `has_description?`, `engagement_count?`, `novelty_score?`.
**Output prediction** (`ActivityQualityPrediction`): `quality_score` (0-100),
`quality_band` (`low|fair|good|excellent`), `strengths[]`, `weaknesses[]`.

**Latency**: <10ms.
