from typing import List, Dict, Any, Optional

def format_skills_explanation(raw_score: float, matched: List[str], missing: List[str], evidence_list: List[Any], level: str) -> tuple:
    """
    Returns (why_awarded, why_deducted) for Skill Matching component.
    """
    matched_title = [m.title() for m in matched]
    missing_title = [m.title() for m in missing]
    
    if level == "SUMMARY":
        why_awarded = f"Matched required skills: {', '.join(matched_title)}." if matched_title else "No required skills matched."
        why_deducted = f"Missing required skills: {', '.join(missing_title)}." if missing_title else "All required skills matched."
        return why_awarded, why_deducted
        
    elif level == "DETAILED":
        exacts = []
        semantics = []
        for ev in evidence_list:
            is_dict = isinstance(ev, dict)
            ev_type = ev["type"] if is_dict else ev.type
            related = ev["related_skill"] if is_dict else ev.related_skill
            
            if not related:
                continue
            if ev_type == "exact_match":
                exacts.append(related)
            elif ev_type in ("alias_match", "abbreviation_match", "hierarchical_match", "family_match"):
                semantics.append(related)
                
        reasons = []
        if exacts:
            reasons.append(f"exact matches for {', '.join(exacts)}")
        if semantics:
            reasons.append(f"semantic matches for {', '.join(semantics)}")
            
        why_awarded = f"Awarded points for matching {len(matched)} required skill(s) out of {len(matched) + len(missing)}: "
        if reasons:
            why_awarded += f"demonstrates {', '.join(reasons)}."
        else:
            why_awarded += "no technical skills matched."
            
        why_deducted = f"Points deducted for {len(missing)} missing required skill(s): {', '.join(missing_title)}." if missing_title else "Zero deductions. Meets all requested core tech requirements."
        return why_awarded, why_deducted
        
    else:  # TECHNICAL
        details = []
        for ev in evidence_list:
            is_dict = isinstance(ev, dict)
            ev_type = ev["type"] if is_dict else ev.type
            related = ev["related_skill"] if is_dict else ev.related_skill
            conf = ev["confidence"] if is_dict else ev.confidence
            if related:
                details.append(f"[{related}: {ev_type} (conf={conf})]")
            
        why_awarded = f"Match resolved with overall skill score of {raw_score:.1f}%. Mapping resolution paths: {'; '.join(details)}."
        why_deducted = f"Deduction penalty applied for OOV/Unmatched nodes: {', '.join(missing_title)}." if missing_title else "No unmatched node penalties applied."
        return why_awarded, why_deducted

def format_experience_explanation(raw_score: float, years: int, internships: int, level: str) -> tuple:
    """
    Returns (why_awarded, why_deducted) for Experience component.
    """
    effective_years = years + (internships * 0.5)
    
    if level == "SUMMARY":
        why_awarded = f"Possesses {years} years of professional experience plus {internships} internship(s)."
        why_deducted = "Experience is below the preferred target of 10 years." if effective_years < 10 else "Meets or exceeds target experience requirements."
        return why_awarded, why_deducted
        
    elif level == "DETAILED":
        why_awarded = f"Awarded {raw_score:.1f}% for work history. Professional tenure is {years} years, augmented by {internships} relevant internship(s) adding {internships * 0.5} years of effective tenure."
        why_deducted = f"Deduction applied because effective tenure ({effective_years} years) is below the maximum scoring threshold of 10 years." if effective_years < 10 else "No deduction applied. Seniority criteria satisfied."
        return why_awarded, why_deducted
        
    else:  # TECHNICAL
        why_awarded = f"Score = min(((tenure_professional ({years}) + (tenure_internship ({internships}) * 0.5)) / 10.0) * 100, 100) = {raw_score:.1f}%."
        why_deducted = f"Unsatisfied target delta: {max(0.0, 10.0 - effective_years):.1f} years remaining to maximize scale weight."
        return why_awarded, why_deducted

def format_education_explanation(raw_score: float, education: str, level: str) -> tuple:
    """
    Returns (why_awarded, why_deducted) for Education component.
    """
    if level == "SUMMARY":
        why_awarded = f"Completed a {education} degree." if education != "None" else "No formal degree was parsed in candidate profile."
        why_deducted = "Lacks an advanced degree (Master or PhD)." if education in ("Bachelor", "None") else "Completed advanced study requirements."
        return why_awarded, why_deducted
        
    elif level == "DETAILED":
        why_awarded = f"Earned {raw_score:.1f}% score contribution. Candidate has completed a {education} level degree."
        why_deducted = "Deduction applies as candidate holds a basic Bachelor's level degree, whereas Master's (80%) or PhD (100%) earns higher preference." if education in ("Bachelor", "None") else "No deductions. Level of study meets highest tier parameters."
        return why_awarded, why_deducted
        
    else:  # TECHNICAL
        why_awarded = f"Study resolution maps level '{education}' to class score = {raw_score:.1f}%."
        why_deducted = f"Study level differential penalty applied (Max score possible is 100% for PhD, current is {raw_score:.1f}%)."
        return why_awarded, why_deducted

def format_projects_explanation(raw_score: float, count: int, level: str) -> tuple:
    """
    Returns (why_awarded, why_deducted) for Projects component.
    """
    if level == "SUMMARY":
        why_awarded = f"Completed {count} technical project(s)."
        why_deducted = "Projects count is below the preferred target of 3 projects." if count < 3 else "Satisfies project experience standards."
        return why_awarded, why_deducted
        
    elif level == "DETAILED":
        why_awarded = f"Awarded {raw_score:.1f}% project score contribution for completing {count} matching project(s) parsed in resume."
        why_deducted = f"Deduction applied because candidate project count ({count}) is below target threshold of 3 projects." if count < 3 else "No deductions applied. Adequate project volume."
        return why_awarded, why_deducted
        
    else:  # TECHNICAL
        why_awarded = f"Project metric score = (count ({count}) / 3.0) * 100 = {raw_score:.1f}%."
        why_deducted = f"Project gap penalty applied: {max(0, 3 - count)} project(s) remaining for maximum category score."
        return why_awarded, why_deducted

def format_document_similarity_explanation(raw_score: float, level: str) -> tuple:
    """
    Returns (why_awarded, why_deducted) for Document Similarity.
    """
    if level == "SUMMARY":
        why_awarded = f"Demonstrates {raw_score:.1f}% vocabulary/text overlap with the job description."
        why_deducted = "Lacks perfect keyword alignments or contains out-of-vocabulary skills."
        return why_awarded, why_deducted
        
    elif level == "DETAILED":
        why_awarded = f"Vocabulary matching (TF-IDF vector cosine overlap) yields {raw_score:.1f}% overlap. This assesses lexical structure alignment with JD skills."
        why_deducted = f"Deduction represents the {(100.0 - raw_score):.1f}% difference in term frequencies and lexical composition."
        return why_awarded, why_deducted
        
    else:  # TECHNICAL
        why_awarded = f"TF-IDF cosine similarity matrix intersection is resolved at {raw_score / 100.0:.4f}."
        why_deducted = f"Lexical distance (1 - cosine_similarity) accounts for {1.0 - (raw_score / 100.0):.4f} distance vector."
        return why_awarded, why_deducted

def format_overall_explanation(raw_score: float, level: str) -> tuple:
    """
    Returns (why_awarded, why_deducted) for Overall Score.
    """
    if level == "SUMMARY":
        why_awarded = f"Earned an overall ATS matching score of {raw_score:.1f}%."
        why_deducted = "Result is weighted average of skills (50%), experience (25%), education (15%), and projects (10%)."
        return why_awarded, why_deducted
        
    elif level == "DETAILED":
        why_awarded = f"ATS ranking resolved overall score of {raw_score:.1f}% as a weighted combination of constituent components."
        why_deducted = "Component gaps in technical skills, experience tenure, or study degrees reduce overall matching potential."
        return why_awarded, why_deducted
        
    else:  # TECHNICAL
        why_awarded = f"ATS Score = (skill_score * 0.50) + (exp_score * 0.25) + (edu_score * 0.15) + (proj_score * 0.10) = {raw_score:.1f}%."
        why_deducted = "Overall deficit is the linear combination of individual sub-score deltas."
        return why_awarded, why_deducted
