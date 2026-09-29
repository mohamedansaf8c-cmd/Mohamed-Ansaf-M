from pathlib import Path

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


class PromptRequest(BaseModel):
    prompt: str
    character: str = "Hero"
    setting: str = "forest"
    tone: str = "dramatic"
    art_style: str = "comic book"


def create_comic(prompt, character, setting, tone, art_style):
    outline = generate_outline(prompt, character, setting, tone, art_style)
    story = generate_story(outline, character, tone)
    images = [
        generate_image(p["image_prompt"], art_style, n)
        for n, p in enumerate(outline, start=1)
    ]
    layout = build_comic_layout(outline, story, images)
    pdf_path = save_pdf(layout)
    return layout, pdf_path


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@router.post("/generate")
def generate(
    request: Request,
    prompt: str = Form(...),
    character: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        layout, pdf_path = create_comic(prompt, character, setting, tone, art_style)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {e}")
    return templates.TemplateResponse(
        request, "comic_preview.html", {"layout": layout, "pdf_name": Path(pdf_path).name}
    )


@router.post("/generate-comic/json")
def generate_json(data: PromptRequest):
    try:
        layout, pdf_path = create_comic(
            data.prompt, data.character, data.setting, data.tone, data.art_style
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {e}")
    return {"layout": layout, "pdf_path": pdf_path}


@router.get("/export-success")
def export_success(request: Request, file: str):
    return templates.TemplateResponse(
        request, "export_success.html", {"pdf_name": Path(file).name}
    )


@router.get("/test-image")
def test_image(prompt: str = "a brave fox in an enchanted forest"):
    try:
        return FileResponse(generate_image(prompt))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")