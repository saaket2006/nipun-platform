import pytest
from backend.services.skills.normalizer import SkillNormalizer
from backend.services.skills.models import Skill
import backend.services.skills.loader as loader

@pytest.fixture(autouse=True)
def mock_skills(monkeypatch):
    test_skills = [
        Skill(
            id="react",
            canonical_name="React",
            aliases=["ReactJS", "React.js"],
            abbreviations=[],
            category="Frontend",
            subcategory="UI",
            technology_family="Frontend"
        ),
        Skill(
            id="large_language_models",
            canonical_name="Large Language Models",
            aliases=["GenAI"],
            abbreviations=["LLM"],
            category="AI",
            subcategory="Deep Learning",
            technology_family="AI"
        )
    ]
    monkeypatch.setattr(loader, "_cached_skills", test_skills)
    monkeypatch.setattr(loader, "get_skills_loader", lambda: test_skills)

def test_normalizer_exact():
    normalizer = SkillNormalizer()
    res = normalizer.normalize("React")
    assert res.match_type == "exact"
    assert res.skill.id == "react"

def test_normalizer_exact_id():
    normalizer = SkillNormalizer()
    res = normalizer.normalize("react")
    assert res.match_type == "exact"
    assert res.skill.id == "react"

def test_normalizer_alias():
    normalizer = SkillNormalizer()
    res = normalizer.normalize("ReactJS")
    assert res.match_type == "alias"
    assert res.skill.id == "react"

def test_normalizer_abbreviation():
    normalizer = SkillNormalizer()
    res = normalizer.normalize("LLM")
    assert res.match_type == "abbreviation"
    assert res.skill.id == "large_language_models"

def test_normalizer_unknown():
    normalizer = SkillNormalizer()
    res = normalizer.normalize("Some Random Skill")
    assert res.match_type == "unknown"
    assert res.skill.id == "some_random_skill"
    assert res.skill.canonical_name == "Some Random Skill"
