import re
from pathlib import Path


def build_comic_layout(outline, story_text, image_paths):
    """Matches each image with its panel story. Returns a list of dicts."""
    story_text = story_text.replace("*", "")
    parts = re.split(r"Panel\s*(\d+)\s*[:.\-]?", story_text, flags=re.IGNORECASE)
    stories = {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}

    layout = []
    for n, (panel, path) in enumerate(zip(outline, image_paths), start=1):
        layout.append({
            "panel": n,
            "title": panel.get("title", f"Panel {n}"),
            "image_path": path,
            "image_url": f"/static/panels/{Path(path).name}",
            "text": stories.get(n, panel.get("scene", "")),
        })
    return layout