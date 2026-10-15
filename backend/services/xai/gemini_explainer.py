import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional

logger = logging.getLogger("resume_screener")

# Priority ordered list of Gemini models to attempt
GEMINI_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
    "gemini-2.5-flash",
]
# Deduplicate while preserving order
SEEN_MODELS = set()
ORDERED_GEMINI_MODELS = [m for m in GEMINI_MODELS if not (m in SEEN_MODELS or SEEN_MODELS.add(m))]


async def generate_grounded_xai_insights(
    candidate_dict: Dict[str, Any],
    job_description: str,
    resume_text: str,
    score_components: List[Any],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Invokes the Google Gemini API to generate grounded, explainable AI insights for a candidate's resume
    evaluated against a target job description.

    Returns a structured dictionary containing:
      - source: "GEMINI" (or "RULE" on fallback)
      - status: "SUCCESS" (or "FALLBACK")
      - status_message: None or reason for fallback
      - model: model used if successful
      - overall_summary: synthesized alignment explanation
      - strengths: list of key strengths
      - skill_gaps: list of missing skills / qualification gaps
      - component_explanations: enriched component explanations
    """
    key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY")

    if not key:
        logger.info("No GEMINI_API_KEY configured. Falling back to deterministic rule-based XAI.")
        return _build_deterministic_fallback(
            candidate_dict=candidate_dict,
            reason="Gemini API key is not configured"
        )

    # Sanitize and truncate inputs to preserve budget and prevent excessive token usage
    jd_excerpt = (job_description or "")[:2500].strip()
    resume_excerpt = (resume_text or "")[:3000].strip()

    name = candidate_dict.get("name", "Candidate")
    experience = candidate_dict.get("experience", 0)
    education = candidate_dict.get("education", "None")
    similarity_score = candidate_dict.get("similarity_score", 0.0)
    matched_skills = candidate_dict.get("matched_skills", [])
    missing_skills = candidate_dict.get("missing_skills", [])

    prompt = f"""You are an expert Explainable AI (XAI) career and hiring evaluator for the Nipun ATS platform.
Your task is to analyze the candidate's alignment with the Job Description and provide a truthful, grounded explanation.

Evaluation Context:
- Candidate Name: {name}
- Overall Match Score: {similarity_score:.1f}%
- Professional Experience: {experience} years
- Education: {education}
- Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}
- Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}

Target Job Description:
\"\"\"{jd_excerpt}\"\"\"

Resume Excerpt:
\"\"\"{resume_excerpt}\"\"\"

Rules:
1. Explain WHY the candidate received this match score based strictly on evidence in their resume and JD requirements.
2. Highlight genuine strengths from their resume that align with the JD.
3. Highlight critical skill gaps or missing qualifications that lowered their score.
4. Ground all statements in the actual submitted resume and JD (do NOT hallucinate technologies or experience not present).
5. Return the response ONLY as a valid JSON object matching the exact schema below, with no markdown code fences or backticks.

Expected JSON schema:
{{
  "overall_summary": "2-3 concise, professional sentences summarizing candidate fit, strengths, and primary gap.",
  "strengths": [
    "Specific strength grounded in resume matching a JD requirement",
    "Another specific strength with evidence"
  ],
  "skill_gaps": [
    "Specific missing skill or experience gap required by the JD",
    "Another gap or improvement area"
  ],
  "skills_explanation": {{
    "why_awarded": "Explanation of matched technical skills grounded in resume",
    "why_deducted": "Explanation of missing technical skills requested by JD"
  }},
  "experience_explanation": {{
    "why_awarded": "Explanation of professional tenure and relevancy",
    "why_deducted": "Seniority or tenure gaps relative to JD expectations"
  }}
}}"""

    # Attempt models in order of priority (handling quotas, timeouts, model availability)
    last_error = None
    for model_name in ORDERED_GEMINI_MODELS:
        try:
            parsed = await _call_gemini_content(prompt, key, model_name)
            if parsed and isinstance(parsed, dict) and "overall_summary" in parsed:
                logger.info("Successfully generated grounded XAI insights with model '%s'", model_name)
                return {
                    "source": "GEMINI",
                    "status": "SUCCESS",
                    "model": model_name,
                    "status_message": None,
                    "overall_summary": parsed.get("overall_summary", "").strip(),
                    "strengths": [str(s).strip() for s in parsed.get("strengths", []) if str(s).strip()],
                    "skill_gaps": [str(g).strip() for g in parsed.get("skill_gaps", []) if str(g).strip()],
                    "component_explanations": {
                        "skills": parsed.get("skills_explanation", {}),
                        "experience": parsed.get("experience_explanation", {})
                    }
                }
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code == 429:
                last_error = f"Quota limit reached (HTTP 429) on model {model_name}"
                logger.warning("Gemini model '%s' quota exceeded (HTTP 429). Attempting fallback model...", model_name)
            elif status_code == 404:
                last_error = f"Model {model_name} not available (HTTP 404)"
                logger.warning("Gemini model '%s' not found (HTTP 404). Attempting fallback model...", model_name)
            elif status_code == 503:
                last_error = f"Model {model_name} temporarily overloaded (HTTP 503)"
                logger.warning("Gemini model '%s' unavailable (HTTP 503). Attempting fallback model...", model_name)
            else:
                last_error = f"Gemini API returned status {status_code}"
                logger.warning("Gemini API error on model '%s': status %d", model_name, status_code)
        except Exception as e:
            last_error = str(e)
            logger.warning("Gemini request failed for model '%s': %s", model_name, e)

    # All Gemini models failed or exhausted quota -> graceful deterministic fallback
    logger.warning("All Gemini model attempts exhausted. Reason: %s. Using deterministic fallback.", last_error)
    return _build_deterministic_fallback(
        candidate_dict=candidate_dict,
        reason=f"AI-generated insights are temporarily unavailable ({last_error or 'quota/connection limit'}). Showing rule-based analysis."
    )


async def _call_gemini_content(prompt: str, api_key: str, model_name: str) -> Optional[Dict[str, Any]]:
    """Makes HTTP request to Gemini API and parses JSON response."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024
        }
    }
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=12.0)
        response.raise_for_status()
        res_json = response.json()

        candidates = res_json.get("candidates", [])
        if not candidates:
            return None

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return None

        raw_text = parts[0].get("text", "").strip()
        return _safe_parse_json(raw_text)


def _safe_parse_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """Safely extracts and parses JSON even if wrapped in markdown code fences or surrounded by text."""
    if not raw_text:
        return None

    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Attempt to locate first { and last }
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start:end+1])
            except Exception:
                pass
        logger.warning("Failed to decode JSON from Gemini response: %s", raw_text[:200])
        return None


def _build_deterministic_fallback(candidate_dict: Dict[str, Any], reason: str) -> Dict[str, Any]:
    """
    Constructs a deterministic, grounded rule-based summary when Gemini is unavailable.
    Never fabricates or falsely claims that AI analysis succeeded.
    """
    name = candidate_dict.get("name", "Candidate")
    score = candidate_dict.get("similarity_score", 0.0)
    matched = candidate_dict.get("matched_skills", [])
    missing = candidate_dict.get("missing_skills", [])
    exp = candidate_dict.get("experience", 0)

    # Grounded strengths based on verified keyword and experience matches
    strengths = []
    if matched:
        strengths.append(f"Demonstrated proficiency in {len(matched)} matching required skills: {', '.join(matched[:4])}")
    if exp > 0:
        strengths.append(f"Possesses {exp} year(s) of relevant professional work experience")
    if candidate_dict.get("projects", 0) > 0:
        strengths.append(f"Completed {candidate_dict.get('projects')} verified technical project(s)")

    # Grounded gaps based on missing skills
    gaps = []
    if missing:
        gaps.append(f"Missing {len(missing)} required skill(s) from job description: {', '.join(missing[:4])}")
    if exp < 3:
        gaps.append(f"Seniority level ({exp} yrs) is below standard mid/senior tenure expectations")

    if not strengths:
        strengths = ["Resume text successfully processed and indexed for keyword matching"]
    if not gaps:
        gaps = ["No major missing skill gaps identified against extracted requirements"]

    summary = (
        f"{name} achieves a {score:.1f}% ATS match score based on deterministic criteria. "
        f"The candidate successfully matched {len(matched)} technical skill(s) with {exp} year(s) of experience, "
        f"with {len(missing)} requirement(s) remaining unsatisfied."
    )

    return {
        "source": "RULE",
        "status": "FALLBACK",
        "status_message": reason,
        "model": None,
        "overall_summary": summary,
        "strengths": strengths,
        "skill_gaps": gaps,
        "component_explanations": {}
    }
