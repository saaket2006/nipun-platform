import pytest
from backend.services.xai.evidence import generate_experience_evidence

def test_generate_experience_evidence_no_internships():
    evidence = generate_experience_evidence(years=5, internships=0)

    assert len(evidence) == 1
    ev = evidence[0]

    assert ev.type == "experience_record"
    assert ev.category == "Work Experience"
    assert ev.title == "Industry Experience Level"
    assert ev.importance == "high"
    assert ev.confidence == 1.0

    assert "Candidate has 5 years of professional experience totaling 5.0 years (Mid Level)." in ev.description

def test_generate_experience_evidence_with_internships():
    evidence = generate_experience_evidence(years=2, internships=2)

    assert len(evidence) == 1
    ev = evidence[0]

    assert ev.type == "experience_record"
    assert ev.category == "Work Experience"
    assert ev.title == "Industry Experience Level"
    assert ev.importance == "high"
    assert ev.confidence == 1.0

    assert "Candidate has 2 years of professional experience" in ev.description
    assert "and 2 relevant internship(s) (counting as +1.0 years of experience)" in ev.description
    assert "totaling 3.0 years (Mid Level)." in ev.description

def test_generate_experience_evidence_senior():
    evidence = generate_experience_evidence(years=8, internships=0)
    assert len(evidence) == 1
    assert "totaling 8.0 years (Senior Level)." in evidence[0].description

def test_generate_experience_evidence_entry_level():
    evidence = generate_experience_evidence(years=0, internships=1)
    assert len(evidence) == 1
    assert "totaling 0.5 years (Entry Level)." in evidence[0].description

def test_generate_experience_evidence_junior():
    evidence = generate_experience_evidence(years=1, internships=1)
    assert len(evidence) == 1
    assert "totaling 1.5 years (Junior Level)." in evidence[0].description

def test_generate_projects_evidence():
    from backend.services.xai.evidence import generate_projects_evidence
    ev_below = generate_projects_evidence(count=2)
    assert "partially satisfies the preferred threshold of 3 projects" in ev_below[0].description
    ev_meet = generate_projects_evidence(count=3)
    assert "exceeds or meets the ideal target threshold of 3 projects" in ev_meet[0].description
