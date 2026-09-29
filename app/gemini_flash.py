import json
from google.genai import types
from app.config import ask, TEXT_MODELS


def generate_outline(prompt, character, setting, tone, art_style):
    """Returns a list of 5 dicts: panel, title, scene, image_prompt."""
    instruction = f"""
Create a 5-panel comic outline.
Story idea: {prompt}
Main character: {character}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY a JSON list of exactly 5 objects. Each object must have the keys:
"panel" (number), "title", "scene" (1-2 sentences), "image_prompt" (a visual description for an image generator,
mention the character, setting and the {art_style} art style).
"""
    response = ask(
        TEXT_MODELS,
        instruction,
        types.GenerateContentConfig(response_mime_type="application/json"),
    )
    text = response.text.replace("```json", "").replace("```", "").strip()
    data = json.loads(text)
    if isinstance(data, dict):
        data = next(iter(data.values()))
    return data[:5]