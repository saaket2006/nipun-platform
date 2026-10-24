from backend.services.skills.models import Skill, NormalizedSkill
from backend.services.skills.loader import get_skills_loader

class SkillNormalizer:
    """
    Normalizes arbitrary skill strings extracted from resumes or job descriptions
    using structured matching against the cached Skill Knowledge Base.
    Supports Exact, Alias, Abbreviation, and validation-safe Unknown match types.
    """
    def __init__(self):
        # This will fetch the singleton cached skills list
        self.skills = get_skills_loader()

        # Pre-compute lookup dictionaries for O(1) matching
        self._exact_map = {}
        self._alias_map = {}
        self._abbr_map = {}

        for s in self.skills:
            id_parts = s.id.split(".")
            simple_id = id_parts[-1] if len(id_parts) > 1 else s.id

            # Exact matches
            for key in (s.canonical_name.lower(), s.id.lower(), simple_id.lower()):
                if key not in self._exact_map:
                    self._exact_map[key] = s

            # Alias matches
            for alias in s.aliases:
                key = alias.lower()
                if key not in self._alias_map:
                    self._alias_map[key] = s

            # Abbreviation matches
            for abbr in s.abbreviations:
                key = abbr.lower()
                if key not in self._abbr_map:
                    self._abbr_map[key] = s

    def normalize(self, skill_name: str) -> NormalizedSkill:
        if not skill_name:
            return self._build_unknown("")

        cleaned = skill_name.strip()
        cleaned_lower = cleaned.lower()

        # 1. Exact Match Check
        if cleaned_lower in self._exact_map:
            return NormalizedSkill(skill=self._exact_map[cleaned_lower], match_type="exact", confidence=1.0)

        # 2. Alias Match Check
        if cleaned_lower in self._alias_map:
            return NormalizedSkill(skill=self._alias_map[cleaned_lower], match_type="alias", confidence=0.9)

        # 3. Abbreviation Match Check
        if cleaned_lower in self._abbr_map:
            return NormalizedSkill(skill=self._abbr_map[cleaned_lower], match_type="abbreviation", confidence=0.8)

        # 4. Unknown/Temporary Skill fallback
        return self._build_unknown(cleaned)

    def _build_unknown(self, raw_name: str) -> NormalizedSkill:
        cleaned_id = raw_name.lower().replace(" ", "_") if raw_name else "unknown"
        temp_skill = Skill(
            id=cleaned_id,
            canonical_name=raw_name or "Unknown",
            aliases=[],
            abbreviations=[],
            category="Unknown",
            subcategory="Unknown",
            technology_family="Unknown"
        )
        return NormalizedSkill(skill=temp_skill, match_type="unknown", confidence=0.0)
