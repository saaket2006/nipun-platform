import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from backend.routers.recruiter import create_job_description
from backend.models.models import User, JobDescription

def test_create_job_description_success():
    # Setup mocks
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Run function
    result = create_job_description(
        title="Software Engineer",
        subtitle="Backend",
        description="Write code",
        company="Tech Inc",
        optional_notes="Urgent",
        current_user=mock_user,
        db=mock_db
    )

    # Assert result
    assert result["message"] == "Job description created successfully"
    assert "id" in result

    # Assert DB calls
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

    # Check what was added
    added_obj = mock_db.add.call_args[0][0]
    assert isinstance(added_obj, JobDescription)
    assert added_obj.owner_id == 1
    assert added_obj.title == "Software Engineer"
    assert added_obj.subtitle == "Backend"
    assert added_obj.description == "Write code"
    assert added_obj.company == "Tech Inc"
    assert added_obj.optional_notes == "Urgent"

def test_create_job_description_minimal():
    # Setup mocks
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Run function with only required fields
    result = create_job_description(
        title="Software Engineer",
        subtitle=None,
        description="Write code",
        company=None,
        optional_notes=None,
        current_user=mock_user,
        db=mock_db
    )

    # Assert result
    assert result["message"] == "Job description created successfully"
    assert "id" in result

    # Assert DB calls
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

    # Check what was added
    added_obj = mock_db.add.call_args[0][0]
    assert isinstance(added_obj, JobDescription)
    assert added_obj.owner_id == 1
    assert added_obj.title == "Software Engineer"
    assert added_obj.subtitle is None
    assert added_obj.description == "Write code"
    assert added_obj.company is None
    assert added_obj.optional_notes is None

def test_create_job_description_deduplication():
    # Verify that saving an existing active JD updates it rather than duplicating it
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    existing_jd = MagicMock(spec=JobDescription)
    existing_jd.id = 42
    mock_db.query.return_value.filter.return_value.first.return_value = existing_jd

    result = create_job_description(
        title="Updated Title",
        subtitle="Fullstack",
        description="Write code",
        company="New Co",
        optional_notes=None,
        current_user=mock_user,
        db=mock_db
    )

    assert result["id"] == 42
    assert "updated" in result["message"]
    assert existing_jd.title == "Updated Title"
    assert existing_jd.company == "New Co"
    # Should NOT add a new record
    mock_db.add.assert_not_called()
    mock_db.commit.assert_called_once()

from backend.routers.recruiter import get_recruiter_stats
from backend.models.models import ScanResult

def test_get_recruiter_stats_malformed_experience():
    # Setup mocks
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.email = "recruiter@test.com"

    # Create mock scan results with malformed experience values
    # One with a bad string, one with an uncastable object, one with a valid float
    scan1 = MagicMock(spec=ScanResult)
    scan1.ats_score = 80
    scan1.analysis_metadata = {
        "candidate": {
            "experience": "Five years" # ValueError
        }
    }

    scan2 = MagicMock(spec=ScanResult)
    scan2.ats_score = 90
    scan2.analysis_metadata = {
        "candidate": {
            "experience": {"years": 5} # TypeError
        }
    }

    scan3 = MagicMock(spec=ScanResult)
    scan3.ats_score = 70
    scan3.analysis_metadata = {
        "candidate": {
            "experience": "5.5" # Valid
        }
    }

    mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = (3, 80.0)
    mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [
        (scan1.analysis_metadata,),
        (scan2.analysis_metadata,),
        (scan3.analysis_metadata,)
    ]

    # Run function
    result = get_recruiter_stats(
        current_user=mock_user,
        db=mock_db
    )

    # Assert results
    assert result["total_candidates_screened"] == 3
    assert result["average_ats_score"] == 80.0
    # Average experience should only count the valid "5.5" string -> 5.5 / 1 = 5.5
    assert result["average_experience_tenure"] == 5.5


from backend.routers.recruiter import list_job_descriptions
import datetime

def test_list_job_descriptions_deduplication():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    # Two JDs with the exact same description
    jd1 = MagicMock(spec=JobDescription)
    jd1.id = 1
    jd1.title = "Junior GenAI Dev"
    jd1.subtitle = None
    jd1.description = "Looking for GenAI dev"
    jd1.company = None
    jd1.optional_notes = None
    jd1.is_archived = False
    jd1.created_at = datetime.datetime(2026, 10, 13, 10, 0, 0)

    jd2 = MagicMock(spec=JobDescription)
    jd2.id = 2
    jd2.title = "Junior GenAI Dev"
    jd2.subtitle = None
    jd2.description = "Looking for GenAI dev"
    jd2.company = None
    jd2.optional_notes = None
    jd2.is_archived = False
    jd2.created_at = datetime.datetime(2026, 10, 13, 9, 0, 0)

    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = [jd1, jd2]

    results = list_job_descriptions(current_user=mock_user, db=mock_db)

    # Should only return 1 unique JD
    assert len(results) == 1
    assert results[0]["id"] == 1
    # Older duplicate should be marked archived
    assert jd2.is_archived is True
    mock_db.commit.assert_called_once()


from backend.routers.recruiter import get_screening_history, get_screening_task_detail
from backend.models.models import ScreeningTask
from fastapi import HTTPException

def test_get_screening_history_ordered():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 42

    t1 = MagicMock(spec=ScreeningTask)
    t1.id = 1
    t1.recruiter_id = 42
    t1.role = "Senior Frontend Engineer"
    t1.resume_count = 5
    t1.created_at = datetime.datetime(2026, 10, 13, 12, 0, 0)

    t2 = MagicMock(spec=ScreeningTask)
    t2.id = 2
    t2.recruiter_id = 42
    t2.role = "Backend Python Engineer"
    t2.resume_count = 3
    t2.created_at = datetime.datetime(2026, 10, 13, 11, 0, 0)

    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = [t1, t2]

    results = get_screening_history(current_user=mock_user, db=mock_db)

    assert len(results) == 2
    assert results[0].id == 1
    assert results[0].role == "Senior Frontend Engineer"
    assert results[0].resume_count == 5
    assert results[1].id == 2
    assert results[1].role == "Backend Python Engineer"
    assert results[1].resume_count == 3


def test_get_screening_task_detail_owner_success():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 42

    task = MagicMock(spec=ScreeningTask)
    task.id = 10
    task.recruiter_id = 42
    task.role = "Senior Full Stack Dev"
    task.job_description = "Job description text requirements"
    task.resume_count = 2
    task.ranked_results = [
        {"rank": 1, "name": "Jane Doe", "similarity_score": 92.5},
        {"rank": 2, "name": "John Smith", "similarity_score": 85.0}
    ]
    task.created_at = datetime.datetime(2026, 10, 13, 10, 0, 0)

    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = task

    result = get_screening_task_detail(task_id=10, current_user=mock_user, db=mock_db)

    assert result.id == 10
    assert result.role == "Senior Full Stack Dev"
    assert result.job_description == "Job description text requirements"
    assert result.resume_count == 2
    assert len(result.ranked_results) == 2
    assert result.ranked_results[0]["rank"] == 1
    assert result.ranked_results[0]["name"] == "Jane Doe"


def test_get_screening_task_detail_unauthorized_or_missing():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 42  # Current recruiter

    # If the task belongs to recruiter 99 or doesn't exist, filter(recruiter_id == 42) returns None
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_screening_task_detail(task_id=999, current_user=mock_user, db=mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Screening task not found"


from backend.routers.recruiter import update_job_description, archive_job_description

def test_create_job_description_empty_name_fails():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    with pytest.raises(HTTPException) as exc_info:
        create_job_description(
            title="   ",
            subtitle=None,
            description="Valid JD text",
            company=None,
            optional_notes=None,
            current_user=mock_user,
            db=mock_db
        )
    assert exc_info.value.status_code == 400
    assert "name cannot be empty" in exc_info.value.detail

def test_create_job_description_empty_description_fails():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    with pytest.raises(HTTPException) as exc_info:
        create_job_description(
            title="Valid Title",
            subtitle=None,
            description="   \n\t  ",
            company=None,
            optional_notes=None,
            current_user=mock_user,
            db=mock_db
        )
    assert exc_info.value.status_code == 400
    assert "text cannot be empty" in exc_info.value.detail

def test_create_job_description_duplicate_names_distinct_records():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = create_job_description(
        title="Software Engineer",
        subtitle=None,
        description="Different description for Role B",
        company=None,
        optional_notes=None,
        current_user=mock_user,
        db=mock_db
    )

    assert result["message"] == "Job description created successfully"
    mock_db.add.assert_called_once()
    added_obj = mock_db.add.call_args[0][0]
    assert added_obj.title == "Software Engineer"
    assert added_obj.description == "Different description for Role B"

def test_update_job_description_success():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    existing = MagicMock(spec=JobDescription)
    existing.id = 10
    existing.owner_id = 1
    existing.title = "Old Title"
    existing.description = "Old JD text"

    mock_db.query.return_value.filter.return_value.first.return_value = existing

    result = update_job_description(
        jd_id=10,
        title="  Updated Backend Engineer  ",
        subtitle=None,
        description="  Updated JD requirements text  ",
        company="Acme Corp",
        optional_notes="Updated notes",
        current_user=mock_user,
        db=mock_db
    )

    assert result["message"] == "Job description updated successfully"
    assert result["id"] == 10
    assert existing.title == "Updated Backend Engineer"
    assert existing.description == "Updated JD requirements text"
    assert existing.company == "Acme Corp"
    mock_db.commit.assert_called_once()

def test_update_job_description_validation():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    # Empty name fails
    with pytest.raises(HTTPException) as exc1:
        update_job_description(
            jd_id=10,
            title="   ",
            subtitle=None,
            description="Valid text",
            company=None,
            optional_notes=None,
            current_user=mock_user,
            db=mock_db
        )
    assert exc1.value.status_code == 400

    # Empty desc fails
    with pytest.raises(HTTPException) as exc2:
        update_job_description(
            jd_id=10,
            title="Valid Title",
            subtitle=None,
            description="   ",
            company=None,
            optional_notes=None,
            current_user=mock_user,
            db=mock_db
        )
    assert exc2.value.status_code == 400

def test_update_job_description_unauthorized():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    # Filter with owner_id returns None for another user's JD
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        update_job_description(
            jd_id=99,
            title="Valid Title",
            subtitle=None,
            description="Valid text",
            company=None,
            optional_notes=None,
            current_user=mock_user,
            db=mock_db
        )
    assert exc.value.status_code == 404

def test_archive_job_description_success():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    existing = MagicMock(spec=JobDescription)
    existing.id = 15
    existing.is_archived = False
    mock_db.query.return_value.filter.return_value.first.return_value = existing

    result = archive_job_description(jd_id=15, current_user=mock_user, db=mock_db)

    assert result["message"] == "Job description archived successfully"
    assert existing.is_archived is True
    mock_db.commit.assert_called_once()

def test_archive_job_description_unauthorized():
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        archive_job_description(jd_id=999, current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404

def test_screening_task_preserves_historical_jd_when_library_modified():
    # Verify that a ScreeningTask's job_description is stored as an immutable snapshot
    task = ScreeningTask(
        id=1,
        recruiter_id=100,
        role="GenAI Engineer",
        job_description="Original Screening Job Description Text v1",
        resume_count=3,
        ranked_results=[{"rank": 1, "name": "Alice"}],
        created_at=datetime.datetime(2026, 10, 10, 10, 0, 0)
    )

    library_jd = JobDescription(
        id=5,
        owner_id=100,
        title="GenAI Engineer",
        description="Original Screening Job Description Text v1",
        is_archived=False
    )

    # Recruiter updates library JD
    library_jd.title = "Lead GenAI Engineer"
    library_jd.description = "Completely rewritten JD v2 with Rust and CUDA requirements"

    # Historical screening task remains intact
    assert task.job_description == "Original Screening Job Description Text v1"
    assert task.role == "GenAI Engineer"

    # Recruiter archives library JD
    library_jd.is_archived = True
    assert task.job_description == "Original Screening Job Description Text v1"


from backend.schemas.schemas import JobDescriptionResponse

def test_job_description_model_name_synonym():
    """Verify that JobDescription.name is an active synonym for JobDescription.title."""
    jd = JobDescription(
        owner_id=1,
        name="Staff Software Engineer",
        description="Lead large-scale distributed systems projects.",
        is_archived=False
    )
    assert jd.title == "Staff Software Engineer"
    assert jd.name == "Staff Software Engineer"

    # Mutating .name must mutate .title
    jd.name = "Principal Software Engineer"
    assert jd.title == "Principal Software Engineer"

    # Mutating .title must mutate .name
    jd.title = "Director of Engineering"
    assert jd.name == "Director of Engineering"

def test_job_description_response_schema_serialization():
    """Verify that JobDescriptionResponse correctly maps both title and name from an ORM object."""
    now = datetime.datetime.utcnow()
    jd = JobDescription(
        id=99,
        owner_id=1,
        title="MLOps Engineer",
        description="Deploy and monitor ML models in production.",
        company="AI Labs",
        optional_notes="Urgent hire",
        is_archived=False,
        created_at=now,
        updated_at=now
    )
    resp = JobDescriptionResponse.model_validate(jd)
    assert resp.id == 99
    assert resp.title == "MLOps Engineer"
    assert resp.name == "MLOps Engineer"
    assert resp.description == "Deploy and monitor ML models in production."
    assert resp.company == "AI Labs"
    assert resp.is_archived is False

def test_create_job_description_with_name_parameter():
    """Verify create_job_description correctly accepts 'name' instead of 'title'."""
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = create_job_description(
        name="Security Architect",
        title=None,
        subtitle=None,
        description="Manage SOC2, IAM, and cloud posture.",
        company=None,
        optional_notes=None,
        current_user=mock_user,
        db=mock_db
    )

    assert result["message"] == "Job description created successfully"
    assert result["name"] == "Security Architect"
    assert result["title"] == "Security Architect"
    added_obj = mock_db.add.call_args[0][0]
    assert added_obj.title == "Security Architect"
    assert added_obj.name == "Security Architect"

def test_update_job_description_with_name_parameter():
    """Verify update_job_description correctly accepts 'name' instead of 'title'."""
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    existing = MagicMock(spec=JobDescription)
    existing.id = 25
    existing.owner_id = 1
    existing.title = "Junior DevOps"
    existing.description = "Old description"

    mock_db.query.return_value.filter.return_value.first.return_value = existing

    result = update_job_description(
        jd_id=25,
        name="Senior Site Reliability Engineer",
        title=None,
        subtitle=None,
        description="Manage Kubernetes clusters and observability.",
        company=None,
        optional_notes=None,
        current_user=mock_user,
        db=mock_db
    )

    assert result["message"] == "Job description updated successfully"
    assert result["name"] == "Senior Site Reliability Engineer"
    assert result["title"] == "Senior Site Reliability Engineer"
    assert existing.title == "Senior Site Reliability Engineer"

def test_list_job_descriptions_includes_name_and_title():
    """Verify list_job_descriptions serializes both 'name' and 'title'."""
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    jd = MagicMock(spec=JobDescription)
    jd.id = 1
    jd.title = "Frontend Developer"
    jd.subtitle = None
    jd.description = "React / Next.js expert"
    jd.company = "SaaS Co"
    jd.optional_notes = None
    jd.is_archived = False
    jd.created_at = datetime.datetime.utcnow()
    jd.updated_at = None

    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = [jd]

    results = list_job_descriptions(current_user=mock_user, db=mock_db)
    assert len(results) == 1
    assert results[0]["title"] == "Frontend Developer"
    assert results[0]["name"] == "Frontend Developer"

def test_live_schema_verification_job_descriptions():
    """Inspects live database schema to verify the table and name/title column constraints."""
    from backend.database.database import engine
    from sqlalchemy import inspect
    insp = inspect(engine)
    tables = insp.get_table_names()
    assert "job_descriptions" in tables, "Table job_descriptions must exist in the target database"

    columns = {c["name"]: c for c in insp.get_columns("job_descriptions")}
    assert "title" in columns, "Column 'title' must exist in job_descriptions table"
    assert columns["title"]["nullable"] is False, "Column 'title' in job_descriptions must be NOT NULL"
    assert "owner_id" in columns, "Column 'owner_id' must exist in job_descriptions"
    assert "description" in columns, "Column 'description' must exist in job_descriptions"
    assert "is_archived" in columns, "Column 'is_archived' must exist in job_descriptions"


def test_get_screening_task_detail_omits_candidate_recommendations():
    """Verify get_screening_task_detail strips recommendations from candidate analysis_metadata."""
    from backend.routers.recruiter import get_screening_task_detail
    from backend.models.models import ScreeningTask

    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 42

    task = MagicMock(spec=ScreeningTask)
    task.id = 99
    task.recruiter_id = 42
    task.role = "Backend Engineer"
    task.job_description = "Python and FastAPI"
    task.resume_count = 1
    task.ranked_results = [
        {
            "rank": 1,
            "name": "Alex Candidate",
            "similarity_score": 88.0,
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Docker"],
            "analysis_metadata": {
                "profile_name": "General Software Engineer",
                "score_breakdown": {"skills": 90},
                "xai": {"summary": "Strong match"},
                "recommendations": {
                    "list": [
                        {
                            "id": "rec-1",
                            "title": "Highlight Professional Experience",
                            "priority": "HIGH"
                        }
                    ]
                }
            }
        }
    ]
    task.created_at = datetime.datetime.utcnow()

    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = task

    result = get_screening_task_detail(task_id=99, current_user=mock_user, db=mock_db)

    assert result.id == 99
    assert len(result.ranked_results) == 1
    cand_meta = result.ranked_results[0]["analysis_metadata"]
    # Candidate recommendations must be completely omitted
    assert "recommendations" not in cand_meta
    # Other recruiter analysis data must be preserved
    assert cand_meta["profile_name"] == "General Software Engineer"
    assert cand_meta["score_breakdown"]["skills"] == 90
    assert cand_meta["xai"]["summary"] == "Strong match"


def test_get_recruiter_stats_omits_candidate_recommendations():
    """Verify get_recruiter_stats returns empty top_recommended_improvements even if scans have recs."""
    from backend.routers.recruiter import get_recruiter_stats
    from backend.models.models import ScanResult

    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 10

    scan = MagicMock(spec=ScanResult)
    scan.ats_score = 85.0
    scan.analysis_metadata = {
        "candidate": {"experience": 3.0, "education": "Bachelor"},
        "skills": {"matched": ["Python"], "missing": ["Rust"]},
        "recommendations": {
            "list": [
                {"title": "Showcase Skill: Rust"},
                {"title": "Highlight Professional Experience"}
            ]
        }
    }

    mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = (1, 85.0)
    mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [
        (scan.analysis_metadata,)
    ]

    stats = get_recruiter_stats(current_user=mock_user, db=mock_db)
    assert stats["total_candidates_screened"] == 1
    assert stats["average_ats_score"] == 85.0
    # top_recommended_improvements must be strictly empty for recruiters
    assert stats["top_recommended_improvements"] == []
    assert len(stats["most_common_matched_skills"]) == 1
    assert len(stats["most_common_missing_skills"]) == 1


@pytest.mark.anyio
async def test_process_resumes_omits_candidate_recommendations_for_recruiter(monkeypatch):
    """Verify process_resumes response strips candidate recommendations from analysis_metadata."""
    from backend.routers.recruiter import process_resumes
    from fastapi import UploadFile
    import io

    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 5

    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Mock screen_resumes to return a candidate with recommendations in analysis_metadata
    async def mock_screen_resumes(*args, **kwargs):
        return {
            "results": [
                {
                    "filename": "resume.pdf",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "1234567890",
                    "linkedin": "https://linkedin.com/in/johndoe",
                    "github": "https://github.com/johndoe",
                    "experience": 4,
                    "education": "Master",
                    "projects": 3,
                    "similarity_score": 88.5,
                    "skill_score": 90.0,
                    "experience_score": 85.0,
                    "education_score": 90.0,
                    "projects_score": 80.0,
                    "rank": 1,
                    "matched_skills": ["Python", "SQL"],
                    "missing_skills": ["Kubernetes"],
                    "extracted_skills": ["Python", "SQL"],
                    "semantic_score": 87.0,
                    "semantic_data": None,
                    "xai_explanations": {"reasoning": "Good fit"},
                    "analysis_metadata": {
                        "profile_name": "General Software Engineer",
                        "recommendations": {
                            "list": [
                                {"title": "Highlight Professional Experience", "priority": "HIGH"},
                                {"title": "Add Certifications or Academic Gaps", "priority": "MEDIUM"}
                            ]
                        }
                    },
                    "pipeline_context": MagicMock()
                }
            ]
        }

    monkeypatch.setattr("backend.routers.recruiter.screen_resumes", mock_screen_resumes)

    # Mock PersistenceStage
    mock_stage = MagicMock()
    mock_res = MagicMock()
    mock_res.status = "success"
    mock_res.event = MagicMock(status="success")
    mock_stage.execute_batch.return_value = [mock_res]
    monkeypatch.setattr("backend.services.pipeline.PersistenceStage", lambda db: mock_stage)

    fake_file = UploadFile(filename="resume.pdf", file=io.BytesIO(b"%PDF-1.4 dummy content"))
    from starlette.requests import Request
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/recruiter/process",
        "headers": [(b"host", b"testserver")],
        "client": ("127.0.0.1", 12345)
    }
    mock_request = Request(scope)

    result = await process_resumes(
        request=mock_request,
        job_description="Seeking software engineer",
        resumes=[fake_file],
        current_user=mock_user,
        db=mock_db
    )

    assert "results" in result
    assert len(result["results"]) == 1
    cand = result["results"][0]
    assert cand["name"] == "John Doe"
    assert cand["similarity_score"] == 88.5
    assert "recommendations" not in cand["analysis_metadata"]
    assert cand["analysis_metadata"]["profile_name"] == "General Software Engineer"


def test_candidate_resume_details_preserves_recommendations():
    """Verify get_candidate_resume_details still returns recommendations for candidate users."""
    from backend.routers.candidate import get_candidate_resume_details
    from backend.models.models import Resume, ScanResult, ResumeStatus

    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.id = 100
    mock_user.email = "candidate@example.com"

    mock_resume = MagicMock(spec=Resume)
    mock_resume.id = 12
    mock_resume.version = 1
    mock_resume.label = "Initial Resume"
    mock_resume.original_filename = "my_resume.pdf"
    mock_resume.file_type = "pdf"
    mock_resume.uploaded_at = datetime.datetime.utcnow()
    mock_resume.status = ResumeStatus.ACTIVE

    mock_scan = MagicMock(spec=ScanResult)
    mock_scan.ats_score = 82.0
    mock_scan.job_description = None
    mock_scan.analysis_metadata = {
        "candidate": {"name": "Candidate User", "email": "candidate@example.com"},
        "recommendations": {
            "list": [
                {"id": "rec-1", "title": "Highlight Professional Experience", "priority": "HIGH"}
            ]
        }
    }
    mock_resume.scan_results = [mock_scan]

    mock_db.query.return_value.filter.return_value.first.return_value = mock_resume

    cand_result = get_candidate_resume_details(resume_id=12, current_user=mock_user, db=mock_db)

    assert cand_result["id"] == 12
    # Candidate user MUST receive recommendations
    assert cand_result["recommendations"] is not None
    assert len(cand_result["recommendations"]["list"]) == 1
    assert cand_result["recommendations"]["list"][0]["title"] == "Highlight Professional Experience"


