import pytest
from backend.services.recommendations.estimator import (
    estimate_missing_skill_gain,
    estimate_experience_gain,
    estimate_education_gain,
    estimate_project_gain,
)
from backend.services.policy.scoring_policy import default_scoring_policy

def test_estimate_missing_skill_gain_default_weights():
    # gain = weight * default_skills_weight * 100.0
    # default_skills_weight is 0.50
    # For weight = 0.8: gain = 0.8 * 0.50 * 100 = 40.0
    result = estimate_missing_skill_gain(weight=0.8)
    assert result == 40.0

def test_estimate_missing_skill_gain_custom_weights():
    custom_weights = {"skills": 0.40}
    # For weight = 0.8: gain = 0.8 * 0.40 * 100 = 32.0
    result = estimate_missing_skill_gain(weight=0.8, weights=custom_weights)
    assert result == 32.0

def test_estimate_missing_skill_gain_custom_weights_missing_key():
    custom_weights = {"experience": 0.30}
    # Falls back to default_skills_weight (0.50)
    # For weight = 0.8: gain = 0.8 * 0.50 * 100 = 40.0
    result = estimate_missing_skill_gain(weight=0.8, weights=custom_weights)
    assert result == 40.0

def test_estimate_experience_gain_below_max():
    # max_yrs = 10.0, default_experience_weight = 0.25
    # For current_years = 5.0 (below max_yrs): gain = (1.0 / 10.0) * 0.25 * 100.0 = 2.5
    result = estimate_experience_gain(current_years=5.0)
    assert result == 2.5

def test_estimate_experience_gain_at_max():
    result = estimate_experience_gain(current_years=10.0)
    assert result == 0.0

def test_estimate_experience_gain_above_max():
    result = estimate_experience_gain(current_years=12.0)
    assert result == 0.0

def test_estimate_experience_gain_custom_weights():
    custom_weights = {"experience": 0.40}
    # For current_years = 5.0: gain = (1.0 / 10.0) * 0.40 * 100.0 = 4.0
    result = estimate_experience_gain(current_years=5.0, weights=custom_weights)
    assert result == 4.0

def test_estimate_experience_gain_custom_weights_missing_key():
    custom_weights = {"skills": 0.40}
    # Falls back to default experience weight (0.25)
    # gain = (1.0 / 10.0) * 0.25 * 100.0 = 2.5
    result = estimate_experience_gain(current_years=5.0, weights=custom_weights)
    assert result == 2.5

def test_estimate_education_gain_phd():
    result = estimate_education_gain(current_education="PhD")
    assert result == 0.0

def test_estimate_education_gain_master():
    # default_education_weight = 0.15
    # gain = 20.0 * 0.15 = 3.0
    result = estimate_education_gain(current_education="Master")
    assert result == 3.0

def test_estimate_education_gain_bachelor():
    # default_education_weight = 0.15
    # gain = 20.0 * 0.15 = 3.0
    result = estimate_education_gain(current_education="Bachelor")
    assert result == 3.0

def test_estimate_education_gain_other():
    # default_education_weight = 0.15
    # gain = 40.0 * 0.15 = 6.0
    result = estimate_education_gain(current_education="High School")
    assert result == 6.0

def test_estimate_education_gain_custom_weights():
    custom_weights = {"education": 0.20}
    # For Master: gain = 20.0 * 0.20 = 4.0
    result = estimate_education_gain(current_education="Master", weights=custom_weights)
    assert result == 4.0

def test_estimate_project_gain_below_target():
    # target = 3, default_projects_weight = 0.10
    # gain = (1.0 / 3) * 0.10 * 100.0 = 3.333... -> 3.3
    result = estimate_project_gain(current_count=2)
    assert result == 3.3

def test_estimate_project_gain_at_target():
    result = estimate_project_gain(current_count=3)
    assert result == 0.0

def test_estimate_project_gain_above_target():
    result = estimate_project_gain(current_count=5)
    assert result == 0.0

def test_estimate_project_gain_custom_weights():
    custom_weights = {"projects": 0.20}
    # gain = (1.0 / 3) * 0.20 * 100.0 = 6.666... -> 6.7
    result = estimate_project_gain(current_count=2, weights=custom_weights)
    assert result == 6.7
