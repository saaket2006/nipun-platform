from typing import List, Dict, Any, Optional
from backend.services.xai.models import ScoreComponent, ExplanationItem, StructuredExplanations
from backend.services.xai.formatter import (
    format_skills_explanation,
    format_experience_explanation,
    format_education_explanation,
    format_projects_explanation,
    format_document_similarity_explanation,
    format_overall_explanation
)

class XaiEngine:
    """
    Explainable AI Explanation Engine.
    Receives structured ScoreComponents and generates multi-level presentation-independent explanations.
    """
    
    def generate_explanations(self, components: List[ScoreComponent]) -> Dict[str, Dict[str, Any]]:
        """
        Generates structured multi-level explanations (SUMMARY, DETAILED, TECHNICAL)
        for all score components.
        """
        explanations = {}
        
        # Helper to find a component by name
        def find_comp(name: str) -> Optional[ScoreComponent]:
            return next((c for c in components if c.name.lower() == name.lower()), None)
            
        # 1. Technical Skills Explanation
        skills_comp = find_comp("Technical Skills")
        if skills_comp:
            # We recover matches and missing lists from component details if stored,
            # or pass down the evidence list for extraction.
            matched = [e.related_skill for e in skills_comp.evidence if e.type != "unmatched" and e.related_skill]
            missing = [e.related_skill for e in skills_comp.evidence if e.type == "unmatched" and e.related_skill]
            
            explanations["skills"] = self._build_explanations_dict(
                name="Technical Skills",
                comp=skills_comp,
                formatter_func=lambda raw_score, lvl: format_skills_explanation(
                    raw_score=raw_score,
                    matched=matched,
                    missing=missing,
                    evidence_list=skills_comp.evidence,  # Can use evidence as source
                    level=lvl
                )
            )
            
        # 2. Experience Explanation
        exp_comp = find_comp("Work Experience")
        if exp_comp:
            # Try to extract details from description
            years = 0
            internships = 0
            if exp_comp.evidence:
                desc = exp_comp.evidence[0].description
                # Parse years and internships out of description or pass dummy fallback
                import re
                years_match = re.search(r"has (\d+) years", desc)
                interns_match = re.search(r"and (\d+) relevant", desc)
                if years_match:
                    years = int(years_match.group(1))
                if interns_match:
                    internships = int(interns_match.group(1))
                    
            explanations["experience"] = self._build_explanations_dict(
                name="Work Experience",
                comp=exp_comp,
                formatter_func=lambda raw_score, lvl: format_experience_explanation(
                    raw_score=raw_score,
                    years=years,
                    internships=internships,
                    level=lvl
                )
            )
            
        # 3. Education Explanation
        edu_comp = find_comp("Education")
        if edu_comp:
            edu_level = "None"
            if edu_comp.evidence:
                desc = edu_comp.evidence[0].description
                if "Doctorate" in desc or "PhD" in desc:
                    edu_level = "PhD"
                elif "Master" in desc:
                    edu_level = "Master"
                elif "Bachelor" in desc:
                    edu_level = "Bachelor"
                    
            explanations["education"] = self._build_explanations_dict(
                name="Education",
                comp=edu_comp,
                formatter_func=lambda raw_score, lvl: format_education_explanation(
                    raw_score=raw_score,
                    education=edu_level,
                    level=lvl
                )
            )
            
        # 4. Projects Explanation
        proj_comp = find_comp("Projects")
        if proj_comp:
            count = 0
            if proj_comp.evidence:
                desc = proj_comp.evidence[0].description
                import re
                count_match = re.search(r"completed (\d+)", desc)
                if count_match:
                    count = int(count_match.group(1))
                    
            explanations["projects"] = self._build_explanations_dict(
                name="Projects",
                comp=proj_comp,
                formatter_func=lambda raw_score, lvl: format_projects_explanation(
                    raw_score=raw_score,
                    count=count,
                    level=lvl
                )
            )
            
        # 5. Document Similarity Explanation
        sim_comp = find_comp("Document Similarity")
        if sim_comp:
            explanations["document_similarity"] = self._build_explanations_dict(
                name="Document Similarity",
                comp=sim_comp,
                formatter_func=lambda raw_score, lvl: format_document_similarity_explanation(
                    raw_score=raw_score,
                    level=lvl
                )
            )
            
        # 6. Overall Score Explanation
        overall_comp = find_comp("Overall Score")
        if overall_comp:
            explanations["overall"] = self._build_explanations_dict(
                name="Overall Score",
                comp=overall_comp,
                formatter_func=lambda raw_score, lvl: format_overall_explanation(
                    raw_score=raw_score,
                    level=lvl
                )
            )
            
        return explanations

    def _build_explanations_dict(self, name: str, comp: ScoreComponent, formatter_func: Any) -> Dict[str, Any]:
        """
        Helper to construct a dict representation of StructuredExplanations.
        """
        levels = ["SUMMARY", "DETAILED", "TECHNICAL"]
        result = {}
        
        for lvl in levels:
            why_awarded, why_deducted = formatter_func(comp.raw_score, lvl)
            
            # Serialize evidence list as dictionaries (suppress per-skill evidence for Technical Skills,
            # as the consolidated Technical Skills Overview provides Matched and Missing skills)
            if "skill" in name.lower() or "skill" in comp.name.lower():
                evidence_dicts = []
            else:
                evidence_dicts = [
                    {
                        "type": ev.type,
                        "category": ev.category,
                        "title": ev.title,
                        "description": ev.description,
                        "importance": ev.importance,
                        "related_skill": ev.related_skill,
                        "confidence": ev.confidence
                    } for ev in comp.evidence
                ]
            
            result[lvl.lower()] = {
                "why_awarded": why_awarded,
                "why_deducted": why_deducted,
                "supporting_evidence": evidence_dicts
            }
            
        return result
