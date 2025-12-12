from docx import Document
from docx.shared import Pt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from typing import Dict
import os

def generate_docx(report: Dict, out_path: str):
    doc = Document()
    doc.add_heading(report['title'], 0)
    doc.add_paragraph(report.get('summary', ''))
    for sec in report.get('sections', []):
        doc.add_heading(sec.get('heading', 'Section'), level=1)
        doc.add_paragraph(sec.get('content', ''))
    doc.save(out_path)
    return out_path

def generate_pdf_from_text(report: Dict, out_path: str):
    c = canvas.Canvas(out_path, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, report['title'])
    y -= 30
    c.setFont("Helvetica", 11)
    c.drawString(50, y, report.get('summary', ''))
    y -= 40
    for sec in report.get('sections', []):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, sec.get('heading', ''))
        y -= 18
        c.setFont("Helvetica", 10)
        for line in sec.get('content', '').splitlines():
            c.drawString(50, y, line)
            y -= 12
            if y < 60:
                c.showPage()
                y = height - 50
    c.save()
    return out_path
