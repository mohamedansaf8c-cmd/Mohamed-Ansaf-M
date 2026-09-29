from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router

BASE_DIR = Path(__file__).parent
(BASE_DIR / "static" / "panels").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "static" / "exports").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ComicCraft")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(router)