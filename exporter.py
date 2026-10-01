"""Convert the Markdown business plan into a .docx file (free, python-docx)."""
import io
import re
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch


def _runs(par, text):
    for part in re.split(r"(\*\*[^*]+\*\*)", text):
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            par.add_run(part[2:-2]).bold = True
        else:
            par.add_run(part)


def markdown_to_docx(md: str) -> bytes:
    doc = Document()
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                ncols = max(len(r) for r in rows)
                table = doc.add_table(rows=len(rows), cols=ncols)
                table.style = "Table Grid"
                for r, row in enumerate(rows):
                    for c in range(ncols):
                        table.cell(r, c).text = row[c].replace("**", "") if c < len(row) else ""
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", s)
        if m:
            doc.add_heading(m.group(2).replace("**", ""), level=len(m.group(1)))
        elif re.match(r"^[-*]\s+", s):
            _runs(doc.add_paragraph(style="List Bullet"), re.sub(r"^[-*]\s+", "", s))
        elif re.match(r"^\d+\.\s+", s):
            _runs(doc.add_paragraph(style="List Number"), re.sub(r"^\d+\.\s+", "", s))
        elif s:
            _runs(doc.add_paragraph(), s)
        i += 1
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def markdown_to_pdf(md: str) -> bytes:
    """Render a simple PDF from Markdown-ish text. Keeps headings and paragraphs."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    h1 = ParagraphStyle("Heading1", parent=styles["Heading1"], spaceAfter=12)
    h2 = ParagraphStyle("Heading2", parent=styles["Heading2"], spaceAfter=8)

    story = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()
        if not s:
            story.append(Spacer(1, 6))
        elif s.startswith("### "):
            story.append(Paragraph(s[4:].replace("**", ""), h2))
        elif s.startswith("## "):
            story.append(Paragraph(s[3:].replace("**", ""), h1))
        elif s.startswith("# "):
            story.append(Paragraph(s[2:].replace("**", ""), h1))
        else:
            # basic inline bold handling
            text = s.replace("**", "<b>").replace("<b>", "<b>")
            # reportlab's Paragraph supports simple HTML-like tags
            story.append(Paragraph(text, normal))
        i += 1

    doc.build(story)
    buf.seek(0)
    return buf.read()
