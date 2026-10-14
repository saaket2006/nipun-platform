from typing import Optional, Dict, Any

class ScoringProfilePolicy:
    """
    Defines policy configurations and fallback weights for adaptive scoring profiles.
    Helps avoid magic numbers when handling weights validation and defaults.
    """
    def __init__(
        self,
        default_weights: dict = None,
        min_weight_sum: float = 0.99,
        max_weight_sum: float = 1.01
    ):
        self.default_weights = default_weights or {
            "skills": 0.50,
            "experience": 0.25,
            "education": 0.15,
            "projects": 0.10
        }
        self.min_weight_sum = min_weight_sum
        self.max_weight_sum = max_weight_sum

# Default global scoring profile policy instance
default_scoring_profile_policy = ScoringProfilePolicy()


def validate_and_normalize_scoring_config(
    raw_config: Any,
    base_weights: Optional[Dict[str, float]] = None
) -> Optional[Dict[str, Any]]:
    """
    Validates, sanitizes, and normalizes optional recruiter custom scoring configuration.
    Returns None if custom scoring is disabled or not provided.
    Raises ValueError with descriptive messages for invalid inputs.
    """
    if raw_config is None:
        return None

    # Handle string (from multipart form data or JSON payload)
    if isinstance(raw_config, str):
        raw_str = raw_config.strip()
        if not raw_str or raw_str in ("null", "undefined", "None"):
            return None
        try:
            import json
            config = json.loads(raw_str)
        except Exception:
            raise ValueError("Invalid JSON format for custom scoring configuration")
    elif isinstance(raw_config, dict):
        config = raw_config
    else:
        # e.g. Form instance or other unexpected type
        return None

    if not isinstance(config, dict):
        raise ValueError("Custom scoring configuration must be a JSON object")

    # If customization is explicitly not enabled, return None
    if not config.get("enabled", False):
        return None

    raw_weights = config.get("weights")
    if not raw_weights or not isinstance(raw_weights, dict):
        raise ValueError("Custom scoring configuration must include a 'weights' object")

    disabled_criteria = set(config.get("disabled_criteria") or [])

    supported_keys = ("skills", "experience", "education", "projects")
    clean_weights = {}

    for key in supported_keys:
        if key in disabled_criteria:
            clean_weights[key] = 0.0
            continue

        raw_val = raw_weights.get(key)
        if raw_val is None:
            # Fall back to base_weights or default policy if omitted
            if base_weights and key in base_weights:
                raw_val = base_weights[key]
            else:
                raw_val = default_scoring_profile_policy.default_weights.get(key, 0.0)

        try:
            val = float(raw_val)
        except (TypeError, ValueError):
            raise ValueError(f"Weight for '{key}' must be a valid number")

        if val < 0.0:
            raise ValueError(f"Weight for '{key}' cannot be negative")

        clean_weights[key] = val

    # Convert percentage values (> 1.5) to decimal if necessary
    total_val = sum(clean_weights.values())
    if total_val > 1.5:
        clean_weights = {k: v / 100.0 for k, v in clean_weights.items()}
        total_val = sum(clean_weights.values())

    if total_val <= 0.0:
        raise ValueError("At least one scoring criterion must be enabled with a positive weight")

    # Proportionally normalize active weights so sum == 1.0000 exactly
    clean_weights = {k: round(v / total_val, 4) for k, v in clean_weights.items()}
    # Fix any minor rounding discrepancy onto the highest active weight
    rounding_delta = round(1.0 - sum(clean_weights.values()), 4)
    if rounding_delta != 0.0:
        active_keys = [k for k in supported_keys if clean_weights[k] > 0.0]
        if active_keys:
            max_key = max(active_keys, key=lambda k: clean_weights[k])
            clean_weights[max_key] = round(clean_weights[max_key] + rounding_delta, 4)

    # Validate thresholds
    raw_thresholds = config.get("thresholds") or {}
    if not isinstance(raw_thresholds, dict):
        raise ValueError("'thresholds' must be an object")

    # Target experience years (for 100% score)
    target_exp = raw_thresholds.get("target_experience_years")
    if target_exp is None:
        target_exp = raw_thresholds.get("max_experience_years", 10.0)
    try:
        target_exp = float(target_exp)
    except (TypeError, ValueError):
        raise ValueError("Target experience years must be a number")
    if target_exp < 1.0 or target_exp > 30.0:
        raise ValueError("Target experience years must be between 1 and 30")

    # Target project count (for 100% score)
    target_proj = raw_thresholds.get("target_project_count")
    if target_proj is None:
        target_proj = raw_thresholds.get("project_target_count", 3)
    try:
        target_proj = int(target_proj)
    except (TypeError, ValueError):
        raise ValueError("Target project count must be an integer")
    if target_proj < 1 or target_proj > 10:
        raise ValueError("Target project count must be between 1 and 10")

    return {
        "enabled": True,
        "weights": clean_weights,
        "thresholds": {
            "target_experience_years": target_exp,
            "target_project_count": target_proj,
            "max_experience_years": target_exp,
            "project_target_count": target_proj
        }
    }

