from sqlalchemy.orm import Session
from typing import Optional
import time
import logging
from typing import List, Dict
from backend.services.nlp_service import preprocess_text
from backend.services.skill_extractor import extract_skills
from backend.services.scoring_service import rank_candidates
from backend.services.pipeline import AnalysisPipeline
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger("resume_screener")


async def screen_resumes(
    job_description: str,
    resumes: List[Dict],
    db: Optional[Session] = None,
    profile_id: Optional[int] = None,
    custom_scoring_config: Optional[Dict] = None
) -> Dict:
    """
    Core business logic to screen and rank candidate resumes against a job description.
    Utilizes the event-driven AnalysisPipeline for each individual resume.
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("New screening request started: %d resume(s) uploaded", len(resumes))

    if not job_description:
        logger.warning("Screening request rejected: Job description is empty")
        raise ValueError("Job description is required")

    if not resumes:
        logger.warning("Screening request rejected: No resumes uploaded")
        raise ValueError("At least one resume must be uploaded")

    # Process Job Description
    clean_jd = await run_in_threadpool(preprocess_text, job_description)
    jd_skills_objs = await run_in_threadpool(extract_skills, job_description)
    jd_skills = [s.canonical_name.lower() for s in jd_skills_objs]
    logger.info("JD skills extracted (%d): %s", len(jd_skills), ", ".join(jd_skills))

    processed_resumes = []
    pipeline = AnalysisPipeline()

    pipeline_config = {}
    if custom_scoring_config:
        pipeline_config["custom_scoring"] = custom_scoring_config

    for resume in resumes:
        filename = resume.get("filename", "unknown_file")
        contents = resume.get("content", b"")

        # Execute Stages 1-7 of the analysis pipeline
        import uuid
        from backend.services.pipeline import AnalysisContext
        context = AnalysisContext(
            request_id=str(uuid.uuid4()),
            profile_id=profile_id,
            configuration=pipeline_config
        )
        recommendation_result = await pipeline.run_analysis(
            filename=filename,
            content_bytes=contents,
            job_description=job_description,
            clean_jd=clean_jd,
            db=db,
            context=context
        )

        if recommendation_result.status != "success":
            logger.warning("Resume pipeline failed for '%s': %s", filename, recommendation_result.error_message)
            processed_resumes.append({
                "filename": filename,
                "name": recommendation_result.error_message,
                "email": "N/A",
                "phone": "N/A",
                "matched_skills": [],
                "missing_skills": sorted(jd_skills)
            })
            continue

        # recommendation_result is the output of run_analysis (RecommendationBuiltEvent)
        scoring = recommendation_result.explanation.scoring
        matching = scoring.matching

        processed_resumes.append({
            "filename": filename,
            "name": scoring.candidate_name,
            "email": scoring.candidate_email,
            "phone": scoring.candidate_phone,
            "linkedin": scoring.candidate_linkedin,
            "github": scoring.candidate_github,
            "experience": scoring.candidate_experience,
            "internships": scoring.candidate_internships,
            "education": scoring.candidate_education,
            "projects": scoring.candidate_projects,
            "text": matching.skills.extraction.clean_text,
            "matched_skills": matching.matched_serialized,
            "missing_skills": matching.missing_serialized,
            "extracted_skills": [s.canonical_name for s in matching.skills.candidate_skills_objs],
            "similarity_score": scoring.similarity_score,
            "skill_score": scoring.skill_score,
            "experience_score": scoring.experience_score,
            "education_score": scoring.education_score,
            "projects_score": scoring.projects_score,
            "semantic_score": scoring.semantic_score,
            "semantic_data": matching.semantic_metadata_payload,
            "xai_explanations": recommendation_result.explanation.xai_explanations,
            "analysis_metadata": recommendation_result.explanation.analysis_metadata,
            "pipeline_event": recommendation_result,
            "pipeline_context": context
        })

        logger.info("Processed candidate: '%s' | Edu: %s | Exp: %d yrs | Internships: %d | Skills: %d matched, %d missing | Semantic Score: %.1f%%",
                    scoring.candidate_name, scoring.candidate_education, scoring.candidate_experience,
                    scoring.candidate_internships, len(matching.matched_serialized), len(matching.missing_serialized),
                    scoring.semantic_score)

    # Rank candidates using scoring logic
    ranked_candidates = await run_in_threadpool(rank_candidates, jd_skills, processed_resumes)
    logger.info("Ranking complete — %d candidates scored", len(ranked_candidates))

    # Clean up output and format the response structure
    final_response = []
    for cand in ranked_candidates:
        cand_dict = {
            "filename": cand["filename"],
            "name": cand["name"],
            "email": cand["email"],
            "phone": cand["phone"],
            "linkedin": cand.get("linkedin", "Not Provided"),
            "github": cand.get("github", "Not Provided"),
            "experience": cand.get("experience", 0),
            "education": cand.get("education", "None"),
            "projects": cand.get("projects", 0),
            "similarity_score": cand["similarity_score"],
            "skill_score": cand.get("skill_score", 0),
            "experience_score": cand.get("experience_score", 0),
            "education_score": cand.get("education_score", 0),
            "projects_score": cand.get("projects_score", 0),
            "rank": cand["rank"],
            "matched_skills": cand["matched_skills"],
            "missing_skills": cand["missing_skills"],
            "extracted_skills": cand.get("extracted_skills", cand["matched_skills"]),
            "semantic_score": cand.get("semantic_score", 0.0),
            "semantic_data": cand.get("semantic_data"),
            "xai_explanations": cand.get("xai_explanations"),
            "analysis_metadata": cand.get("analysis_metadata"),
            "pipeline_event": cand.get("pipeline_event"),
            "pipeline_context": cand.get("pipeline_context")
        }
        final_response.append(cand_dict)

    elapsed = round(time.time() - start_time, 2)
    for cand in final_response:
        logger.info("  #%d %-20s → Final: %.1f%% (Skill: %.1f | Exp: %.1f | Edu: %.1f | Proj: %.1f)",
                    cand["rank"], cand["name"], cand["similarity_score"],
                    cand["skill_score"], cand["experience_score"],
                    cand["education_score"], cand["projects_score"])
    logger.info("Request completed in %.2fs", elapsed)
    logger.info("=" * 60)

    applied_scoring_config = None
    if final_response:
        cand0 = final_response[0]
        meta0 = cand0.get("analysis_metadata") or {}
        applied_scoring_config = {
            "is_custom": meta0.get("is_custom_scoring", False),
            "profile_id": meta0.get("profile_id"),
            "profile_name": meta0.get("profile_name", "General Software Engineer"),
            "component_weights": meta0.get("component_weights", {"skills": 0.50, "experience": 0.25, "education": 0.15, "projects": 0.10}),
            "scoring_thresholds": meta0.get("scoring_thresholds", {"max_experience_years": 10.0, "project_target_count": 3})
        }

    return {
        "results": final_response,
        "jd_skills": sorted(jd_skills),
        "scoring_config": applied_scoring_config
    }
