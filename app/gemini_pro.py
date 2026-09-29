from app.config import ask, PRO_MODELS


def generate_story(outline, character, tone):
    """Returns one text block: 'Panel 1: ...', 'Panel 2: ...' etc."""
    scenes = "\n".join(f"Panel {p['panel']} - {p['title']}: {p['scene']}" for p in outline)
    instruction = f"""
Write a comic story from this outline. Main character: {character}. Tone: {tone}.

{scenes}

For each panel write short narration and 1-3 lines of dialogue.
Format EXACTLY like this, plain text only, no markdown or asterisks:
Panel 1:
Narration: ...
{character}: "..."

Panel 2:
...
"""
    return ask(PRO_MODELS, instruction).text