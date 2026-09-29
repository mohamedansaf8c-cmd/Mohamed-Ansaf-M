import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it to a .env file in the project root.")

client = genai.Client(api_key=API_KEY)

# Each list is tried in order until one works.
TEXT_MODELS = ["gemini-3.6-flash", "gemini-3.1-flash-lite", "gemini-3.5-flash-lite"]
PRO_MODELS = ["gemini-3.1-pro-preview"] + TEXT_MODELS
IMAGE_MODELS = ["gemini-3.1-flash-image", "gemini-3.1-flash-image-preview", "gemini-2.5-flash-image"]


def ask(models, contents, config=None):
    last_error = None
    for name in models:
        try:
            return client.models.generate_content(model=name, contents=contents, config=config)
        except Exception as e:
            print(f"[Gemini model {name} failed] {e}")
            last_error = e
    raise last_error