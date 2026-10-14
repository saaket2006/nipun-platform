import re
from typing import List, Any
from backend.services.recommendations.models import Recommendation
from backend.services.policy.recommendation_policy import default_recommendation_policy
from backend.services.policy.scoring_policy import default_scoring_policy
from backend.services.recommendations.estimator import (
    estimate_missing_skill_gain,
    estimate_experience_gain,
    estimate_education_gain,
    estimate_project_gain
)

def generate_heuristics_recommendations(scoring_event: Any) -> List[Recommendation]:
    """
    Generates deterministic recommendations based on candidate scoring results and metadata.
    Does NOT require an LLM to be present.
    """
    recommendations = []
    
    # Extract scoring profile weights if available
    profile_resolved = getattr(scoring_event, "profile_resolved", None)
    weights = profile_resolved.weights if profile_resolved else None

    # 1. Missing Technical Skills
    # Extract missing skills from scoring event matching
    missing_skills_info = [] # List of (skill_name, weight)
    
    # Check match results inside event
    matching = getattr(scoring_event, "matching", None)
    if matching and hasattr(matching, "match_results"):
        for res in matching.match_results:
            if res.match_type == "UNKNOWN":
                missing_skills_info.append((
                    res.required_skill.canonical_name,
                    res.weight
                ))
                
    # Sort missing skills by weight descending
    missing_skills_info = sorted(missing_skills_info, key=lambda x: -x[1])
    
    # Limit number of skill recommendations
    limit = default_recommendation_policy.max_skills_recommendations
    for name, weight in missing_skills_info[:limit]:
        # Determine priority
        if weight >= default_recommendation_policy.critical_missing_skill_weight:
            priority = "CRITICAL"
        elif weight >= default_recommendation_policy.high_missing_skill_weight:
            priority = "HIGH"
        elif weight >= 0.20:
            priority = "MEDIUM"
        else:
            priority = "LOW"
            
        gain = estimate_missing_skill_gain(weight, weights)
        
        recommendations.append(Recommendation(
            id=f"skill_missing_{name.lower().replace(' ', '_')}",
            title=f"Showcase Skill: {name}",
            description=f"This skill is a primary technical requirement for the role. Try adding it to your skills or project descriptions.",
            priority=priority,
            category="Skills",
            reason=f"Skill is listed in the job description with a high match weight of {weight:.2f}.",
            source="SEMANTIC",
            related_skills=[name],
            estimated_score_gain=gain,
            confidence=1.0
        ))
        
    # 2. Experience Tenure Gap
    exp_years = scoring_event.candidate_experience
    exp_score = scoring_event.experience_score
    if exp_years < 10:
        if exp_score < default_recommendation_policy.critical_threshold:
            priority = "CRITICAL"
        elif exp_score < default_recommendation_policy.high_threshold:
            priority = "HIGH"
        else:
            priority = "MEDIUM"
            
        gain = estimate_experience_gain(exp_years, weights)
        
        recommendations.append(Recommendation(
            id="experience_tenure_gap",
            title="Highlight Professional Experience",
            description="The role prefers candidates with stronger experience. Ensure you list all previous developer tenures, internships, and freelance projects.",
            priority=priority,
            category="Experience",
            reason=f"Your effective experience is {exp_years} year(s), which is below the maximum scoring threshold of 10 years.",
            source="RULE",
            estimated_score_gain=gain,
            confidence=1.0
        ))
        
    # 3. Education Gap
    edu_level = scoring_event.candidate_education
    edu_score = scoring_event.education_score
    if edu_level in ("Bachelor", "None"):
        priority = "HIGH" if edu_level == "None" else "MEDIUM"
        gain = estimate_education_gain(edu_level, weights)
        
        recommendations.append(Recommendation(
            id="education_degree_gap",
            title="Add Certifications or Academic Gaps",
            description="Lacks an advanced degree. Consider showcasing online certificates, bootcamps, or specialized developer certifications to boost your educational profile.",
            priority=priority,
            category="Education",
            reason=f"Academic level resolved as '{edu_level}', whereas Master or PhD-level study scores higher matching preferences.",
            source="RULE",
            estimated_score_gain=gain,
            confidence=1.0
        ))
        
    # 4. Project Count Gap
    proj_count = scoring_event.candidate_projects
    target_projects = default_scoring_policy.project_target_count
    if proj_count < target_projects:
        priority = "HIGH" if proj_count < 2 else "MEDIUM"
        gain = estimate_project_gain(proj_count, weights)
        
        recommendations.append(Recommendation(
            id="project_count_gap",
            title="Showcase More Technical Projects",
            description="List 1-2 more hands-on technical projects on your resume that feature the requested technologies (e.g. build open-source or portfolio work).",
            priority=priority,
            category="Projects",
            reason=f"Only {proj_count} project(s) matching tech requirements were identified, which is below the target threshold of {target_projects} projects.",
            source="RULE",
            estimated_score_gain=gain,
            confidence=1.0
        ))
        
    # 5. Quantified Achievements Heuristic (Check regex metrics)
    raw_text = getattr(scoring_event, "extracted_text", "")
    if not raw_text and matching and hasattr(matching, "skills") and hasattr(matching.skills, "extraction"):
        raw_text = matching.skills.extraction.raw_text
        
    if raw_text:
        # Simple check for numbers, percentages, or metrics in text
        metrics_pattern = re.compile(r"\d+%\s*|\d+\s*year|\d+\s*million|\d+\s*k|\$\d+", re.IGNORECASE)
        matches = metrics_pattern.findall(raw_text)
        if len(matches) < 3:
            recommendations.append(Recommendation(
                id="quantified_achievements_missing",
                title="Add Measurable Impact & Metrics",
                description="Describe your past roles using numbers and impact rather than just tasks (e.g. 'Reduced loading time by 20%' or 'Managed a database of 1M rows').",
                priority="MEDIUM",
                category="General",
                reason="Few numerical metrics or quantifiable business outcomes were identified in your resume text.",
                source="RULE",
                estimated_score_gain=2.0,
                confidence=0.8
            ))
            
    return recommendations
