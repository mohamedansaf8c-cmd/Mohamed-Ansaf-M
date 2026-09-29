import time
from pathlib import Path
from fpdf import FPDF

EXPORT_DIR = Path(__file__).parent / "static" / "exports"


def _clean(text):
    # The built-in PDF fonts only support Latin-1 characters.
    return text.encode("latin-1", "replace").decode("latin-1")


def save_pdf(layout):
    """Builds a PDF (one panel per page) and returns its file path."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(0, 10, _clean(f"Panel {panel['panel']}: {panel['title']}"), new_x="LMARGIN", new_y="NEXT")
        y = pdf.get_y() + 2
        pdf.image(panel["image_path"], x=15, y=y, w=180)
        pdf.set_y(y + 185)
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 7, _clean(panel["text"]), new_x="LMARGIN", new_y="NEXT")

    path = EXPORT_DIR / f"comic_{time.strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(str(path))
    return str(path)