from typing import List, Dict, Any, Optional
from backend.services.xai.models import Evidence

def generate_skills_evidence(match_results: List[Any]) -> List[Evidence]:
    """
    Generates Evidence objects for each MatchResult in semantic skill matching.
    """
    evidence_list = []
    
    for res in match_results:
        req_name = res.required_skill.canonical_name
        cand_name = res.candidate_skill.canonical_name
        
        if res.match_type == "EXACT":
            evidence_list.append(Evidence(
                type="exact_match",
                category="Technical Skills",
                title=f"Exact Match: {req_name}",
                description=f"Candidate has exact keyword match for required skill '{req_name}'.",
                importance="high",
                related_skill=req_name,
                confidence=res.confidence
            ))
        elif res.match_type == "ALIAS":
            evidence_list.append(Evidence(
                type="alias_match",
                category="Technical Skills",
                title=f"Alias Match: {req_name}",
                description=f"Candidate possesses '{cand_name}', which is a recognized alias/synonym for '{req_name}'.",
                importance="high",
                related_skill=req_name,
                confidence=res.confidence
            ))
        elif res.match_type == "ABBREVIATION":
            evidence_list.append(Evidence(
                type="abbreviation_match",
                category="Technical Skills",
                title=f"Abbreviation Match: {req_name}",
                description=f"Candidate possesses '{cand_name}', which is an abbreviation/acronym of '{req_name}'.",
                importance="high",
                related_skill=req_name,
                confidence=res.confidence
            ))
        elif res.match_type == "HIERARCHICAL":
            evidence_list.append(Evidence(
                type="hierarchical_match",
                category="Technical Skills",
                title=f"Hierarchical Subtitle: {req_name}",
                description=f"Candidate has experience with '{cand_name}', a sibling technology under the same category '{res.required_skill.category}'.",
                importance="medium",
                related_skill=req_name,
                confidence=res.confidence
            ))
        elif res.match_type == "TECHNOLOGY_FAMILY":
            evidence_list.append(Evidence(
                type="family_match",
                category="Technical Skills",
                title=f"Technology Family: {req_name}",
                description=f"Candidate has experience in '{cand_name}', part of the same technology family '{res.required_skill.technology_family}'.",
                importance="medium",
                related_skill=req_name,
                confidence=res.confidence
            ))
        elif res.match_type == "UNKNOWN":
            evidence_list.append(Evidence(
                type="unmatched",
                category="Technical Skills",
                title=f"Missing Skill: {req_name}",
                description=f"No matching or related skill for '{req_name}' was identified in candidate's profile.",
                importance="low",
                related_skill=req_name,
                confidence=0.0
            ))
            
    return evidence_list

def generate_experience_evidence(years: int, internships: int) -> List[Evidence]:
    """Generates Evidence for candidate professional experience."""
    effective_years = years + (internships * 0.5)
    description = f"Candidate has {years} years of professional experience"
    if internships > 0:
        description += f" and {internships} relevant internship(s) (counting as +{internships * 0.5} years of experience)"
    description += f" totaling {effective_exp_title(effective_years)}."
    
    return [
        Evidence(
            type="experience_record",
            category="Work Experience",
            title="Industry Experience Level",
            description=description,
            importance="high",
            confidence=1.0
        )
    ]

def generate_education_evidence(education: str) -> List[Evidence]:
    """Generates Evidence for candidate educational background."""
    desc_map = {
        "PhD": "Candidate holds a Doctorate (PhD) degree, representing the highest academic credential.",
        "Master": "Candidate has completed a Master's degree, indicating advanced academic specialization.",
        "Bachelor": "Candidate has completed a Bachelor's degree, fulfilling core academic guidelines.",
        "None": "No formal degree was detected in the candidate's parsed resume."
    }
    
    return [
        Evidence(
            type="education_level",
            category="Education",
            title="Academic Credentials",
            description=desc_map.get(education, f"Candidate has completed a {education} degree."),
            importance="high",
            confidence=1.0
        )
    ]

def generate_projects_evidence(count: int, target: Optional[int] = None) -> List[Evidence]:
    """Generates Evidence for technical projects."""
    from backend.services.policy.scoring_policy import default_scoring_policy
    if target is None:
        target = default_scoring_policy.project_target_count
    desc = f"Candidate has completed {count} technical projects."
    if count >= target:
        desc += f" This exceeds or meets the ideal target threshold of {target} projects."
    elif count > 0:
        desc += f" This partially satisfies the preferred threshold of {target} projects."
        
    return [
        Evidence(
            type="project_count",
            category="Projects",
            title="Technical Project Count",
            description=desc,
            importance="medium",
            confidence=1.0
        )
    ]

def generate_document_similarity_evidence(similarity_percentage: float) -> List[Evidence]:
    """Generates Evidence for overall text/vocabulary overlap (TF-IDF cosine)."""
    return [
        Evidence(
            type="document_similarity",
            category="Formatting & Similarty",
            title="Vocabulary Match (TF-IDF)",
            description=f"Raw text vocabulary overlap comparison check indicates {similarity_percentage:.1f}% term similarity with the job description.",
            importance="medium",
            confidence=1.0
        )
    ]

def effective_exp_title(years: float) -> str:
    if years >= 7:
        return f"{years} years (Senior Level)"
    elif years >= 3:
        return f"{years} years (Mid Level)"
    elif years >= 1:
        return f"{years} years (Junior Level)"
    return f"{years} years (Entry Level)"
