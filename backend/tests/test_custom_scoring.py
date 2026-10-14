import io
import docx
import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.orm import Session
from starlette.requests import Request
from fastapi import HTTPException

from backend.services.policy.scoring_profile_policy import (
    default_scoring_profile_policy,
    validate_and_normalize_scoring_config
)
from backend.services.policy.scoring_policy import default_scoring_policy
from backend.models.models import User, ScoringProfile, ScreeningTask
from backend.routers.recruiter import process_resumes
from backend.services.pipeline import AnalysisPipeline, AnalysisContext


def create_docx_bytes(paragraphs: list[str]) -> bytes:
    doc = docx.Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()


# =====================================================================
# Unit Tests for validate_and_normalize_scoring_config
# =====================================================================

def test_validation_returns_none_when_omitted_or_disabled():
    assert validate_and_normalize_scoring_config(None) is None
    assert validate_and_normalize_scoring_config("") is None
    assert validate_and_normalize_scoring_config("   ") is None
    assert validate_and_normalize_scoring_config("null") is None
    assert validate_and_normalize_scoring_config({"enabled": False}) is None
    assert validate_and_normalize_scoring_config(json.dumps({"enabled": False})) is None


def test_validation_rejects_invalid_json():
    with pytest.raises(ValueError, match="Invalid JSON format"):
        validate_and_normalize_scoring_config("{not-json}")


def test_validation_rejects_missing_weights():
    with pytest.raises(ValueError, match="must include a 'weights' object"):
        validate_and_normalize_scoring_config({"enabled": True})


def test_validation_rejects_negative_weights():
    config = {
        "enabled": True,
        "weights": {"skills": -0.1, "experience": 0.5, "education": 0.3, "projects": 0.3}
    }
    with pytest.raises(ValueError, match="cannot be negative"):
        validate_and_normalize_scoring_config(config)


def test_validation_rejects_all_zero_or_disabled_weights():
    config = {
        "enabled": True,
        "weights": {"skills": 0, "experience": 0, "education": 0, "projects": 0}
    }
    with pytest.raises(ValueError, match="must be enabled with a positive weight"):
        validate_and_normalize_scoring_config(config)

    config_all_disabled = {
        "enabled": True,
        "weights": {"skills": 0.5, "experience": 0.5},
        "disabled_criteria": ["skills", "experience", "education", "projects"]
    }
    with pytest.raises(ValueError, match="must be enabled with a positive weight"):
        validate_and_normalize_scoring_config(config_all_disabled)


def test_validation_rejects_out_of_bounds_thresholds():
    # Experience years < 1 or > 30
    with pytest.raises(ValueError, match="Target experience years must be between 1 and 30"):
        validate_and_normalize_scoring_config({
            "enabled": True,
            "weights": {"skills": 0.5, "experience": 0.5, "education": 0.0, "projects": 0.0},
            "thresholds": {"target_experience_years": 0.5}
        })

    with pytest.raises(ValueError, match="Target experience years must be between 1 and 30"):
        validate_and_normalize_scoring_config({
            "enabled": True,
            "weights": {"skills": 0.5, "experience": 0.5, "education": 0.0, "projects": 0.0},
            "thresholds": {"target_experience_years": 35}
        })

    # Projects count < 1 or > 10
    with pytest.raises(ValueError, match="Target project count must be between 1 and 10"):
        validate_and_normalize_scoring_config({
            "enabled": True,
            "weights": {"skills": 0.5, "experience": 0.5, "education": 0.0, "projects": 0.0},
            "thresholds": {"target_project_count": 0}
        })

    with pytest.raises(ValueError, match="Target project count must be between 1 and 10"):
        validate_and_normalize_scoring_config({
            "enabled": True,
            "weights": {"skills": 0.5, "experience": 0.5, "education": 0.0, "projects": 0.0},
            "thresholds": {"target_project_count": 15}
        })


def test_validation_normalizes_percentages_to_decimal_sum_one():
    config = {
        "enabled": True,
        "weights": {"skills": 40, "experience": 30, "education": 20, "projects": 10},
        "thresholds": {"target_experience_years": 5, "target_project_count": 4}
    }
    res = validate_and_normalize_scoring_config(config)
    assert res is not None
    assert res["enabled"] is True
    weights = res["weights"]
    assert weights["skills"] == 0.4
    assert weights["experience"] == 0.3
    assert weights["education"] == 0.2
    assert weights["projects"] == 0.1
    assert round(sum(weights.values()), 4) == 1.0
    assert res["thresholds"]["target_experience_years"] == 5.0
    assert res["thresholds"]["target_project_count"] == 4


def test_validation_redistributes_when_criterion_is_disabled():
    # If projects is disabled, remaining weights (skills: 50, exp: 25, edu: 25) rebalance to sum to 1.0
    config = {
        "enabled": True,
        "weights": {"skills": 0.50, "experience": 0.25, "education": 0.25, "projects": 0.10},
        "disabled_criteria": ["projects"]
    }
    res = validate_and_normalize_scoring_config(config)
    assert res is not None
    weights = res["weights"]
    assert weights["projects"] == 0.0
    assert round(sum(weights.values()), 4) == 1.0
    assert weights["skills"] == 0.50
    assert weights["experience"] == 0.25
    assert weights["education"] == 0.25


# =====================================================================
# Pipeline & Scoring Engine Integration Tests
# =====================================================================

@pytest.mark.anyio
async def test_pipeline_default_scoring_run_preserves_baseline():
    """Verify that running pipeline without custom scoring uses default policy weights & thresholds."""
    pipeline = AnalysisPipeline()
    context = AnalysisContext(request_id="req-default")

    resume_bytes = create_docx_bytes([
        "Alice Smith",
        "alice@example.com",
        "5 years of experience in Python and FastAPI.",
        "Education: Master in Computer Science.",
        "Projects",
        "Built distributed cache system, automated test suite, data pipeline."
    ])

    event = await pipeline.run_analysis(
        filename="alice_resume.docx",
        content_bytes=resume_bytes,
        job_description="Looking for Python, FastAPI, and data pipeline skills.",
        clean_jd="looking for python fastapi and data pipeline skills",
        context=context
    )

    assert event.status == "success"
    scoring = event.explanation.scoring
    meta = event.explanation.analysis_metadata

    assert meta["is_custom_scoring"] is False
    assert meta["component_weights"] == default_scoring_profile_policy.default_weights
    assert scoring.similarity_score > 0


@pytest.mark.anyio
async def test_pipeline_custom_weights_affects_score_calculation():
    """Verify that custom weights directly alter similarity score and component contributions."""
    pipeline = AnalysisPipeline()

    resume_bytes = create_docx_bytes([
        "Bob Builder",
        "bob@example.com",
        "10 years of experience in Python.",
        "Education: Bachelor in Computer Science.",
        "Maintained core server backend."
    ])

    # Run 1: High Experience Weight (70%), Low Skills Weight (10%)
    custom_exp_heavy = {
        "enabled": True,
        "weights": {"skills": 0.10, "experience": 0.70, "education": 0.10, "projects": 0.10},
        "thresholds": {"target_experience_years": 10.0, "target_project_count": 3}
    }
    ctx_exp = AnalysisContext(request_id="req-exp", configuration={"custom_scoring": custom_exp_heavy})
    event_exp = await pipeline.run_analysis(
        filename="bob.docx",
        content_bytes=resume_bytes,
        job_description="Seeking Python and Go developer.",
        clean_jd="seeking python and go developer",
        context=ctx_exp
    )

    # Run 2: High Projects Weight (70%), Low Experience Weight (10%)
    custom_proj_heavy = {
        "enabled": True,
        "weights": {"skills": 0.10, "experience": 0.10, "education": 0.10, "projects": 0.70},
        "thresholds": {"target_experience_years": 10.0, "target_project_count": 3}
    }
    ctx_proj = AnalysisContext(request_id="req-proj", configuration={"custom_scoring": custom_proj_heavy})
    event_proj = await pipeline.run_analysis(
        filename="bob.docx",
        content_bytes=resume_bytes,
        job_description="Seeking Python and Go developer.",
        clean_jd="seeking python and go developer",
        context=ctx_proj
    )

    score_exp_heavy = event_exp.explanation.scoring.similarity_score
    score_proj_heavy = event_proj.explanation.scoring.similarity_score

    # Bob has 10 years experience (100% exp score) but 0 projects (0% project score).
    # Thus score_exp_heavy MUST be significantly higher than score_proj_heavy.
    assert score_exp_heavy > score_proj_heavy
    assert event_exp.explanation.analysis_metadata["is_custom_scoring"] is True
    assert event_exp.explanation.analysis_metadata["component_weights"]["experience"] == 0.70


@pytest.mark.anyio
async def test_pipeline_custom_thresholds_scaling():
    """Verify target_experience_years and target_project_count scale component scores."""
    pipeline = AnalysisPipeline()

    resume_bytes = create_docx_bytes([
        "Carol Dev",
        "carol@example.com",
        "3 years of experience in Python.",
        "Education: Bachelor in Computer Science.",
        "Projects",
        "Built single web app."
    ])

    # With default target of 10 years experience, 3 years experience gives 30% experience score
    ctx_default = AnalysisContext(request_id="req-thresh-def")
    event_def = await pipeline.run_analysis(
        filename="carol.docx",
        content_bytes=resume_bytes,
        job_description="Looking for Python developer.",
        clean_jd="looking for python developer",
        context=ctx_default
    )

    # With custom target of 3 years experience, 3 years experience gives 100% experience score
    custom_thresh = {
        "enabled": True,
        "weights": {"skills": 0.50, "experience": 0.25, "education": 0.15, "projects": 0.10},
        "thresholds": {"target_experience_years": 3.0, "target_project_count": 1}
    }
    ctx_custom = AnalysisContext(request_id="req-thresh-cust", configuration={"custom_scoring": custom_thresh})
    event_cust = await pipeline.run_analysis(
        filename="carol.docx",
        content_bytes=resume_bytes,
        job_description="Looking for Python developer.",
        clean_jd="looking for python developer",
        context=ctx_custom
    )

    exp_score_def = event_def.explanation.scoring.experience_score
    exp_score_cust = event_cust.explanation.scoring.experience_score

    assert exp_score_def == 30.0
    assert exp_score_cust == 100.0


# =====================================================================
# Isolation & DB Integrity Tests (No Mutation of Stored Profiles)
# =====================================================================

@pytest.mark.anyio
async def test_consecutive_runs_isolation_and_no_profile_mutation():
    """Verify custom settings do not mutate stored DB profile or leak to subsequent runs."""
    mock_db = MagicMock(spec=Session)

    stored_profile = ScoringProfile(
        id=5,
        name="Backend Developer",
        weights={"skills": 0.45, "experience": 0.30, "education": 0.10, "projects": 0.15},
        is_default=False
    )
    mock_db.query.return_value.filter.return_value.first.return_value = stored_profile

    # Run 1: Custom configuration with 80% skills
    custom_config = {
        "enabled": True,
        "weights": {"skills": 0.80, "experience": 0.10, "education": 0.05, "projects": 0.05},
        "thresholds": {"target_experience_years": 8.0, "target_project_count": 2}
    }
    pipeline = AnalysisPipeline()
    ctx1 = AnalysisContext(request_id="run-1", profile_id=5, configuration={"custom_scoring": custom_config})
    res1 = await pipeline.run_analysis(
        filename="cand1.docx",
        content_bytes=create_docx_bytes(["Dave Smith", "dave@example.com", "Python developer."]),
        job_description="Python",
        clean_jd="python",
        db=mock_db,
        context=ctx1
    )

    # Verify run 1 used custom weights
    assert res1.explanation.analysis_metadata["component_weights"]["skills"] == 0.80

    # Stored profile in DB MUST NOT be mutated!
    assert stored_profile.weights["skills"] == 0.45

    # Run 2: Next screening run with default settings (no custom configuration)
    ctx2 = AnalysisContext(request_id="run-2", profile_id=5, configuration={})
    res2 = await pipeline.run_analysis(
        filename="cand2.docx",
        content_bytes=create_docx_bytes(["Eve Jones", "eve@example.com", "Python developer."]),
        job_description="Python",
        clean_jd="python",
        db=mock_db,
        context=ctx2
    )

    # Verify run 2 reverted cleanly to original Backend Developer profile weights
    assert res2.explanation.analysis_metadata["is_custom_scoring"] is False
    assert res2.explanation.analysis_metadata["component_weights"]["skills"] == 0.45


# =====================================================================
# Recruiter Process Endpoint Validation Tests
# =====================================================================

@pytest.mark.anyio
async def test_process_resumes_rejects_invalid_custom_scoring():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.email = "recruiter@example.com"

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/recruiter/process",
        "headers": [],
        "client": ("127.0.0.1", 12345)
    }
    req = Request(scope)

    invalid_config = json.dumps({
        "enabled": True,
        "weights": {"skills": -0.5}  # Negative weight!
    })

    with pytest.raises(HTTPException) as exc_info:
        await process_resumes(
            request=req,
            job_description="Senior Developer",
            custom_scoring_config=invalid_config,
            resumes=[],
            current_user=mock_user,
            db=mock_db
        )
    assert exc_info.value.status_code == 400
    assert "cannot be negative" in exc_info.value.detail
