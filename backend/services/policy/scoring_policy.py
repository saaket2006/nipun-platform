class ScoringPolicy:
    """
    Defines policy configurations for ATS scoring and weights.
    Removes magic numbers from scoring systems and stages.
    """
    def __init__(
        self,
        skills_weight: float = 0.50,
        experience_weight: float = 0.25,
        education_weight: float = 0.15,
        projects_weight: float = 0.10,
        max_experience_years: float = 10.0,
        project_target_count: int = 3
    ):
        self.skills_weight = skills_weight
        self.experience_weight = experience_weight
        self.education_weight = education_weight
        self.projects_weight = projects_weight
        self.max_experience_years = max_experience_years
        self.project_target_count = project_target_count

# Default global scoring policy instance
default_scoring_policy = ScoringPolicy()
