import os
from datetime import datetime
from src.tools.doc_generator import generate_docx, generate_pdf_from_text
from src.config import cfg

def write_report(structured_report: dict) -> dict:
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    title = structured_report.get("title", "Research Report")
    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-")).rstrip()
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    base = f"{safe_title[:50]}_{timestamp}"
    docx_path = os.path.join(cfg.OUTPUT_DIR, base + ".docx")
    pdf_path = os.path.join(cfg.OUTPUT_DIR, base + ".pdf")
    generate_docx(structured_report, docx_path)
    generate_pdf_from_text(structured_report, pdf_path)
    return {"docx": docx_path, "pdf": pdf_path}
