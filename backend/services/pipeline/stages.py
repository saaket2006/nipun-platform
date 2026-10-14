
import logging
import json
import traceback
import datetime
from typing import Any, Optional, Dict, List
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.config import settings
from backend.services.nlp_service import preprocess_text
from backend.services.skill_extractor import extract_skills
from backend.services.document_service import extract_text
from backend.services.info_extractor import (
    extract_name, extract_email, extract_phone, extract_linkedin,
    extract_github, extract_experience, extract_relevant_internships,
    extract_education, extract_projects
)
from backend.services.semantic.matcher import SemanticMatcher
from backend.services.semantic.scorer import SemanticScorer
from backend.services.metadata_builder import build_analysis_metadata
from backend.services.policy.scoring_policy import default_scoring_policy
from backend.services.policy.scoring_profile_policy import default_scoring_profile_policy
from backend.models.models import Resume, ScanResult, ScoringProfile
from backend.models.enums import ResumeStatus

from backend.services.pipeline.context import AnalysisContext
from backend.services.pipeline.events import (
    PipelineEvent, ResumeExtractedEvent, SkillsExtractedEvent,
    SemanticMatchedEvent, ProfileResolvedEvent, ScoredEvent,
    ExplanationBuiltEvent, RecommendationBuiltEvent, PersistenceEvent
)

logger = logging.getLogger("resume_screener")

class PipelineStageException(Exception):
    """Exception raised by a pipeline stage during execution."""
    pass

class PipelineStage(ABC):
    """Abstract base class representing a single pipeline stage."""

    @abstractmethod
    def execute(self, event: Any) -> Any:
        pass


class ResumeTextExtractionStage(PipelineStage):
    """Stage 1: Validates and extracts raw text from resume bytes."""

    async def execute(self, arg: Any) -> Any:
        is_context = isinstance(arg, AnalysisContext)
        event = arg.event if is_context else arg

        if event.status != "success":
            return arg

        # File type validation
        if not any(event.filename.lower().endswith(ext) for ext in settings.ALLOWED_EXTENSIONS):
            logger.warning("Skipping '%s': Unsupported file extension", event.filename)
            event.status = "error"
            event.error_message = "Unsupported/Invalid File"
            if is_context:
                arg.event = event
                return arg
            return event

        # File size validation
        if len(event.content_bytes) > settings.MAX_FILE_SIZE:
            logger.warning("Skipping '%s': File size (%d bytes) exceeds limit (%d bytes)",
                           event.filename, len(event.content_bytes), settings.MAX_FILE_SIZE)
            event.status = "error"
            event.error_message = "File Too Large (>5MB)"
            if is_context:
                arg.event = event
                return arg
            return event

        # Text extraction
        try:
            event.raw_text = extract_text(event.content_bytes, event.filename)
            event.clean_text = preprocess_text(event.raw_text)
        except Exception as e:
            logger.error("Skipping '%s': Text extraction failed: %s", event.filename, e)
            event.status = "error"
            event.error_message = "Unreadable File"

        if is_context:
            arg.event = event
            return arg
        return event


class SkillExtractionStage(PipelineStage):
    """Stage 2: Extracts technical skills from raw text."""

    async def execute(self, arg: Any) -> Any:
        is_context = isinstance(arg, AnalysisContext)
        event = arg.event if is_context else arg

        output = SkillsExtractedEvent(event)
        if output.status != "success":
            if is_context:
                arg.event = output
                return arg
            return output

        try:
            # Extract skills from job description and candidate resume
            output.jd_skills_objs = extract_skills(event.job_description)
            output.jd_skills_names = [s.canonical_name.lower() for s in output.jd_skills_objs]
            output.candidate_skills_objs = extract_skills(event.raw_text)
        except Exception as e:
            logger.error("Skill extraction stage failed: %s", e)
            output.status = "error"
            output.error_message = "Skill extraction failed"

        if is_context:
            arg.event = output
            return arg
        return output


class SemanticMatchingStage(PipelineStage):
    """Stage 3: Performs semantic skill matching using the Semantic Scoring Engine."""

    async def execute(self, arg: Any) -> Any:
        is_context = isinstance(arg, AnalysisContext)
        event = arg.event if is_context else arg

        output = SemanticMatchedEvent(event)
        if output.status != "success":
            if is_context:
                arg.event = output
                return arg
            return output

        try:
            matcher = SemanticMatcher()
            scorer = SemanticScorer()

            match_results = matcher.match_skills(event.jd_skills_objs, event.candidate_skills_objs)
            semantic_breakdown = scorer.calculate_score(match_results)
            semantic_score = semantic_breakdown["overall"]

            output.match_results = match_results

            # Serialize for backward compatibility
            output.matched_serialized = sorted(list(set([
                res.required_skill.canonical_name.lower()
                for res in match_results
                if res.match_type != "UNKNOWN"
            ])))
            output.missing_serialized = sorted(list(set([
                res.required_skill.canonical_name.lower()
                for res in match_results
                if res.match_type == "UNKNOWN"
            ])))

            # Construct semantic metadata payload
            exact_list = []
            alias_list = []
            hierarchical_list = []
            family_list = []

            for res in match_results:
                item = {
                    "required": res.required_skill.canonical_name,
                    "candidate": res.candidate_skill.canonical_name,
                    "confidence": res.confidence,
                    "weight": res.weight,
                    "reason": res.reason.dict() if hasattr(res.reason, "dict") else res.reason
                }
                if res.match_type == "EXACT":
                    exact_list.append(item)
                elif res.match_type in ("ALIAS", "ABBREVIATION"):
                    alias_list.append(item)
                elif res.match_type == "HIERARCHICAL":
                    hierarchical_list.append(item)
                elif res.match_type == "TECHNOLOGY_FAMILY":
                    family_list.append(item)

            output.semantic_metadata_payload = {
                "exact_matches": exact_list,
                "alias_matches": alias_list,
                "hierarchical_matches": hierarchical_list,
                "family_matches": family_list,
                "semantic_score": semantic_score
            }
        except Exception as e:
            logger.error("Semantic matching stage failed: %s", e)
            output.status = "error"
            output.error_message = "Semantic matching failed"

        if is_context:
            arg.event = output
            return arg
        return output


class ScoringProfileResolutionStage(PipelineStage):
    """Stage 4: Resolves the profile weights configuration from profile_id or default."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self._profile_cache = {}

    async def execute(self, arg: Any) -> Any:
        is_context = isinstance(arg, AnalysisContext)
        event = arg.event if is_context else arg

        output = ProfileResolvedEvent(event)
        if output.status != "success":
            if is_context:
                arg.event = output
                return arg
            return output

        try:
            profile_id = None
            if is_context:
                profile_id = arg.profile_id

            # Check cache first
            cache_key = profile_id if profile_id is not None else "default"
            if cache_key in self._profile_cache:
                cached = self._profile_cache[cache_key]
                output.profile_id = cached["id"]
                output.profile_name = cached["name"]
                output.weights = cached["weights"]
                logger.info(f"Using cached scoring profile '{cached['name']}' with weights: {cached['weights']}")
            else:
                # If DB session is provided, resolve from DB
                resolved = None
                if self.db and profile_id is not None:
                    resolved = self.db.query(ScoringProfile).filter(ScoringProfile.id == profile_id).first()
                elif self.db:
                    # Resolve default profile
                    resolved = self.db.query(ScoringProfile).filter(ScoringProfile.is_default == True).first()

                if resolved:
                    output.profile_id = resolved.id
                    output.profile_name = resolved.name
                    # weights might be stringified JSON or dict
                    w = resolved.weights
                    if isinstance(w, str):
                        import json
                        w = json.loads(w)
                    output.weights = {k: float(v) for k, v in w.items()}

                    # Cache the result
                    self._profile_cache[cache_key] = {
                        "id": output.profile_id,
                        "name": output.profile_name,
                        "weights": output.weights
                    }

                    logger.info(f"Resolved scoring profile '{resolved.name}' with weights: {output.weights}")
                else:
                    # Built-in fallback
                    output.profile_id = None
                    output.profile_name = "General Software Engineer"
                    output.weights = default_scoring_profile_policy.default_weights

                    # Cache the fallback result too, so we don't query the DB again if it failed
                    self._profile_cache[cache_key] = {
                        "id": output.profile_id,
                        "name": output.profile_name,
                        "weights": output.weights
                    }

                    logger.info("Using default general software engineer weights (Fallback)")

        except Exception as e:
            logger.error("Scoring profile resolution failed: %s. Falling back to default.", e)
            output.profile_id = None
            output.profile_name = "General Software Engineer"
            output.weights = default_scoring_profile_policy.default_weights

        if is_context:
            arg.event = output
            return arg
        return output


class ScoringStage(PipelineStage):
    """Stage 4: Scores candidate details (experience, education, projects, document similarity)."""

    async def execute(self, arg: Any) -> Any:
        is_context = isinstance(arg, AnalysisContext)
        event = arg.event if is_context else arg

        output = ScoredEvent(event)
        if output.status != "success":
            if is_context:
                arg.event = output
                return arg
            return output

        try:
            # Resolve event and weights
            if isinstance(event, ProfileResolvedEvent):
                weights = event.weights
                matching_event = event.matching
            else:
                weights = default_scoring_profile_policy.default_weights
                matching_event = event

            raw_text = matching_event.skills.extraction.raw_text
            jd_skills = matching_event.skills.jd_skills_names

            # Extract candidate metadata details
            output.candidate_name = extract_name(raw_text)
            output.candidate_email = extract_email(raw_text)
            output.candidate_phone = extract_phone(raw_text)
            output.candidate_linkedin = extract_linkedin(raw_text)
            output.candidate_github = extract_github(raw_text)
            output.candidate_experience = extract_experience(raw_text)
            output.candidate_internships = extract_relevant_internships(raw_text, jd_skills)
            output.candidate_education = extract_education(raw_text)
            output.candidate_projects = extract_projects(raw_text)

            # Pull scores from matching event
            output.semantic_score = matching_event.semantic_metadata_payload.get("semantic_score", 0.0)
            output.skill_score = output.semantic_score

            # 1. Experience Score (Max years from policy)
            effective_exp_years = output.candidate_experience + (output.candidate_internships * 0.5)
            output.experience_score = min((effective_exp_years / default_scoring_policy.max_experience_years) * 100, 100)

            # 2. Education Score
            education = output.candidate_education
            if education == "PhD":
                output.education_score = 100
            elif education == "Master":
                output.education_score = 80
            elif education == "Bachelor":
                output.education_score = 60
            else:
                output.education_score = 20

            # 3. Projects Score (Target count from policy, capped at 100%)
            output.projects_score = min(100.0, (output.candidate_projects / default_scoring_policy.project_target_count) * 100)

            # 4. Overall Similarity Score (Weights dynamically from resolved profile weights)
            skills_w = weights.get("skills", 0.50)
            experience_w = weights.get("experience", 0.25)
            education_w = weights.get("education", 0.15)
            projects_w = weights.get("projects", 0.10)

            output.similarity_score = (
                output.skill_score * skills_w +
                output.experience_score * experience_w +
                output.education_score * education_w +
                output.projects_score * projects_w
            )
            output.similarity_score = round(output.similarity_score, 2)

            # 5. TF-IDF Cosine Similarity for Document Similarity Component
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.metrics.pairwise import cosine_similarity

                jd_text = " ".join(jd_skills)
                cand_text = " ".join(matching_event.matched_serialized)

                if jd_text.strip() and cand_text.strip():
                    vectorizer = TfidfVectorizer(stop_words='english')
                    tfidf_jd = vectorizer.fit_transform([jd_text])
                    if len(vectorizer.vocabulary_) > 0:
                        tfidf_cand = vectorizer.transform([cand_text])
                        sim = float(cosine_similarity(tfidf_jd, tfidf_cand).flatten()[0]) * 100
                        output.doc_similarity_score = round(sim, 2)
                    else:
                        output.doc_similarity_score = 0.0
                else:
                    output.doc_similarity_score = 0.0
            except Exception as ex:
                logger.error("Failed to compute TF-IDF similarity in stage: %s", ex)
                output.doc_similarity_score = 0.0

        except Exception as e:
            logger.error("Scoring stage failed: %s", e)
            output.status = "error"
            output.error_message = "Scoring failed"

        if is_context:
            arg.event = output
            return arg
        return output


class ExplanationBuildingStage(PipelineStage):
    """Stage 5: Builds structured score explanations (XAI)."""

    async def execute(self, arg: Any) -> Any:
        is_context = isinstance(arg, AnalysisContext)
        event = arg.event if is_context else arg

        output = ExplanationBuiltEvent(event)
        if output.status != "success":
            if is_context:
                arg.event = output
                return arg
            return output

        try:
            from backend.services.xai.builder import build_score_components
            from backend.services.xai.engine import XaiEngine

            # 1. Build score components list with Evidence items
            components = build_score_components(
                scoring_event=event,
                match_results=event.matching.match_results,
                doc_similarity_percentage=event.doc_similarity_score
            )

            # 2. Compile multi-level explanations
            xai_engine = XaiEngine()
            explanations = xai_engine.generate_explanations(components)

            # 3. Overall Summary reasoning
            overall_reason = explanations.get("overall", {}).get("summary", {}).get("why_awarded", "Overall score computed successfully.")

            # 4. Serialize components for Pydantic version-safe storage
            serialized_comps = []
            for comp in components:
                ev_list = []
                for ev in comp.evidence:
                    ev_list.append({
                        "type": ev.type,
                        "category": ev.category,
                        "title": ev.title,
                        "description": ev.description,
                        "importance": ev.importance,
                        "related_skill": ev.related_skill,
                        "confidence": ev.confidence
                    })
                serialized_comps.append({
                    "name": comp.name,
                    "raw_score": comp.raw_score,
                    "weight": comp.weight,
                    "weighted_score": comp.weighted_score,
                    "max_score": comp.max_score,
                    "status": comp.status,
                    "details": comp.details,
                    "evidence": ev_list
                })

            # Construct candidate result map for standard metadata builder
            cand_dict = {
                "name": event.candidate_name,
                "email": event.candidate_email,
                "phone": event.candidate_phone,
                "linkedin": event.candidate_linkedin,
                "github": event.candidate_github,
                "experience": event.candidate_experience,
                "education": event.candidate_education,
                "projects": event.candidate_projects,
                "similarity_score": event.similarity_score,
                "skill_score": event.skill_score,
                "experience_score": event.experience_score,
                "education_score": event.education_score,
                "projects_score": event.projects_score,
                "matched_skills": event.matching.matched_serialized,
                "missing_skills": event.matching.missing_serialized,
                "extracted_skills": [s.canonical_name for s in event.matching.skills.candidate_skills_objs]
            }

            # Generate base analysis_metadata schema
            output.analysis_metadata = build_analysis_metadata(
                candidate_result=cand_dict,
                processing_time_ms=0,
                parser=event.matching.skills.extraction.file_ext,
                document_type=event.matching.skills.extraction.file_ext,
                semantic_data=event.matching.semantic_metadata_payload
            )

            # Enrich with complete structured XAI block
            output.analysis_metadata["xai"] = {
                "enabled": True,
                "components": serialized_comps,
                "overall_summary": overall_reason,
                "explanations": explanations
            }

            # Enrich with Adaptive Scoring Profile details (Part 6)
            profile_resolved = getattr(event, "profile_resolved", None)
            if profile_resolved:
                output.analysis_metadata["profile_id"] = profile_resolved.profile_id
                output.analysis_metadata["profile_name"] = profile_resolved.profile_name
                output.analysis_metadata["profile_version"] = profile_resolved.profile_version
                output.analysis_metadata["component_weights"] = profile_resolved.weights
            else:
                output.analysis_metadata["profile_id"] = None
                output.analysis_metadata["profile_name"] = "General Software Engineer"
                output.analysis_metadata["profile_version"] = "1.0.0"
                output.analysis_metadata["component_weights"] = default_scoring_profile_policy.default_weights

            output.analysis_metadata["engine_version"] = "v1.0.0"

            # Store structured score breakdown
            output.analysis_metadata["score_breakdown"] = {
                "skill_score": event.skill_score,
                "experience_score": event.experience_score,
                "education_score": event.education_score,
                "projects_score": event.projects_score,
                "doc_similarity_score": event.doc_similarity_score
            }

            # Set flat fields for legacy compatibility / logs
            output.xai_explanations = {
                "skills_summary": explanations.get("skills", {}).get("summary", {}).get("why_awarded", ""),
                "experience_summary": explanations.get("experience", {}).get("summary", {}).get("why_awarded", ""),
                "education_summary": explanations.get("education", {}).get("summary", {}).get("why_awarded", ""),
                "projects_summary": explanations.get("projects", {}).get("summary", {}).get("why_awarded", ""),
                "overall_reasoning": overall_reason
            }

        except Exception as e:
            logger.error("Explanation building stage failed: %s", e)
            output.status = "error"
            output.error_message = "Explanation building failed"

        if is_context:
            arg.event = output
            return arg
        return output


class RecommendationBuildingStage(PipelineStage):
    """Stage 6: Generates deterministic recommendations for resume improvements."""

    async def execute(self, arg: Any) -> Any:
        is_context = isinstance(arg, AnalysisContext)
        event = arg.event if is_context else arg

        output = RecommendationBuiltEvent(event)
        if output.status != "success":
            if is_context:
                arg.event = output
                return arg
            return output

        try:
            from backend.services.recommendations.builder import build_resume_recommendations

            # Build list of Pydantic Recommendation models
            recs = await build_resume_recommendations(event.scoring)

            # Serialize for JSON database storage with lifecycle and history tracking
            serialized_recs = []
            now_iso = datetime.datetime.utcnow().isoformat() + "Z"
            for r in recs:
                serialized_recs.append({
                    "id": r.id,
                    "title": r.title,
                    "description": r.description,
                    "priority": r.priority,
                    "category": r.category,
                    "reason": r.reason,
                    "source": r.source,
                    "related_skills": r.related_skills,
                    "estimated_score_gain": r.estimated_score_gain,
                    "confidence": r.confidence,
                    "status": "ACTIVE",
                    "generated_at": now_iso,
                    "resolved_at": None,
                    "accepted_by_user": False
                })

            output.recommendations = serialized_recs

            # Inject recommendations block into analysis_metadata
            event.analysis_metadata["recommendations"] = {
                "list": serialized_recs,
                "generated_at": now_iso,
                "engine_version": "1.0.0"
            }
        except Exception as e:
            logger.error("Recommendation building stage failed: %s", e)
            output.status = "error"
            output.error_message = "Recommendation building failed"

        if is_context:
            arg.event = output
            return arg
        return output


class PersistenceStage(PipelineStage):
    """Stage 6: Persists Resume and ScanResult to the database transactionally."""

    def __init__(self, db: Session):
        self.db = db


    def execute_batch(self, args_list: list, **common_kwargs) -> list:
        """Batch executes persistence for multiple items, optimizing N+1 database queries."""
        if not args_list:
            return []

        outputs = []
        valid_items = []

        # Prepare Resumes
        for item in args_list:
            arg = item.get("arg")
            kwargs = item.get("kwargs", {})
            # Merge common kwargs with specific kwargs
            merged_kwargs = {**common_kwargs, **kwargs}

            is_context = isinstance(arg, AnalysisContext)
            event = arg.event if is_context else arg

            output = PersistenceEvent(event)
            outputs.append(output)

            if output.status != "success":
                if is_context:
                    arg.event = output
                continue

            try:
                candidate_id = merged_kwargs.get("candidate_id")
                version = merged_kwargs.get("version", 1)
                label = merged_kwargs.get("label")
                label_source = merged_kwargs.get("label_source", "SYSTEM")
                job_description_id = merged_kwargs.get("job_description_id")
                ats_score = merged_kwargs.get("ats_score", 0.0)
                elapsed_ms = merged_kwargs.get("elapsed_ms", 0)

                scoring = event.explanation.scoring
                extraction = scoring.matching.skills.extraction

                meta = event.explanation.analysis_metadata
                meta["score"]["overall"] = ats_score
                meta["engine"]["processing_time_ms"] = elapsed_ms

                if is_context:
                    meta["pipeline_metrics"] = arg.metrics

                resume = Resume(
                    candidate_id=candidate_id,
                    extracted_text=extraction.raw_text,
                    original_filename=extraction.filename,
                    file_type=extraction.file_ext,
                    version=version,
                    label=label,
                    label_source=label_source,
                    status=ResumeStatus.ACTIVE
                )
                valid_items.append({
                    "resume": resume,
                    "meta": meta,
                    "job_description_id": job_description_id,
                    "ats_score": ats_score,
                    "output": output
                })
            except Exception as e:
                logger.error("Error preparing persistence for item: %s", e)
                output.status = "error"
                output.error_message = f"Data preparation failed: {str(e)}"
                if is_context:
                    arg.event = output

        if not valid_items:
            return outputs

        try:
            # Batch insert Resumes
            resumes_to_add = [item["resume"] for item in valid_items]
            self.db.add_all(resumes_to_add)
            self.db.flush()

            # Batch insert ScanResults
            scan_results_to_add = []
            for item in valid_items:
                resume = item["resume"]
                scan_result = ScanResult(
                    resume_id=resume.id,
                    job_description_id=item["job_description_id"],
                    ats_score=item["ats_score"],
                    analysis_metadata=item["meta"]
                )
                scan_results_to_add.append(scan_result)
                item["scan_result"] = scan_result

            self.db.add_all(scan_results_to_add)
            self.db.flush()

            # Finalize outputs
            for item in valid_items:
                resume = item["resume"]
                scan_result = item["scan_result"]
                output = item["output"]

                output.resume_id = resume.id
                output.scan_result_id = scan_result.id
                output.recommendation.explanation.scoring.similarity_score = item["ats_score"]

            logger.info("Pipeline batch persisted %d Resumes and ScanResults successfully", len(valid_items))
        except Exception as e:
            self.db.rollback()
            logger.error("Batch persistence failed: %s", e)
            for item in valid_items:
                output = item["output"]
                output.status = "error"
                output.error_message = f"Database batch persistence failed: {str(e)}"

        # Make sure the context events are updated as well for the ones that were successfully run
        for i, item in enumerate(args_list):
            arg = item.get("arg")
            is_context = isinstance(arg, AnalysisContext)
            if is_context:
                # the outputs array corresponds 1:1 with args_list
                arg.event = outputs[i]
                outputs[i] = arg

        return outputs

    def execute(self, arg: Any, **kwargs) -> PersistenceEvent:
        is_context = isinstance(arg, AnalysisContext)
        event = arg.event if is_context else arg

        output = PersistenceEvent(event)
        if output.status != "success":
            if is_context:
                arg.event = output
                return arg
            return output

        try:
            # Extract arguments
            candidate_id = kwargs.get("candidate_id")
            version = kwargs.get("version", 1)
            label = kwargs.get("label")
            label_source = kwargs.get("label_source", "SYSTEM")
            job_description_id = kwargs.get("job_description_id")
            ats_score = kwargs.get("ats_score", 0.0)
            elapsed_ms = kwargs.get("elapsed_ms", 0)

            scoring = event.explanation.scoring
            extraction = scoring.matching.skills.extraction

            # Build final analysis_metadata with correct overall ats_score and elapsed time
            meta = event.explanation.analysis_metadata
            meta["score"]["overall"] = ats_score
            meta["engine"]["processing_time_ms"] = elapsed_ms

            # Save pipeline execution metrics from context (Part 10 / metrics)
            if is_context:
                meta["pipeline_metrics"] = arg.metrics

            # Save Resume model
            resume = Resume(
                candidate_id=candidate_id,
                extracted_text=extraction.raw_text,
                original_filename=extraction.filename,
                file_type=extraction.file_ext,
                version=version,
                label=label,
                label_source=label_source,
                status=ResumeStatus.ACTIVE
            )
            self.db.add(resume)
            self.db.flush()  # get resume.id

            # Save ScanResult model
            scan_result = ScanResult(
                resume_id=resume.id,
                job_description_id=job_description_id,
                ats_score=ats_score,
                analysis_metadata=meta
            )
            self.db.add(scan_result)
            self.db.flush()

            output.resume_id = resume.id
            output.scan_result_id = scan_result.id

            # Sync back to output.recommendation.explanation.scoring.similarity_score = ats_score
            output.recommendation.explanation.scoring.similarity_score = ats_score

            logger.info("Pipeline persisted Resume ID %d and ScanResult ID %d successfully", resume.id, scan_result.id)
        except Exception as e:
            self.db.rollback()
            logger.error("Persistence stage failed: %s", e)
            output.status = "error"
            output.error_message = f"Database persistence failed: {str(e)}"

        return output
