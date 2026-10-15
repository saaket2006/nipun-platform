import io
from unittest.mock import patch, AsyncMock
import pytest

from backend.models.models import User, CandidateProfile, Resume, JobDescription, ScanResult
from backend.models.enums import UserRole, ResumeStatus
from backend.dependencies.auth_utils import get_password_hash
from backend.limiter import limiter


@pytest.fixture(autouse=True)
def disable_rate_limiting():
    """Temporarily disables SlowAPI rate limiting for unit tests."""
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture
def candidate_a(db_session):
    """Creates Candidate A in the test database."""
    user = User(
        firebase_uid="firebase_cand_a",
        email="candidate_a@example.com",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.CANDIDATE,
        profile_completed=True,
        display_name="Candidate Alpha"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = CandidateProfile(
        user_id=user.id,
        current_status="Job Seeker",
        field_of_study="Computer Science",
        current_domain="Full Stack Development"
    )
    db_session.add(profile)
    db_session.commit()
    return user


@pytest.fixture
def candidate_b(db_session):
    """Creates Candidate B in the test database for cross-user isolation tests."""
    user = User(
        firebase_uid="firebase_cand_b",
        email="candidate_b@example.com",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.CANDIDATE,
        profile_completed=True,
        display_name="Candidate Beta"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = CandidateProfile(
        user_id=user.id,
        current_status="Working Professional",
        field_of_study="Software Engineering",
        current_domain="Cloud Architecture"
    )
    db_session.add(profile)
    db_session.commit()
    return user


def test_candidate_stats_empty_dashboard(client, candidate_a):
    """Candidate with no previous analyses receives latest_ats_score: None."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": candidate_a.firebase_uid, "email": candidate_a.email}
        response = client.get(
            "/api/candidate/stats",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("latest_ats_score") is None


def test_candidate_process_resume_with_grounded_xai_and_persistence(client, db_session, candidate_a):
    """
    Candidate submitting resume and JD generates grounded XAI insights,
    persists scan and resume, and returns structured result with XAI and recommendations.
    """
    mock_gemini_xai = {
        "overall_summary": "Strong alignment with Python requirements and cloud architecture.",
        "strengths": [
            "Demonstrated 4 years of production FastAPI experience",
            "Strong background in containerized microservices"
        ],
        "skill_gaps": [
            "Lacks hands-on Kubernetes cluster orchestration experience"
        ],
        "skills_explanation": {
            "why_awarded": "Candidate has solid command of Python and FastAPI.",
            "why_deducted": "Missing Kubernetes mentioned in JD."
        },
        "experience_explanation": {
            "why_awarded": "4 years meets standard expectations.",
            "why_deducted": ""
        }
    }

    dummy_pdf_bytes = b"dummy content"
    resume_text = "John Doe\njohn@example.com\nPython, FastAPI, Docker, SQL\n4 years of experience\nBachelor of Science in Computer Science\nDeveloped REST APIs with FastAPI and Docker"

    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify, \
         patch("backend.routers.candidate.parse_document_text", return_value=resume_text), \
         patch("backend.services.pipeline.stages.extract_text", return_value=resume_text), \
         patch("backend.services.xai.gemini_explainer._call_gemini_content", new_callable=AsyncMock) as mock_gemini:

        mock_verify.return_value = {"uid": candidate_a.firebase_uid, "email": candidate_a.email}
        mock_gemini.return_value = mock_gemini_xai

        form_data = {
            "job_description": "We are seeking a Backend Engineer with strong Python, FastAPI, and Docker skills.",
            "label": "My Target SWE Resume"
        }
        files = {
            "resume": ("resume.pdf", dummy_pdf_bytes, "application/pdf")
        }

        response = client.post(
            "/api/candidate/process",
            headers={"Authorization": "Bearer valid_token"},
            data=form_data,
            files=files
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1

        cand_res = data["results"][0]
        assert cand_res["label"] == "My Target SWE Resume"
        assert cand_res["version"] == 1
        assert "similarity_score" in cand_res
        assert cand_res["similarity_score"] > 0
        assert "resume_id" in cand_res

        # Check XAI block returned
        xai = cand_res.get("xai")
        assert xai is not None
        assert xai["enabled"] is True
        assert xai["source"] == "GEMINI"
        assert xai["status"] == "SUCCESS"
        assert xai["overall_summary"] == "Strong alignment with Python requirements and cloud architecture."
        assert len(xai["strengths"]) == 2
        assert len(xai["skill_gaps"]) == 1
        assert "components" in xai
        assert "explanations" in xai

        # Check Recommendations block returned
        recs = cand_res.get("recommendations")
        assert recs is not None
        assert "list" in recs

        # Verify Database Persistence
        stored_resume = db_session.query(Resume).filter(Resume.id == cand_res["resume_id"]).first()
        assert stored_resume is not None
        assert stored_resume.candidate_id == candidate_a.id
        assert stored_resume.label == "My Target SWE Resume"
        assert stored_resume.version == 1
        assert stored_resume.status == ResumeStatus.ACTIVE

        assert len(stored_resume.scan_results) == 1
        scan = stored_resume.scan_results[0]
        assert scan.ats_score == cand_res["similarity_score"]
        assert scan.analysis_metadata.get("xai") is not None
        assert scan.analysis_metadata["xai"]["source"] == "GEMINI"


def test_candidate_dashboard_stats_and_history_lifecycle(client, db_session, candidate_a, candidate_b):
    """
    Verifies that after screening, stats and history return fresh authoritative data,
    versions are numbered and ordered, and data is strictly isolated between candidates.
    """
    dummy_pdf = b"dummy content"
    resume_text_v1 = "Python Developer with 2 years experience and Docker skills"
    resume_text_v2 = "Senior Python Developer with 5 years experience, FastAPI and Docker"
    resume_text_b = "Java Developer with Spring Boot and AWS"

    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify, \
         patch("backend.services.xai.gemini_explainer._call_gemini_content", side_effect=Exception("Gemini Offline")):

        # 1. Candidate A submits Version 1 (fallback deterministic XAI)
        mock_verify.return_value = {"uid": candidate_a.firebase_uid, "email": candidate_a.email}
        with patch("backend.routers.candidate.parse_document_text", return_value=resume_text_v1), \
             patch("backend.services.pipeline.stages.extract_text", return_value=resume_text_v1):
            r1 = client.post(
                "/api/candidate/process",
                headers={"Authorization": "Bearer valid_token"},
                data={"job_description": "Python Developer needed", "label": "V1 Draft"},
                files={"resume": ("v1.pdf", dummy_pdf, "application/pdf")}
            )
            assert r1.status_code == 200, r1.text
            data1 = r1.json()["results"][0]
            assert data1["version"] == 1
            # Deterministic fallback verified
            assert data1["xai"]["source"] == "RULE"
            assert data1["xai"]["status"] == "FALLBACK"
            assert "temporarily unavailable" in data1["xai"]["status_message"]

        # 2. Candidate A submits Version 2
        with patch("backend.routers.candidate.parse_document_text", return_value=resume_text_v2), \
             patch("backend.services.pipeline.stages.extract_text", return_value=resume_text_v2):
            r2 = client.post(
                "/api/candidate/process",
                headers={"Authorization": "Bearer valid_token"},
                data={"job_description": "Senior Python Developer needed", "label": "V2 Polished"},
                files={"resume": ("v2.pdf", dummy_pdf, "application/pdf")}
            )
            assert r2.status_code == 200, r2.text
            data2 = r2.json()["results"][0]
            assert data2["version"] == 2

        # 3. Candidate B submits Version 1
        mock_verify.return_value = {"uid": candidate_b.firebase_uid, "email": candidate_b.email}
        with patch("backend.routers.candidate.parse_document_text", return_value=resume_text_b), \
             patch("backend.services.pipeline.stages.extract_text", return_value=resume_text_b):
            rb = client.post(
                "/api/candidate/process",
                headers={"Authorization": "Bearer valid_token"},
                data={"job_description": "Java Developer", "label": "Beta Resume"},
                files={"resume": ("beta.pdf", dummy_pdf, "application/pdf")}
            )
            assert rb.status_code == 200, rb.text
            assert rb.json()["results"][0]["version"] == 1

        # 4. Check Candidate A stats
        mock_verify.return_value = {"uid": candidate_a.firebase_uid, "email": candidate_a.email}
        stats_a = client.get("/api/candidate/stats", headers={"Authorization": "Bearer valid_token"}).json()
        assert stats_a["latest_ats_score"] == data2["similarity_score"]
        assert "last_analysis_date" in stats_a

        # 5. Check Candidate A history list (must show V2 then V1, NOT Candidate B's resume)
        history_a = client.get("/api/candidate/resumes", headers={"Authorization": "Bearer valid_token"}).json()
        assert len(history_a) == 2
        assert history_a[0]["version"] == 2
        assert history_a[0]["label"] == "V2 Polished"
        assert history_a[1]["version"] == 1
        assert history_a[1]["label"] == "V1 Draft"

        # 6. Check Candidate B history list (must only show 1 resume)
        mock_verify.return_value = {"uid": candidate_b.firebase_uid, "email": candidate_b.email}
        history_b = client.get("/api/candidate/resumes", headers={"Authorization": "Bearer valid_token"}).json()
        assert len(history_b) == 1
        assert history_b[0]["label"] == "Beta Resume"

        # 7. Candidate B attempts to view Candidate A's resume details -> 404 forbidden/not found
        v2_id = data2["resume_id"]
        detail_unauth = client.get(f"/api/candidate/resumes/{v2_id}", headers={"Authorization": "Bearer valid_token"})
        assert detail_unauth.status_code == 404

        # 8. Candidate A views their own resume details -> 200 with XAI and recommendations
        mock_verify.return_value = {"uid": candidate_a.firebase_uid, "email": candidate_a.email}
        detail_auth = client.get(f"/api/candidate/resumes/{v2_id}", headers={"Authorization": "Bearer valid_token"})
        assert detail_auth.status_code == 200
        detail_json = detail_auth.json()
        assert detail_json["id"] == v2_id
        assert detail_json["xai"] is not None
        assert detail_json["recommendations"] is not None

        # 9. Candidate A renames label
        rename_res = client.put(
            f"/api/candidate/resumes/{v2_id}/label",
            headers={"Authorization": "Bearer valid_token"},
            json={"label": "V2 Production Ready"}
        )
        assert rename_res.status_code == 200
        assert rename_res.json()["label"] == "V2 Production Ready"

        # 10. Candidate A deletes V2
        del_res = client.delete(f"/api/candidate/resumes/{v2_id}", headers={"Authorization": "Bearer valid_token"})
        assert del_res.status_code == 200

        # History now only has V1
        history_after_del = client.get("/api/candidate/resumes", headers={"Authorization": "Bearer valid_token"}).json()
        assert len(history_after_del) == 1
        assert history_after_del[0]["version"] == 1


def test_candidate_job_description_title_non_truncation_and_legacy_healing(client, candidate_a, db_session):
    """
    Verify that candidate JD titles are not unnecessarily truncated to 50 characters,
    and legacy truncated titles ending with '...' are healed from description in resume details.
    """
    long_title = "Senior Full Stack Python Developer with React, FastAPI, Docker, and Cloud Native Architecture Experience"
    full_jd = f"{long_title}\n\nWe are looking for a senior developer with extensive Python and React expertise."

    resume_content = b"%PDF-1.4 Fake PDF Content for Full Stack Developer with Python, FastAPI, Docker, React."

    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify, \
         patch("backend.routers.candidate.parse_document_text", return_value="Skills: Python, FastAPI, React\nCandidate Alpha\ncandidate_a@example.com"), \
         patch("backend.services.pipeline.stages.extract_text", return_value="Skills: Python, FastAPI, React\nCandidate Alpha\ncandidate_a@example.com"):

        mock_verify.return_value = {"uid": candidate_a.firebase_uid, "email": candidate_a.email}

        files = {"resume": ("resume_full.pdf", io.BytesIO(resume_content), "application/pdf")}
        data = {"job_description": full_jd, "label": "Full JD Test"}

        res = client.post("/api/candidate/process", headers={"Authorization": "Bearer valid_token"}, data=data, files=files)
        assert res.status_code == 200, res.text
        res_data = res.json()
        assert "results" in res_data and len(res_data["results"]) > 0
        resume_id = res_data["results"][0]["resume_id"]

        # Fetch details: verify title preserved the full first line (well over 50 chars) without truncation
        detail_res = client.get(f"/api/candidate/resumes/{resume_id}", headers={"Authorization": "Bearer valid_token"})
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["job_description"]["title"] == long_title
        assert len(detail["job_description"]["title"]) > 50

        # Simulate legacy truncated record in DB: title ends with '...'
        scan = db_session.query(ScanResult).filter(ScanResult.resume_id == resume_id).first()
        assert scan is not None
        assert scan.job_description is not None
        legacy_truncated = long_title[:50] + "..."
        scan.job_description.title = legacy_truncated
        db_session.commit()

        # Fetch details again: verify healed title restored from description
        healed_res = client.get(f"/api/candidate/resumes/{resume_id}", headers={"Authorization": "Bearer valid_token"})
        assert healed_res.status_code == 200
        healed_detail = healed_res.json()
        assert healed_detail["job_description"]["title"] == long_title
        assert not healed_detail["job_description"]["title"].endswith("...")

