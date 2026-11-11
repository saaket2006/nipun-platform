"""
Unit and boundary tests for candidate scoring status logic.
Audits the existing scoring thresholds in backend/services/xai/builder.py
and verifies boundary behavior (below, equal to, above each threshold).
"""

import pytest
from unittest.mock import MagicMock
from backend.services.xai.builder import _resolve_status, build_score_components


# ==============================================================================
# 1. DIRECT BOUNDARY TESTS FOR _resolve_status
# ==============================================================================

class TestResolveStatusBoundaries:
    """Tests the status resolution function with exact boundaries."""

    @pytest.mark.parametrize("score, met_th, partial_th, expected", [
        # --- Technical Skills (80.0 / 40.0) ---
        (0.0, 80.0, 40.0, "not_met"),
        (39.9, 80.0, 40.0, "not_met"),         # Below partially met
        (40.0, 80.0, 40.0, "partially_met"),   # Exactly at partially met
        (40.1, 80.0, 40.0, "partially_met"),   # Just above partially met
        (49.0, 80.0, 40.0, "partially_met"),   # User example: 49%
        (79.9, 80.0, 40.0, "partially_met"),   # Just below met
        (80.0, 80.0, 40.0, "met"),             # Exactly at met
        (80.1, 80.0, 40.0, "met"),             # Just above met
        (100.0, 80.0, 40.0, "met"),            # Perfect score

        # --- Work Experience (80.0 / 30.0) ---
        (0.0, 80.0, 30.0, "not_met"),
        (29.9, 80.0, 30.0, "not_met"),         # Below partially met
        (30.0, 80.0, 30.0, "partially_met"),   # User example: 30% (exactly at boundary)
        (30.1, 80.0, 30.0, "partially_met"),   # Just above partially met
        (79.9, 80.0, 30.0, "partially_met"),   # Just below met
        (80.0, 80.0, 30.0, "met"),             # Exactly at met
        (80.1, 80.0, 30.0, "met"),             # Just above met

        # --- Education (80.0 / 60.0) ---
        (20.0, 80.0, 60.0, "not_met"),         # Other/None tier (20%) -> not_met
        (59.9, 80.0, 60.0, "not_met"),         # Just below Bachelor
        (60.0, 80.0, 60.0, "partially_met"),   # User example: 60% Bachelor (exactly at boundary)
        (60.1, 80.0, 60.0, "partially_met"),   # Just above Bachelor
        (79.9, 80.0, 60.0, "partially_met"),   # Just below Master (80%)
        (80.0, 80.0, 60.0, "met"),             # Master tier (80%) -> met
        (100.0, 80.0, 60.0, "met"),            # PhD tier (100%) -> met

        # --- Projects (100.0 / 20.0) ---
        (0.0, 100.0, 20.0, "not_met"),         # 0 projects
        (19.9, 100.0, 20.0, "not_met"),        # Below partially met
        (20.0, 100.0, 20.0, "partially_met"),  # Exactly at partially met
        (33.3, 100.0, 20.0, "partially_met"),  # 1 of 3 projects -> partially_met
        (66.7, 100.0, 20.0, "partially_met"),  # 2 of 3 projects -> partially_met
        (99.9, 100.0, 20.0, "partially_met"),  # Just below 100% -> partially_met!
        (100.0, 100.0, 20.0, "met"),           # User example: 100% (3 of 3 projects) -> met

        # --- Document Similarity (70.0 / 30.0) ---
        (29.9, 70.0, 30.0, "not_met"),
        (30.0, 70.0, 30.0, "partially_met"),
        (69.9, 70.0, 30.0, "partially_met"),
        (70.0, 70.0, 30.0, "met"),

        # --- Overall Match Score (70.0 / 40.0) ---
        (39.9, 70.0, 40.0, "not_met"),
        (40.0, 70.0, 40.0, "partially_met"),
        (69.9, 70.0, 40.0, "partially_met"),
        (70.0, 70.0, 40.0, "met"),
    ])
    def test_status_boundary_resolution(self, score, met_th, partial_th, expected):
        assert _resolve_status(score, met_th, partial_th) == expected


# ==============================================================================
# 2. REPRODUCING USER-REPORTED CANDIDATE EVALUATION SCENARIO
# ==============================================================================

class TestUserScenarioScoringComponents:
    """
    Reproduces the exact candidate scenario reported by the user:
    - Education: 60% -> Partially Met
    - Technical Skills: 49% -> Partially Met
    - Projects: 100% -> Met
    - Work Experience: 30% -> Partially Met
    """

    def test_user_reported_exact_scenario(self):
        mock_event = MagicMock()
        mock_event.profile_resolved = None
        mock_event.skill_score = 49.0
        mock_event.experience_score = 30.0
        mock_event.education_score = 60.0
        mock_event.projects_score = 100.0
        mock_event.candidate_experience = 3.0
        mock_event.candidate_internships = 0
        mock_event.candidate_education = "Bachelor"
        mock_event.candidate_projects = 3
        
        # Calculate composite similarity score based on default weights
        # (49 * 0.50) + (30 * 0.25) + (60 * 0.15) + (100 * 0.10) = 24.5 + 7.5 + 9.0 + 10.0 = 51.0%
        mock_event.similarity_score = 51.0

        components = build_score_components(
            scoring_event=mock_event,
            match_results=[],
            doc_similarity_percentage=45.0
        )

        comp_dict = {c.name: c for c in components}

        # Verify exact reported statuses
        assert comp_dict["Education"].raw_score == 60.0
        assert comp_dict["Education"].status == "partially_met"

        assert comp_dict["Technical Skills"].raw_score == 49.0
        assert comp_dict["Technical Skills"].status == "partially_met"

        assert comp_dict["Projects"].raw_score == 100.0
        assert comp_dict["Projects"].status == "met"

        assert comp_dict["Work Experience"].raw_score == 30.0
        assert comp_dict["Work Experience"].status == "partially_met"

        # Overall composite: 51.0% >= 40.0 and < 70.0 -> partially_met
        assert comp_dict["Overall Score"].raw_score == 51.0
        assert comp_dict["Overall Score"].status == "partially_met"
        assert comp_dict["Overall Score"].weighted_score == 51.0

        # Weighted scores vs Raw scores validation:
        # Technical skills raw is 49.0, weighted is 24.5
        assert comp_dict["Technical Skills"].weighted_score == 24.5
        # Work experience raw is 30.0, weighted is 7.5
        assert comp_dict["Work Experience"].weighted_score == 7.5
        # Education raw is 60.0, weighted is 9.0
        assert comp_dict["Education"].weighted_score == 9.0
        # Projects raw is 100.0, weighted is 10.0
        assert comp_dict["Projects"].weighted_score == 10.0


# ==============================================================================
# 3. DEMONSTRATING CURRENT DISPARITIES / ASYMMETRIES
# ==============================================================================

class TestCurrentThresholdDisparities:
    """
    Demonstrates the mathematical anomalies under current hardcoded thresholds:
    1. A 75% in Technical Skills is 'partially_met', but 70% in Overall Score is 'met'.
    2. A 90% in Projects is 'partially_met', but 80% in Education is 'met'.
    3. A 30% in Experience is 'partially_met', but 30% in Technical Skills is 'not_met'.
    4. A 55% in Education is 'not_met', but 40% in Technical Skills is 'partially_met'.
    """

    def test_skills_75_vs_overall_70(self):
        # Skills at 75% is considered partially met (needs 80% for met)
        assert _resolve_status(75.0, 80.0, 40.0) == "partially_met"
        # Overall score at 70% is considered met (needs 70% for met)
        assert _resolve_status(70.0, 70.0, 40.0) == "met"

    def test_projects_90_vs_education_80(self):
        # Projects requires 100% for met; 90% is partially met
        assert _resolve_status(90.0, 100.0, 20.0) == "partially_met"
        # Education requires 80% for met; 80% is met
        assert _resolve_status(80.0, 80.0, 60.0) == "met"

    def test_experience_30_vs_skills_30(self):
        # Experience at 30% is partially met (threshold is 30.0)
        assert _resolve_status(30.0, 80.0, 30.0) == "partially_met"
        # Technical skills at 30% is not met (threshold is 40.0)
        assert _resolve_status(30.0, 80.0, 40.0) == "not_met"

    def test_education_55_vs_skills_40(self):
        # Education at 55% is not met (threshold is 60.0)
        assert _resolve_status(55.0, 80.0, 60.0) == "not_met"
        # Skills at 40% is partially met (threshold is 40.0)
        assert _resolve_status(40.0, 80.0, 40.0) == "partially_met"
