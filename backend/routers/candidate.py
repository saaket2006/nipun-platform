import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload

from backend.dependencies.auth_deps import require_candidate
from backend.database.database import get_db
from backend.models.models import User, Resume, JobDescription, ScanResult, CandidateProfile
from backend.models.enums import ResumeStatus
from backend.services.document_service import extract_text as parse_document_text
from backend.services.screening_service import screen_resumes
from backend.services.metadata_builder import build_analysis_metadata
from backend.schemas.schemas import CandidateProfileUpdate, UserProfileResponse
import time

logger = logging.getLogger("resume_screener")

router = APIRouter(prefix="/candidate", tags=["candidate"])

@router.get("/status")
def candidate_status():
    """Endpoint for checking candidate service status."""
    return {"status": "candidate service is active"}

@router.post("/process")
async def process_candidate_resume(
    job_description: str = Form(...),
    resume: UploadFile = File(...),
    label: Optional[str] = Form(None),
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    """
    Evaluates a candidate's resume against a pasted job description using the shared ATS engine.
    Persists the resume parsed text, job description, and scan results in database.
    Supports resume versioning, editable labels, and analysis snapshotting.
    """
    logger.info("Candidate endpoint called by user: %s", current_user.email)

    if not job_description:
        raise HTTPException(status_code=400, detail="Job description is required")
        
    if not resume or not resume.filename:
        raise HTTPException(status_code=400, detail="Resume file is required")

    filename = resume.filename
    try:
        content = await resume.read()
    except Exception as e:
        logger.error("Failed to read candidate resume file: %s", e)
        raise HTTPException(status_code=400, detail="Unreadable resume file")

    start_time = time.time()
    try:
        # 1. Parse/Extract text from resume
        raw_text = parse_document_text(content, filename)
    except ValueError as e:
        logger.error("Resume extraction failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # 2. Run screening using existing ATS service
        resumes_data = [{"filename": filename, "content": content}]
        results = await screen_resumes(job_description, resumes_data)
        
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Verify result exists
        if not results.get("results"):
            raise HTTPException(status_code=400, detail="Parsing failed to generate valid results")
            
        candidate_result = results["results"][0]

        # Determine version
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
        if profile:
            profile.resume_version_counter += 1
            version = profile.resume_version_counter
        else:
            # Fallback if profile doesn't exist
            version = 1

        # Default label if not provided
        if not label or not label.strip():
            label_val = f"Version {version}"
            label_source_val = "SYSTEM"
        else:
            label_val = label.strip()
            label_source_val = "USER"

        # 3. Create database records
        # Derive a clean, readable title from the job description (up to 250 chars)
        jd_clean = job_description.strip()
        lines = [l.strip() for l in jd_clean.splitlines() if l.strip()]
        first_line = lines[0] if lines else "Target Job Description"
        derived_title = first_line[:247] + "..." if len(first_line) > 250 else first_line

        # Save Job Description
        jd_model = JobDescription(
            owner_id=current_user.id,
            title=derived_title,
            description=job_description
        )
        db.add(jd_model)
        db.flush()

        from backend.services.pipeline import PersistenceStage
        
        persist_stage = PersistenceStage(db)
        persistence_result = persist_stage.execute(
            candidate_result["pipeline_context"],
            candidate_id=current_user.id,
            version=version,
            label=label_val,
            label_source=label_source_val,
            job_description_id=jd_model.id,
            ats_score=candidate_result["similarity_score"],
            elapsed_ms=elapsed_ms
        )
        
        if persistence_result.status != "success":
            raise HTTPException(status_code=500, detail=persistence_result.error_message)
            
        db.commit()
        
        # Retrieve stored resume for uploaded_at datetime
        stored_resume = db.query(Resume).filter(Resume.id == persistence_result.resume_id).first()
        resume_id_val = persistence_result.resume_id
        uploaded_at_val = stored_resume.uploaded_at.isoformat() if stored_resume else ""

        logger.info("Candidate resume analysis persisted successfully for ScanResult ID %d", persistence_result.scan_result_id)
        
        # Include resume versioning details and top-level xai/recommendations in the return result
        candidate_result["version"] = version
        candidate_result["label"] = label_val
        candidate_result["resume_id"] = resume_id_val
        candidate_result["uploaded_at"] = uploaded_at_val
        meta = candidate_result.get("analysis_metadata") or {}
        candidate_result["xai"] = meta.get("xai")
        candidate_result["recommendations"] = meta.get("recommendations")

        # Clean up pipeline events to prevent response serialization issues
        candidate_result.pop("pipeline_event", None)
        candidate_result.pop("pipeline_context", None)
        for r in results.get("results", []):
            r.pop("pipeline_event", None)
            r.pop("pipeline_context", None)

        return results

    except HTTPException:
        db.rollback()
        raise
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.exception("Error during candidate screening:")
        raise HTTPException(status_code=500, detail="Internal server error during screening")

@router.get("/resumes")
def get_candidate_resumes(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    """
    Retrieves all resume versions uploaded by the candidate, ordered by newest first.
    """
    logger.info("Candidate resumes list requested for user: %s", current_user.email)
    resumes = (
        db.query(Resume)
        .options(joinedload(Resume.scan_results).joinedload(ScanResult.job_description))
        .filter(Resume.candidate_id == current_user.id, Resume.status == ResumeStatus.ACTIVE)
        .order_by(Resume.version.desc())
        .all()
    )

    response_data = []
    for r in resumes:
        score = None
        jd_title = None
        jd_summary = None
        meta = {}
        if r.scan_results:
            scan = r.scan_results[0]
            score = scan.ats_score
            meta = scan.analysis_metadata or {}
            if scan.job_description:
                jd_title = scan.job_description.title
                jd_summary = scan.job_description.description[:100] + ("..." if len(scan.job_description.description) > 100 else "")
        response_data.append({
            "id": r.id,
            "version": r.version,
            "original_filename": r.original_filename,
            "label": r.label,
            "uploaded_at": r.uploaded_at.isoformat(),
            "ats_score": score,
            "job_description_title": jd_title,
            "job_description_summary": jd_summary,
            "analysis_metadata": {
                "profile_name": meta.get("profile_name") or "General Software Engineer",
                "profile_version": meta.get("profile_version") or "1.0.0",
                "engine_version": meta.get("engine_version") or meta.get("engine", {}).get("version") or "v1.0.0"
            }
        })

    return response_data

@router.get("/resumes/{resume_id}")
def get_candidate_resume_details(
    resume_id: int,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    """
    Retrieves full historical snapshot details for a specific resume version.
    """
    logger.info("Candidate resume details requested for resume ID %d, user: %s", resume_id, current_user.email)
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.candidate_id == current_user.id, Resume.status == ResumeStatus.ACTIVE)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume version not found")

    scan = resume.scan_results[0] if resume.scan_results else None
    score = scan.ats_score if scan else 0.0
    meta = scan.analysis_metadata if scan else {}

    # Backward compatibility: extract values from standardized nested structure or legacy flat keys
    cand_info = meta.get("candidate", {})
    score_categories = meta.get("score", {}).get("categories", {})
    skills_info = meta.get("skills", {})

    raw_jd_title = scan.job_description.title if scan and scan.job_description else ""
    raw_jd_desc = scan.job_description.description if scan and scan.job_description else ""

    # Heal legacy truncated titles (e.g., old entries truncated to 50 chars + "...")
    if raw_jd_title and raw_jd_title.endswith("...") and raw_jd_desc:
        prefix = raw_jd_title[:-3].strip()
        first_line = next((line.strip() for line in raw_jd_desc.splitlines() if line.strip()), "")
        if first_line.startswith(prefix):
            raw_jd_title = first_line[:247] + "..." if len(first_line) > 250 else first_line

    return {
        "id": resume.id,
        "version": resume.version,
        "label": resume.label,
        "original_filename": resume.original_filename,
        "file_type": resume.file_type,
        "uploaded_at": resume.uploaded_at.isoformat(),
        "ats_score": score,
        "job_description": {
            "title": raw_jd_title,
            "description": raw_jd_desc
        } if scan else None,
        "extracted_skills": skills_info.get("extracted") or meta.get("extracted_skills") or [],
        "matched_skills": skills_info.get("matched") or meta.get("matched_skills") or [],
        "missing_skills": skills_info.get("missing") or meta.get("missing_skills") or [],
        "candidate_details": {
            "name": cand_info.get("name") or meta.get("candidate_name", "N/A"),
            "email": cand_info.get("email") or meta.get("email", "N/A"),
            "phone": cand_info.get("phone") or meta.get("phone", "N/A"),
            "linkedin": cand_info.get("linkedin") or meta.get("linkedin", "N/A"),
            "github": cand_info.get("github") or meta.get("github", "N/A"),
            "experience": cand_info.get("experience") if "experience" in cand_info else meta.get("experience", 0),
            "education": cand_info.get("education") or meta.get("education", "N/A"),
            "projects": cand_info.get("projects") if "projects" in cand_info else meta.get("projects", 0),
            "skill_score": score_categories.get("skill_score") if "skill_score" in score_categories else meta.get("skill_score", 0.0),
            "experience_score": score_categories.get("experience_score") if "experience_score" in score_categories else meta.get("experience_score", 0.0),
            "education_score": score_categories.get("education_score") if "education_score" in score_categories else meta.get("education_score", 0.0),
            "projects_score": score_categories.get("projects_score") if "projects_score" in score_categories else meta.get("projects_score", 0.0)
        },
        "analysis_metadata": {
            "profile_name": meta.get("profile_name") or "General Software Engineer",
            "profile_version": meta.get("profile_version") or "1.0.0",
            "engine_version": meta.get("engine_version") or meta.get("engine", {}).get("version") or "v1.0.0"
        },
        "xai": meta.get("xai"),
        "recommendations": meta.get("recommendations")
    }

@router.delete("/resumes/{resume_id}")
def delete_candidate_resume(
    resume_id: int,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    """
    Deletes a single resume version. Deleting one version does not affect other versions.
    """
    logger.info("Candidate resume deletion requested for resume ID %d, user: %s", resume_id, current_user.email)
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.candidate_id == current_user.id, Resume.status == ResumeStatus.ACTIVE)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume version not found")

    resume.status = ResumeStatus.DELETED
    db.commit()
    return {"message": "Resume version deleted successfully"}

@router.put("/resumes/{resume_id}/label")
def update_candidate_resume_label(
    resume_id: int,
    payload: dict,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    """
    Updates the editable label of a specific resume version.
    """
    logger.info("Candidate resume label update requested for resume ID %d, user: %s", resume_id, current_user.email)
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.candidate_id == current_user.id, Resume.status == ResumeStatus.ACTIVE)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume version not found")

    new_label = payload.get("label")
    if not new_label or not new_label.strip():
        raise HTTPException(status_code=400, detail="Label cannot be empty")

    resume.label = new_label.strip()
    resume.label_source = "USER"
    db.commit()
    return {"message": "Label updated successfully", "label": resume.label}

@router.get("/stats")
def get_candidate_stats(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    """
    Retrieves latest ATS score details for candidate dashboard metrics.
    """
    logger.info("Candidate stats requested for user: %s", current_user.email)

    latest_scan = (
        db.query(ScanResult)
        .join(Resume)
        .filter(Resume.candidate_id == current_user.id, Resume.status == ResumeStatus.ACTIVE)
        .order_by(ScanResult.created_at.desc())
        .first()
    )

    if not latest_scan:
        return {"latest_ats_score": None}

    return {
        "latest_ats_score": latest_scan.ats_score,
        "last_analysis_date": latest_scan.created_at.isoformat(),
        "timestamp": latest_scan.created_at.isoformat()
    }

from pydantic import BaseModel

class UpdateRecommendationPayload(BaseModel):
    status: str  # ACTIVE, COMPLETED, DISMISSED, EXPIRED
    accepted_by_user: Optional[bool] = None

@router.put("/resumes/{resume_id}/recommendations/{rec_id}")
def update_recommendation_status(
    resume_id: int,
    rec_id: str,
    payload: UpdateRecommendationPayload,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    """
    Updates the lifecycle status and history flags of a specific recommendation
    inside the analysis_metadata of the resume's scan result.
    """
    logger.info("Recommendation status update requested for resume: %d, rec: %s", resume_id, rec_id)
    
    # 1. Fetch the resume and verify candidate ownership
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.candidate_id == current_user.id, Resume.status == ResumeStatus.ACTIVE)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume version not found")
        
    # 2. Get the scan result
    scan = resume.scan_results[0] if resume.scan_results else None
    if not scan:
        raise HTTPException(status_code=404, detail="Scan result not found for this resume version")
        
    # 3. Get analysis metadata
    meta = scan.analysis_metadata or {}
    recs_block = meta.get("recommendations", {})
    recs_list = recs_block.get("list", [])
    
    # 4. Find the recommendation
    found_rec = None
    import datetime
    for r in recs_list:
        if r.get("id") == rec_id:
            found_rec = r
            break
            
    if not found_rec:
        raise HTTPException(status_code=404, detail=f"Recommendation with ID '{rec_id}' not found in this analysis snapshot")
        
    # Valid statuses
    valid_statuses = ["ACTIVE", "COMPLETED", "DISMISSED", "EXPIRED"]
    status_upper = payload.status.upper()
    if status_upper not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status '{payload.status}'. Must be one of {valid_statuses}")
        
    # Update status and timestamps
    found_rec["status"] = status_upper
    if status_upper != "ACTIVE":
        found_rec["resolved_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    else:
        found_rec["resolved_at"] = None
        
    if payload.accepted_by_user is not None:
        found_rec["accepted_by_user"] = payload.accepted_by_user
    elif status_upper == "COMPLETED":
        found_rec["accepted_by_user"] = True
        
    # 5. Save changes
    from sqlalchemy.orm.attributes import flag_modified
    meta["recommendations"]["list"] = recs_list
    scan.analysis_metadata = meta
    flag_modified(scan, "analysis_metadata")
    db.commit()
    
    logger.info("Successfully updated recommendation '%s' status to %s", rec_id, status_upper)
    return {"message": "Recommendation status updated successfully", "recommendation": found_rec}


@router.patch("/profile", response_model=UserProfileResponse)
def update_candidate_profile(
    payload: CandidateProfileUpdate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    """
    Update candidate's profile information and display name.
    Strictly scoped to current_user.id derived from the verified Firebase token.
    Follows PATCH semantics: omitted fields remain unchanged.
    """
    logger.info("Candidate profile update requested for user: %s (id: %s)", current_user.email, current_user.id)

    # 1. Update display_name on users table if provided
    if payload.display_name is not None:
        current_user.display_name = payload.display_name

    # 2. Update CandidateProfile fields if any provided
    candidate_profile_updates = {
        k: v for k, v in [
            ("current_status", payload.current_status),
            ("field_of_study", payload.field_of_study),
            ("current_domain", payload.current_domain),
        ] if v is not None
    }

    if candidate_profile_updates:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
        if not profile:
            profile = CandidateProfile(
                user_id=current_user.id,
                current_status=payload.current_status or "Other",
                field_of_study=payload.field_of_study or "N/A",
                current_domain=payload.current_domain or "N/A"
            )
            db.add(profile)
        else:
            for field, val in candidate_profile_updates.items():
                setattr(profile, field, val)

    db.commit()
    db.refresh(current_user)
    if current_user.candidate_profile:
        db.refresh(current_user.candidate_profile)

    logger.info("Candidate profile updated successfully for user: %s", current_user.email)
    return current_user
