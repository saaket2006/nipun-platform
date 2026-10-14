from typing import List, Dict, Any
from backend.services.xai.models import ScoreComponent, Evidence
from backend.services.xai.evidence import (
    generate_skills_evidence,
    generate_experience_evidence,
    generate_education_evidence,
    generate_projects_evidence,
    generate_document_similarity_evidence
)
from backend.services.policy.scoring_policy import default_scoring_policy

def build_score_components(
    scoring_event: Any,
    match_results: List[Any],
    doc_similarity_percentage: float = 0.0
) -> List[ScoreComponent]:
    """
    Builds the structured ScoreComponent list using the candidate's scored parameters
    and semantic MatchResults.
    """
    components = []
    
    # Extract weights from resolved profile or use default fallback
    profile = getattr(scoring_event, "profile_resolved", None)
    weights = profile.weights if profile else {"skills": 0.50, "experience": 0.25, "education": 0.15, "projects": 0.10}
    
    # 1. Technical Skills Component
    skills_raw = scoring_event.skill_score
    skills_weight = weights.get("skills", 0.50)
    skills_evidence = generate_skills_evidence(match_results)
    components.append(ScoreComponent(
        name="Technical Skills",
        raw_score=skills_raw,
        weight=skills_weight,
        weighted_score=skills_raw * skills_weight,
        max_score=100.0,
        status=_resolve_status(skills_raw, 80.0, 40.0),
        details="Evaluates matches of candidate technical skills against the job description.",
        evidence=skills_evidence
    ))
    
    # 2. Work Experience Component
    exp_raw = scoring_event.experience_score
    exp_weight = weights.get("experience", 0.25)
    exp_evidence = generate_experience_evidence(
        years=scoring_event.candidate_experience,
        internships=scoring_event.candidate_internships
    )
    components.append(ScoreComponent(
        name="Work Experience",
        raw_score=exp_raw,
        weight=exp_weight,
        weighted_score=exp_raw * exp_weight,
        max_score=100.0,
        status=_resolve_status(exp_raw, 80.0, 30.0),
        details="Calculates score based on professional tenure and relevant internships.",
        evidence=exp_evidence
    ))
    
    # 3. Education Component
    edu_raw = scoring_event.education_score
    edu_weight = weights.get("education", 0.15)
    edu_evidence = generate_education_evidence(scoring_event.candidate_education)
    components.append(ScoreComponent(
        name="Education",
        raw_score=edu_raw,
        weight=edu_weight,
        weighted_score=edu_raw * edu_weight,
        max_score=100.0,
        status=_resolve_status(edu_raw, 80.0, 60.0),
        details="Checks parsed academic credentials matching PhD, Master, or Bachelor tier.",
        evidence=edu_evidence
    ))
    
    # 4. Projects Component
    proj_raw = scoring_event.projects_score
    proj_weight = weights.get("projects", 0.10)
    proj_evidence = generate_projects_evidence(scoring_event.candidate_projects)
    components.append(ScoreComponent(
        name="Projects",
        raw_score=proj_raw,
        weight=proj_weight,
        weighted_score=proj_raw * proj_weight,
        max_score=100.0,
        status=_resolve_status(proj_raw, 100.0, 20.0),
        details=f"Checks count of completed matching tech projects (ideal target is {default_scoring_policy.project_target_count}).",
        evidence=proj_evidence
    ))
    
    # 5. Document Similarity Component
    sim_raw = doc_similarity_percentage
    sim_weight = 0.0
    sim_evidence = generate_document_similarity_evidence(sim_raw)
    components.append(ScoreComponent(
        name="Document Similarity",
        raw_score=sim_raw,
        weight=sim_weight,
        weighted_score=0.0,
        max_score=100.0,
        status=_resolve_status(sim_raw, 70.0, 30.0),
        details="Lexical TF-IDF text overlap check between JD requirements and candidate profile.",
        evidence=sim_evidence
    ))
    
    # 6. Overall Score Component
    overall_raw = scoring_event.similarity_score
    overall_weight = 1.00
    # Combine all evidence for overall score reference
    overall_evidence = skills_evidence + exp_evidence + edu_evidence + proj_evidence + sim_evidence
    components.append(ScoreComponent(
        name="Overall Score",
        raw_score=overall_raw,
        weight=overall_weight,
        weighted_score=overall_raw,
        max_score=100.0,
        status=_resolve_status(overall_raw, 70.0, 40.0),
        details="Weighted linear sum of all core matching parameters.",
        evidence=overall_evidence
    ))
    
    return components

def _resolve_status(score: float, met_threshold: float, partially_met_threshold: float) -> str:
    if score >= met_threshold:
        return "met"
    elif score >= partially_met_threshold:
        return "partially_met"
    return "not_met"
