"""
Backend end-to-end tests for the SkillGraph assessment flow.

Tests the full flow: login → list assessments → start attempt → fetch questions
→ submit answers → get scored results, without needing a running server.

Uses FastAPI's TestClient against the app directly.
"""
from __future__ import annotations

import json
import os

# Force a test database before importing app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_skillgraph.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing")
os.environ.setdefault("ML_GATEWAY_URL", "http://localhost:8000")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def auth_token(client):
    """Log in as the seeded candidate."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "candidate@skillgraph.dev", "password": "candidate123"},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    return data["access_token"], data


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    token, _ = auth_token
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


class TestAuth:
    def test_login_candidate(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"email": "candidate@skillgraph.dev", "password": "candidate123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "candidate"
        assert data["email"] == "candidate@skillgraph.dev"
        assert data["access_token"]

    def test_login_trainer(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"email": "trainer@techcorp.io", "password": "trainer123"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "trainer"

    def test_login_admin(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"email": "admin@techcorp.io", "password": "admin123"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

    def test_login_wrong_password(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"email": "candidate@skillgraph.dev", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_login_missing_email(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"password": "candidate123"},
        )
        assert resp.status_code == 422

    def test_get_me(self, client, auth_headers):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "candidate@skillgraph.dev"

    def test_get_roles(self, client):
        resp = client.get("/api/auth/roles")
        assert resp.status_code == 200
        data = resp.json()
        role_ids = [r["id"] for r in data["roles"]]
        assert "candidate" in role_ids
        assert "trainer" in role_ids
        assert "admin" in role_ids

    def test_protected_route_requires_auth(self, client):
        resp = client.get("/api/assessments/")
        assert resp.status_code == 401


class TestAssessments:
    def test_list_assessments(self, client, auth_headers):
        resp = client.get("/api/assessments/", headers=auth_headers)
        assert resp.status_code == 200
        assessments = resp.json()
        assert len(assessments) >= 1
        a = assessments[0]
        assert "id" in a
        assert "title" in a
        assert "skills" in a
        assert "duration_minutes" in a

    def test_get_assessment(self, client, auth_headers):
        resp = client.get("/api/assessments/", headers=auth_headers)
        assessments = resp.json()
        aid = assessments[0]["id"]

        resp2 = client.get(f"/api/assessments/{aid}", headers=auth_headers)
        assert resp2.status_code == 200
        a = resp2.json()
        assert a["id"] == aid
        assert a["is_active"] is True

    def test_assessment_not_found(self, client, auth_headers):
        resp = client.get("/api/assessments/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestAssessmentFlow:
    @pytest.fixture(scope="class")
    def assessment(self, client, auth_headers):
        resp = client.get("/api/assessments/", headers=auth_headers)
        return resp.json()[0]

    def test_start_assessment(self, client, auth_headers, assessment):
        resp = client.post(
            f"/api/assessments/{assessment['id']}/start",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "attempt_id" in data
        assert data["assessment_id"] == assessment["id"]
        assert data["duration_minutes"] == assessment["duration_minutes"]

    def test_get_questions(self, client, auth_headers, assessment):
        # Start first
        start = client.post(
            f"/api/assessments/{assessment['id']}/start",
            headers=auth_headers,
        ).json()
        attempt_id = start["attempt_id"]

        resp = client.get(
            f"/api/assessments/{assessment['id']}/questions?attempt_id={attempt_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["attempt_id"] == attempt_id
        assert len(data["questions"]) >= 5
        q = data["questions"][0]
        assert "prompt" in q
        assert "question_type" in q
        assert "options" in q or "starter_code" in q  # type-appropriate fields


class TestAttemptSubmission:
    @pytest.fixture(scope="class")
    def started_attempt(self, client, auth_headers):
        resp = client.get("/api/assessments/", headers=auth_headers)
        aid = resp.json()[0]["id"]
        start = client.post(
            f"/api/assessments/{aid}/start",
            headers=auth_headers,
        ).json()
        return start["attempt_id"], aid

    def test_submit_and_score(self, client, auth_headers, started_attempt):
        attempt_id, assessment_id = started_attempt

        # Get questions to know correct answers
        resp = client.get(
            f"/api/assessments/{assessment_id}/questions?attempt_id={attempt_id}",
            headers=auth_headers,
        )
        questions = resp.json()["questions"]

        # Build answers: for MCQ, pick first option; for others, empty/starter
        answers = []
        for q in questions:
            ans = {
                "question_id": q["id"],
                "question_type": q["question_type"],
                "time_spent_seconds": 30,
                "compiled": True,
            }
            if q["question_type"] in ("mcq", "multi_select"):
                ans["submitted_options"] = [0]
            elif q["question_type"] in ("coding", "sql"):
                ans["submitted_code"] = q.get("starter_code") or ""
            else:
                ans["submitted_answer"] = ""
            answers.append(ans)

        resp = client.post(
            f"/api/attempts/{attempt_id}/submit",
            headers=auth_headers,
            json={"answers": answers},
        )
        assert resp.status_code == 200
        result = resp.json()
        assert "overall_score" in result
        assert "raw_score" in result
        assert "ml_score" in result
        assert "dimension_scores" in result
        assert "skills" in result
        assert "evidence" in result
        assert result["questions_count"] == len(questions)

    def test_get_attempt_result(self, client, auth_headers, started_attempt):
        attempt_id, assessment_id = started_attempt
        resp = client.get(f"/api/attempts/{attempt_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "graded"
        assert data["overall_score"] >= 0
        assert data["overall_score"] <= 100


class TestSkills:
    def test_get_my_skills(self, client, auth_headers):
        resp = client.get("/api/skills/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "user_id" in data
        assert "skills" in data
        assert isinstance(data["skills"], dict)

    def test_list_all_skills(self, client, auth_headers):
        resp = client.get("/api/skills/", headers=auth_headers)
        assert resp.status_code == 200
        skills = resp.json()
        assert isinstance(skills, list)
        assert len(skills) >= 1


class TestRBAC:
    def test_candidate_cannot_create_assessment(self, client, auth_headers):
        """A candidate (authenticated) should not be able to create assessments."""
        resp = client.post(
            "/api/assessments/",
            headers=auth_headers,
            json={
                "title": "Hack",
                "description": "Should fail",
                "duration_minutes": 60,
                "total_questions": 10,
                "skills": ["Test"],
            },
        )
        assert resp.status_code in (403, 405)

    def test_trainer_can_create_assessment(self, client):
        """Trainer should be able to create an assessment."""
        resp = client.post(
            "/api/auth/login",
            json={"email": "trainer@techcorp.io", "password": "trainer123"},
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        resp = client.post(
            "/api/assessments/",
            headers=headers,
            json={
                "title": "Trainer Created Test",
                "description": "Test",
                "duration_minutes": 30,
                "total_questions": 5,
                "skills": ["Python"],
                "allowed_question_types": ["mcq"],
                "coding_languages": [],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Trainer Created Test"


class TestMLGatewayIntegration:
    def test_ml_gateway_health(self):
        """The ML gateway on port 8000 should be reachable."""
        import httpx
        try:
            resp = httpx.get("http://localhost:8000/health", timeout=5)
            assert resp.status_code == 200
            assert resp.json()["status"] == "ok"
        except Exception:
            pytest.skip("ML Gateway not running on port 8000")

    def test_scoring_uses_ml_or_fallback(self, client, auth_headers):
        """Scoring should succeed regardless of ML gateway availability (local fallback)."""
        resp = client.get("/api/assessments/", headers=auth_headers)
        assessments = resp.json()
        aid = assessments[0]["id"]

        start = client.post(
            f"/api/assessments/{aid}/start", headers=auth_headers
        ).json()
        attempt_id = start["attempt_id"]

        questions = client.get(
            f"/api/assessments/{aid}/questions?attempt_id={attempt_id}",
            headers=auth_headers,
        ).json()["questions"]

        answers = []
        for q in questions:
            ans = {
                "question_id": q["id"],
                "question_type": q["question_type"],
                "time_spent_seconds": 15,
                "compiled": True,
            }
            if q["question_type"] in ("mcq", "multi_select"):
                ans["submitted_options"] = [0] if q["options"] else []
            elif q["question_type"] in ("coding", "sql"):
                ans["submitted_code"] = q.get("starter_code") or ""
            else:
                ans["submitted_answer"] = "N/A"
            answers.append(ans)

        result = client.post(
            f"/api/attempts/{attempt_id}/submit",
            headers=auth_headers,
            json={"answers": answers},
        ).json()

        # At minimum, the scorecard must return an overall score
        assert 0 <= result["overall_score"] <= 100
        assert "skills" in result
        # dimension_scores should be a dict (possibly from ML or local fallback)
        assert isinstance(result["dimension_scores"], dict)
        # The scoring pipeline must produce some skill estimates or evidence
        assert isinstance(result.get("evidence", []), list)
