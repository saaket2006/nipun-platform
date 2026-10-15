import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock
from backend.services.xai.gemini_explainer import (
    generate_grounded_xai_insights,
    _safe_parse_json,
    _build_deterministic_fallback,
    ORDERED_GEMINI_MODELS
)

def test_safe_parse_json_variants():
    # Plain JSON
    assert _safe_parse_json('{"overall_summary": "Good fit"}') == {"overall_summary": "Good fit"}
    # Markdown json codefence
    assert _safe_parse_json('```json\n{"overall_summary": "Good fit"}\n```') == {"overall_summary": "Good fit"}
    # Plain codefence
    assert _safe_parse_json('```\n{"overall_summary": "Good fit"}\n```') == {"overall_summary": "Good fit"}
    # Surrounding conversational text
    assert _safe_parse_json('Here is your evaluation: {"overall_summary": "Good fit"} Hope this helps!') == {"overall_summary": "Good fit"}
    # Empty or invalid
    assert _safe_parse_json('') is None
    assert _safe_parse_json('Not a json at all') is None


@pytest.mark.anyio
async def test_no_api_key_deterministic_fallback():
    candidate_dict = {
        "name": "Jane Doe",
        "experience": 4,
        "similarity_score": 82.5,
        "matched_skills": ["Python", "FastAPI", "Docker"],
        "missing_skills": ["Kubernetes"],
        "projects": 3
    }
    result = await generate_grounded_xai_insights(
        candidate_dict=candidate_dict,
        job_description="Need FastAPI and Docker developer",
        resume_text="Senior Python and FastAPI engineer with Docker experience",
        score_components=[],
        api_key=""
    )
    assert result["source"] == "RULE"
    assert result["status"] == "FALLBACK"
    assert result["model"] is None
    assert "temporarily unavailable" in result["status_message"] or "not configured" in result["status_message"]
    assert "82.5%" in result["overall_summary"]
    assert len(result["strengths"]) > 0
    assert any("Python" in s or "FastAPI" in s for s in result["strengths"])
    assert len(result["skill_gaps"]) > 0
    assert any("Kubernetes" in g for g in result["skill_gaps"])


@pytest.mark.anyio
async def test_successful_gemini_call():
    mock_payload = {
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

    candidate_dict = {
        "name": "John Smith",
        "experience": 4,
        "similarity_score": 85.0,
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": ["Kubernetes"]
    }

    with patch("backend.services.xai.gemini_explainer._call_gemini_content", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_payload
        result = await generate_grounded_xai_insights(
            candidate_dict=candidate_dict,
            job_description="Looking for Python backend lead",
            resume_text="Experienced Python developer",
            score_components=[],
            api_key="test_dummy_key"
        )

        assert result["source"] == "GEMINI"
        assert result["status"] == "SUCCESS"
        assert result["model"] == ORDERED_GEMINI_MODELS[0]
        assert result["status_message"] is None
        assert result["overall_summary"] == "Strong alignment with Python requirements and cloud architecture."
        assert len(result["strengths"]) == 2
        assert len(result["skill_gaps"]) == 1
        assert "skills" in result["component_explanations"]


@pytest.mark.anyio
async def test_gemini_model_fallback_on_429_quota():
    """When the first model hits 429 quota, fallback model succeeds."""
    candidate_dict = {
        "name": "Alex",
        "experience": 2,
        "similarity_score": 70.0,
        "matched_skills": ["React"],
        "missing_skills": ["TypeScript"]
    }

    call_count = 0
    async def mock_call_impl(prompt, key, model_name):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            req = httpx.Request("POST", "https://api.example.com")
            res = httpx.Response(status_code=429, request=req)
            raise httpx.HTTPStatusError("Quota exceeded", request=req, response=res)
        return {
            "overall_summary": "Recovered with fallback model.",
            "strengths": ["React familiarity"],
            "skill_gaps": ["TypeScript gap"]
        }

    with patch("backend.services.xai.gemini_explainer._call_gemini_content", side_effect=mock_call_impl):
        result = await generate_grounded_xai_insights(
            candidate_dict=candidate_dict,
            job_description="Frontend dev",
            resume_text="React dev",
            score_components=[],
            api_key="test_dummy_key"
        )

        assert result["source"] == "GEMINI"
        assert result["status"] == "SUCCESS"
        assert result["overall_summary"] == "Recovered with fallback model."
        assert call_count == 2


@pytest.mark.anyio
async def test_gemini_all_models_fail_graceful_deterministic_fallback():
    """When all models fail (e.g. network timeout or persistent 503), returns deterministic fallback with reason."""
    candidate_dict = {
        "name": "Jordan",
        "experience": 3,
        "similarity_score": 75.0,
        "matched_skills": ["SQL"],
        "missing_skills": ["PostgreSQL"]
    }

    with patch("backend.services.xai.gemini_explainer._call_gemini_content", side_effect=httpx.ConnectTimeout("Timeout")):
        result = await generate_grounded_xai_insights(
            candidate_dict=candidate_dict,
            job_description="Database engineer",
            resume_text="SQL engineer",
            score_components=[],
            api_key="test_dummy_key"
        )

        assert result["source"] == "RULE"
        assert result["status"] == "FALLBACK"
        assert result["model"] is None
        assert "temporarily unavailable" in result["status_message"]
        assert "75.0%" in result["overall_summary"]
        assert len(result["strengths"]) > 0
        assert len(result["skill_gaps"]) > 0
