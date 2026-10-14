from typing import List, Dict, Any, Optional

class PipelineEvent:
    """Base class for all pipeline stages' input/output data contracts."""
    pass

class ResumeExtractedEvent(PipelineEvent):
    def __init__(self, filename: str, content_bytes: bytes, job_description: str, clean_jd: str):
        self.filename = filename
        self.content_bytes = content_bytes
        self.job_description = job_description
        self.clean_jd = clean_jd

        self.raw_text = ""
        self.clean_text = ""
        self.file_ext = filename.split(".")[-1].lower() if "." in filename else "unknown"

        self.status = "success"  # "success" or "error"
        self.error_message = ""

class SkillsExtractedEvent(PipelineEvent):
    def __init__(self, extraction: ResumeExtractedEvent):
        self.extraction = extraction
        self.jd_skills_objs: List[Any] = []
        self.jd_skills_names: List[str] = []
        self.candidate_skills_objs: List[Any] = []

        # Copy status from previous event
        self.status = extraction.status
        self.error_message = extraction.error_message

class SemanticMatchedEvent(PipelineEvent):
    def __init__(self, skills: SkillsExtractedEvent):
        self.skills = skills
        self.match_results: List[Any] = []
        self.matched_serialized: List[str] = []
        self.missing_serialized: List[str] = []
        self.semantic_metadata_payload: Dict[str, Any] = {}

        self.status = skills.status
        self.error_message = skills.error_message

class ProfileResolvedEvent(PipelineEvent):
    def __init__(self, matching: SemanticMatchedEvent):
        self.matching = matching
        self.profile_id: Optional[int] = None
        self.profile_name: str = "General Software Engineer"
        self.profile_version: str = "1.0.0"
        self.weights: Dict[str, float] = {"skills": 0.50, "experience": 0.25, "education": 0.15, "projects": 0.10}
        self.is_custom: bool = False
        self.max_experience_years: float = 10.0
        self.project_target_count: int = 3
        self.custom_config: Optional[Dict[str, Any]] = None
        self.status = matching.status
        self.error_message = matching.error_message

class ScoredEvent(PipelineEvent):
    def __init__(self, source: Any):
        if isinstance(source, ProfileResolvedEvent):
            self.profile_resolved = source
            self.matching = source.matching
        else:
            self.profile_resolved = None
            self.matching = source
        self.semantic_score = 0.0

        # Candidate Info
        self.candidate_name = "N/A"
        self.candidate_email = "N/A"
        self.candidate_phone = "N/A"
        self.candidate_linkedin = "Not Provided"
        self.candidate_github = "Not Provided"
        self.candidate_experience = 0
        self.candidate_internships = 0
        self.candidate_education = "None"
        self.candidate_projects = 0

        # Individual scores (calculated or placeholder)
        self.similarity_score = 0.0
        self.skill_score = 0.0
        self.experience_score = 0.0
        self.education_score = 0.0
        self.projects_score = 0.0
        self.doc_similarity_score = 0.0

        self.status = self.matching.status
        self.error_message = self.matching.error_message

class ExplanationBuiltEvent(PipelineEvent):
    def __init__(self, scoring: ScoredEvent):
        self.scoring = scoring
        self.analysis_metadata: Dict[str, Any] = {}
        self.xai_explanations: Dict[str, str] = {}

        self.status = scoring.status
        self.error_message = scoring.error_message

class RecommendationBuiltEvent(PipelineEvent):
    def __init__(self, explanation: ExplanationBuiltEvent):
        self.explanation = explanation
        self.recommendations: List[Dict[str, Any]] = []
        self.status = explanation.status
        self.error_message = explanation.error_message

class PersistenceEvent(PipelineEvent):
    def __init__(self, recommendation: RecommendationBuiltEvent):
        self.recommendation = recommendation
        self.resume_id: Optional[int] = None
        self.scan_result_id: Optional[int] = None

        self.status = recommendation.status
