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

