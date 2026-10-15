import os
import json
import logging
import httpx
from typing import List
from backend.services.recommendations.models import Recommendation

logger = logging.getLogger("resume_screener")

async def enhance_recommendations_with_llm(recommendations: List[Recommendation]) -> List[Recommendation]:
    """
    Enhances the wording and formatting of recommendations using an LLM (Gemini or OpenAI)
    if API keys are configured.
    Otherwise, returns the recommendations list as-is (graceful fallback).
    """
    if not recommendations:
        return recommendations
        
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not gemini_key and not openai_key:
        logger.info("No LLM API keys configured. Skipping LLM enhancement stage.")
        return recommendations
        
    # Prepare recommendations payload for the prompt
    payload = []
    for r in recommendations:
        payload.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "category": r.category
        })
        
    prompt = (
        "You are an expert resume writer. Enhance the titles and descriptions of these resume recommendations to "
        "make them more professional, compelling, and actionable for the candidate. "
        "You must preserve the 'id' and 'category' keys exactly. "
        "Return the response ONLY as a valid JSON array of objects containing 'id', 'title', and 'description'. "
        "Do not include markdown wrappers like ```json. "
        f"Input data: {json.dumps(payload)}"
    )
    
    try:
        enhanced_data = None
        if gemini_key:
            enhanced_data = await _call_gemini_api(prompt, gemini_key)
        elif openai_key:
            enhanced_data = await _call_openai_api(prompt, openai_key)
            
        if enhanced_data:
            # Map enhanced text back to recommendations
            enhanced_map = {item["id"]: item for item in enhanced_data if "id" in item}
            for r in recommendations:
                if r.id in enhanced_map:
                    r.title = enhanced_map[r.id].get("title", r.title)
                    r.description = enhanced_map[r.id].get("description", r.description)
                    r.source = "LLM" # Update source tag indicating LLM enhancement
                    
            logger.info("Successfully enhanced %d recommendation(s) using LLM.", len(recommendations))
    except Exception as e:
        logger.warning("LLM enhancement failed: %s. Falling back to rule-based heuristics.", e)
        
    return recommendations

async def _call_gemini_api(prompt: str, api_key: str) -> List[dict]:
    # Priority ordered list of Gemini models to attempt
    from backend.services.xai.gemini_explainer import ORDERED_GEMINI_MODELS

    headers = {"Content-Type": "application/json"}
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

    async with httpx.AsyncClient() as client:
        for model_name in ORDERED_GEMINI_MODELS:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                response = await client.post(url, json=payload, headers=headers, timeout=12.0)
                if response.status_code != 200:
                    logger.warning("Gemini model '%s' returned status %d. Trying fallback...", model_name, response.status_code)
                    continue

                res_body = response.json()
                candidates = res_body.get("candidates", [])
                if not candidates:
                    continue

                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                if not text:
                    continue

                if text.startswith("```json"):
                    text = text[7:]
                elif text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return parsed
                elif isinstance(parsed, dict) and "recommendations" in parsed:
                    return parsed["recommendations"]
            except Exception as e:
                logger.warning("Error with Gemini model '%s': %s", model_name, e)

    return []

async def _call_openai_api(prompt: str, api_key: str) -> List[dict]:
    url = "https://api.openai.com/v1/chat/completions"
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers, timeout=10.0)
        res_body = response.json()
        choices = res_body.get("choices", [])
        if choices:
            text = choices[0]["message"]["content"].strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
    return []
