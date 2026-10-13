from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, Depends
from typing import List
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.services.screening_service import screen_resumes
from backend.limiter import limiter
from backend.dependencies.auth_deps import require_recruiter
from backend.database.database import get_db
from backend.models.models import User, JobDescription, Resume, ScanResult, RecruiterProfile
from backend.models.enums import CompanyType
from backend.schemas.schemas import RecruiterProfileUpdate, UserProfileResponse

logger = logging.getLogger("resume_screener")

router = APIRouter(prefix="/recruiter", tags=["recruiter"])

from typing import Optional

@router.post("/process")
@limiter.limit("5/minute")
async def process_resumes(
    request: Request,
    job_description: Optional[str] = Form(None),
    jd_id: Optional[int] = Form(None),
    profile_id: Optional[int] = Form(None),
    resumes: List[UploadFile] = File(...),
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """
    Screens uploaded resume files against a job description.
    Enforces authentication and recruiter role verification.
    Persists screening results inside the database for dashboard statistics.
    """
    logger.info("Recruiter endpoint called by user: %s", current_user.email)
    
    # Resolve Form default objects if called directly
    if not isinstance(jd_id, int):
        try:
            jd_id = int(jd_id)
        except (TypeError, ValueError):
            jd_id = None

    if not isinstance(profile_id, int):
        try:
            profile_id = int(profile_id)
        except (TypeError, ValueError):
            profile_id = None
    if jd_id:
        jd_model = db.query(JobDescription).filter(
            JobDescription.id == jd_id,
            JobDescription.owner_id == current_user.id
        ).first()
        if not jd_model:
            raise HTTPException(status_code=404, detail="Job description not found in your library")
        jd_text = jd_model.description
    else:
        if not job_description or not job_description.strip():
            raise HTTPException(status_code=400, detail="Job description text is required when no jd_id is provided")
        jd_text = job_description
        # Save new Job Description into library
        jd_model = JobDescription(
            owner_id=current_user.id,
            title=job_description[:50] + ("..." if len(job_description) > 50 else ""),
            description=job_description
        )
        db.add(jd_model)
        db.flush()  # Obtain jd_model.id
        
    if not resumes:
        raise HTTPException(status_code=400, detail="At least one resume must be uploaded")
        
    resumes_data = []
    for resume in resumes:
        filename = resume.filename
        if not filename:
            continue
        try:
            content = await resume.read()
            resumes_data.append({
                "filename": filename,
                "content": content
            })
        except Exception as e:
            logger.error("Failed to read uploaded resume file '%s': %s", filename, e)
            
    try:
        results = await screen_resumes(jd_text, resumes_data, db=db, profile_id=profile_id)
        
        # Save each parsed candidate resume and scan result
        from backend.services.pipeline import PersistenceStage
        persist_stage = PersistenceStage(db)

        batch_args = []
        for cand in results.get("results", []):
            # Skip invalid/error files from saving
            if cand.get("email") == "N/A" and cand.get("name") in ("Unsupported/Invalid File", "File Too Large (>5MB)"):
                continue
                
            pipeline_ctx = cand["pipeline_context"]
            
            batch_args.append({
                "arg": pipeline_ctx,
                "kwargs": {
                    "candidate_id": None,
                    "version": 1,
                    "label": None,
                    "label_source": "SYSTEM",
                    "job_description_id": jd_model.id,
                    "ats_score": cand["similarity_score"],
                    "elapsed_ms": 0
                }
            })
            
        if batch_args:
            batch_results = persist_stage.execute_batch(batch_args)
            for res in batch_results:
                # If it's a context, the event is nested
                event = res.event if hasattr(res, 'event') else res
                if event.status != "success":
                    raise HTTPException(status_code=500, detail=event.error_message)

        db.commit()
        logger.info("Screening persisted successfully for job description ID %d", jd_model.id)
        
        for cand in results.get("results", []):
            cand.pop("pipeline_event", None)
            cand.pop("pipeline_context", None)
            
        return results
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.exception("Error during screening:")
        raise HTTPException(status_code=500, detail="Internal server error during screening")

@router.get("/profiles")
def get_scoring_profiles(
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """
    Returns all configured and seeded scoring profiles.
    """
    from backend.models.models import ScoringProfile
    profiles = db.query(ScoringProfile).order_by(ScoringProfile.name).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "target_role": p.target_role,
            "experience_level": p.experience_level,
            "domain": p.domain,
            "weights": p.weights,
            "is_default": p.is_default
        }
        for p in profiles
    ]

# ==========================================
# JD Library CRUD Endpoints
# ==========================================

@router.get("/jobs")
def list_job_descriptions(
    include_archived: bool = False,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """
    Retrieves all job descriptions created by the recruiter.
    """
    query = db.query(JobDescription).filter(JobDescription.owner_id == current_user.id)
    if not include_archived:
        query = query.filter(JobDescription.is_archived == False)
    jds = query.order_by(JobDescription.created_at.desc()).all()
    return [
        {
            "id": j.id,
            "title": j.title,
            "subtitle": j.subtitle,
            "description": j.description,
            "company": j.company,
            "optional_notes": j.optional_notes,
            "is_archived": j.is_archived,
            "created_at": j.created_at.isoformat()
        }
        for j in jds
    ]

@router.post("/jobs")
def create_job_description(
    title: str = Form(...),
    subtitle: Optional[str] = Form(None),
    description: str = Form(...),
    company: Optional[str] = Form(None),
    optional_notes: Optional[str] = Form(None),
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """
    Adds a new job description to the recruiter's library.
    """
    jd = JobDescription(
        owner_id=current_user.id,
        title=title,
        subtitle=subtitle,
        description=description,
        company=company,
        optional_notes=optional_notes
    )
    db.add(jd)
    db.commit()
    return {"message": "Job description created successfully", "id": jd.id}

@router.put("/jobs/{jd_id}")
def update_job_description(
    jd_id: int,
    title: str = Form(...),
    subtitle: Optional[str] = Form(None),
    description: str = Form(...),
    company: Optional[str] = Form(None),
    optional_notes: Optional[str] = Form(None),
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """
    Edits an existing job description in the recruiter's library.
    """
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.owner_id == current_user.id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
        
    jd.title = title
    jd.subtitle = subtitle
    jd.description = description
    jd.company = company
    jd.optional_notes = optional_notes
    db.commit()
    return {"message": "Job description updated successfully"}

@router.delete("/jobs/{jd_id}")
def archive_job_description(
    jd_id: int,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """
    Soft-deletes (archives) a job description.
    """
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.owner_id == current_user.id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
        
    jd.is_archived = True
    db.commit()
    return {"message": "Job description archived successfully"}

@router.delete("/jobs/{jd_id}/delete")
def delete_job_description(
    jd_id: int,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """
    Permanently deletes a job description and its scan results.
    """
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.owner_id == current_user.id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
        
    db.delete(jd)
    db.commit()
    return {"message": "Job description and all associated results deleted permanently"}

# ==========================================
# Dashboard & Recruiter Stats Route
# ==========================================

@router.get("/stats")
def get_recruiter_stats(
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """
    Retrieves dashboard statistics and aggregates recruiter intelligence statistics.
    """
    logger.info("Recruiter stats requested for user: %s", current_user.email)
    
    from sqlalchemy import func
    
    # 1. Calculate aggregates directly in the database
    stats = db.query(
        func.count(ScanResult.id),
        func.avg(ScanResult.ats_score)
    ).join(JobDescription).filter(JobDescription.owner_id == current_user.id).first()

    total_candidates = stats[0] or 0
    avg_score = round(stats[1], 1) if stats[1] is not None else 0.0
        
    # Intelligence statistics
    experience_sum = 0.0
    experience_count = 0
    education_counts = {}
    missing_skills_counts = {}
    matched_skills_counts = {}
    improvement_counts = {}
    
    # 2. Fetch only the required JSON data for intelligence stats
    metadata_records = db.query(ScanResult.analysis_metadata).join(
        JobDescription
    ).filter(JobDescription.owner_id == current_user.id).all()

    for row in metadata_records:
        meta = row[0] or {}
        candidate_info = meta.get("candidate", {})
        
        # 1. Experience
        exp = candidate_info.get("experience")
        if exp is not None:
            try:
                experience_sum += float(exp)
                experience_count += 1
            except (ValueError, TypeError):
                pass
                
        # 2. Education
        edu = candidate_info.get("education")
        if edu:
            education_counts[edu] = education_counts.get(edu, 0) + 1
            
        # 3. Missing Skills
        skills_info = meta.get("skills", {})
        missing = skills_info.get("missing", [])
        for skill in missing:
            skill_lower = skill.strip().lower()
            if skill_lower:
                missing_skills_counts[skill_lower] = missing_skills_counts.get(skill_lower, 0) + 1
                
        # 4. Matched Skills
        matched = skills_info.get("matched", [])
        for skill in matched:
            skill_lower = skill.strip().lower()
            if skill_lower:
                matched_skills_counts[skill_lower] = matched_skills_counts.get(skill_lower, 0) + 1
                
        # 5. Recommended improvements
        recs = meta.get("recommendations", {}).get("list", [])
        for r in recs:
            title = r.get("title")
            if title:
                improvement_counts[title] = improvement_counts.get(title, 0) + 1
                
    # Format and sort aggregates
    avg_experience = round(experience_sum / experience_count, 1) if experience_count > 0 else 0.0
    
    common_missing = sorted(
        [{"skill": k, "count": v} for k, v in missing_skills_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]
    
    common_matched = sorted(
        [{"skill": k, "count": v} for k, v in matched_skills_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]
    
    top_improvements = sorted(
        [{"recommendation": k, "count": v} for k, v in improvement_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]
    
    most_common_edu = "None"
    if education_counts:
        most_common_edu = max(education_counts, key=education_counts.get)
        
    return {
        "total_candidates_screened": total_candidates,
        "average_ats_score": avg_score,
        "average_experience_tenure": avg_experience,
        "most_common_education_level": most_common_edu,
        "most_common_missing_skills": common_missing,
        "most_common_matched_skills": common_matched,
        "top_recommended_improvements": top_improvements,
        "education_breakdown": [{"level": k, "count": v} for k, v in education_counts.items()]
    }


@router.patch("/profile", response_model=UserProfileResponse)
def update_recruiter_profile(
    payload: RecruiterProfileUpdate,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """
    Update recruiter's profile information and display name.
    Strictly scoped to current_user.id derived from the verified Firebase token.
    Follows PATCH semantics: omitted fields remain unchanged.
    """
    logger.info("Recruiter profile update requested for user: %s (id: %s)", current_user.email, current_user.id)

    # 1. Update display_name on users table if provided
    if payload.display_name is not None:
        current_user.display_name = payload.display_name

    # 2. Update RecruiterProfile fields if any provided
    recruiter_profile_updates = {
        k: v for k, v in [
            ("company_name", payload.company_name),
            ("company_type", payload.company_type),
            ("hiring_domain", payload.hiring_domain),
        ] if v is not None
    }

    if recruiter_profile_updates:
        profile = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == current_user.id).first()
        if not profile:
            profile = RecruiterProfile(
                user_id=current_user.id,
                company_name=payload.company_name or "N/A",
                company_type=payload.company_type or CompanyType.OTHER,
                hiring_domain=payload.hiring_domain or "N/A"
            )
            db.add(profile)
        else:
            for field, val in recruiter_profile_updates.items():
                setattr(profile, field, val)

    db.commit()
    db.refresh(current_user)
    if current_user.recruiter_profile:
        db.refresh(current_user.recruiter_profile)

    logger.info("Recruiter profile updated successfully for user: %s", current_user.email)
    return current_user
