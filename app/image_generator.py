import io
import re
import textwrap
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from google.genai import types

from app.config import client, IMAGE_MODELS

PANELS_DIR = Path(__file__).parent / "static" / "panels"
COLORS = [(255, 214, 165), (202, 255, 191), (155, 246, 255), (189, 178, 255), (255, 198, 255)]

_gemini_enabled = True  # switched off after the first failure so we don't waste time


def _gemini_image(prompt):
    global _gemini_enabled
    if not _gemini_enabled:
        return None
    for name in IMAGE_MODELS:
        try:
            response = client.models.generate_content(
                model=name,
                contents=prompt,
                config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    return Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
        except Exception as e:
            print(f"[Gemini image model {name} failed] {str(e)[:150]}")
    _gemini_enabled = False
    print("[Gemini images unavailable on this key, using free fallback]")
    return None


def _free_image(prompt):
    """Free image service, no key needed. Anonymous use is rate-limited, so it retries."""
    text = urllib.parse.quote(prompt[:350])
    urls = [
        f"https://image.pollinations.ai/prompt/{text}?width=640&height=640&nologo=true",
        f"https://gen.pollinations.ai/image/{text}?width=640&height=640",
    ]
    for attempt in range(3):
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 ComicCraft"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read()
                return Image.open(io.BytesIO(data)).convert("RGB")
            except Exception as e:
                print(f"[Free image try {attempt + 1} failed] {str(e)[:150]}")
        time.sleep(16)  # wait out the rate limit, then try again
    return None


def _placeholder(prompt, panel_no):
    img = Image.new("RGB", (640, 640), COLORS[(panel_no - 1) % len(COLORS)])
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 629, 629], outline=(30, 30, 30), width=5)
    draw.text((30, 30), f"Panel {panel_no} (placeholder image)", fill=(30, 30, 30))
    y = 80
    for line in textwrap.wrap(prompt, width=60)[:14]:
        draw.text((30, y), line, fill=(30, 30, 30))
        y += 22
    return img


def generate_image(prompt, art_style="comic book", panel_no=1):
    """Saves a square image in static/panels and returns the file path."""
    PANELS_DIR.mkdir(parents=True, exist_ok=True)
    full_prompt = f"{prompt}. {art_style} style comic panel, no text, vibrant colors."

    image = _gemini_image(full_prompt) or _free_image(full_prompt)
    if image is None:
        print(f"[Panel {panel_no}] All image sources failed, using placeholder.")
        image = _placeholder(prompt, panel_no)
    image = ImageOps.fit(image, (640, 640))

    safe = re.sub(r"[^a-zA-Z0-9]+", "_", prompt)[:30].strip("_")
    path = PANELS_DIR / f"panel{panel_no}_{safe}_{int(time.time())}.png"
    image.save(path)
    return str(path)