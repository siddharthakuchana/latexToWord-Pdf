import os
import io
import re
import tempfile
import pypdf
import docx
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


def sanitize_filename(name: str, default_name: str, target_ext: str) -> str:
    """
    Cleans and standardizes output filenames, stripping illegal filesystem characters,
    ensuring correct target extension, and trimming spaces.
    """
    target_ext = target_ext.lstrip(".")
    if not name or not name.strip():
        base = default_name
    else:
        base = name.strip()
        # Remove existing file extension if user typed it in
        base = re.sub(r'\.(pdf|docx|doc|tex|txt|rtf|odt)$', '', base, flags=re.IGNORECASE)
        # Remove invalid filename characters
        base = re.sub(r'[\\/*?:"<>|]', '_', base)
        base = base.strip('. ')
        if not base:
            base = default_name
    return f"{base}.{target_ext}"


def convert_latex_to_docx(content):
    temp_dir = tempfile.mkdtemp()
    tex_file = os.path.join(temp_dir, "document.tex")

    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(content)

    docx_file = os.path.join(temp_dir, "document.docx")

    try:
        import pypandoc
    except ImportError:
        raise ImportError("pypandoc is required for LaTeX conversion. Please run: pip install pypandoc")

    pypandoc.convert_file(
        tex_file,
        "docx",
        outputfile=docx_file
    )

    return docx_file


def convert_pdf_to_docx(pdf_input, output_docx=None):
    """
    Converts a PDF file (path or bytes) to an editable Microsoft Word (.docx) document.
    Extracts text paragraphs, detects headings, preserves page breaks, and embeds extracted images.
    """
    if isinstance(pdf_input, (bytes, bytearray)):
        pdf_stream = io.BytesIO(pdf_input)
    elif hasattr(pdf_input, "read"):
        pdf_stream = pdf_input
    else:
        pdf_stream = open(pdf_input, "rb")

    reader = pypdf.PdfReader(pdf_stream)
    doc = docx.Document()

    # Configure default styling
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x1e, 0x29, 0x3b)

    total_pages = len(reader.pages)
    if total_pages == 0:
        doc.add_paragraph("Empty PDF document.")
    else:
        for idx, page in enumerate(reader.pages):
            if idx > 0:
                doc.add_page_break()

            # Extract text
            page_text = page.extract_text() or ""
            lines = [line.strip() for line in page_text.splitlines()]

            current_para = []
            for line in lines:
                if not line:
                    if current_para:
                        doc.add_paragraph(" ".join(current_para))
                        current_para = []
                elif len(line) < 45 and not line.endswith(('.', ':', ';', ',')) and len(current_para) == 0:
                    p = doc.add_heading(line, level=2)
                    p.paragraph_format.space_before = Pt(8)
                    p.paragraph_format.space_after = Pt(4)
                else:
                    current_para.append(line)
            if current_para:
                doc.add_paragraph(" ".join(current_para))

            # Extract embedded images and append into DOCX
            try:
                for img_idx, img_file in enumerate(page.images):
                    img_temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    img_temp.write(img_file.data)
                    img_temp.close()
                    try:
                        doc.add_picture(img_temp.name, width=Inches(4.5))
                    except Exception:
                        pass
                    finally:
                        if os.path.exists(img_temp.name):
                            os.remove(img_temp.name)
            except Exception:
                pass

    if not output_docx:
        temp_dir = tempfile.mkdtemp()
        output_docx = os.path.join(temp_dir, "document.docx")

    doc.save(output_docx)
    return output_docx


def convert_docx_to_pdf_pure_python(docx_file, output_pdf=None):
    """
    Pure Python converter from DOCX to PDF using python-docx and reportlab.
    Ensures DOCX -> PDF works anywhere even if Microsoft Word is not installed.
    """
    if not output_pdf:
        temp_dir = tempfile.mkdtemp()
        output_pdf = os.path.join(temp_dir, "converted.pdf")

    doc = docx.Document(docx_file)
    pdf_doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontSize = 10
    normal_style.leading = 14
    normal_style.textColor = colors.HexColor("#1e293b")

    heading1_style = styles["Heading1"]
    heading1_style.fontSize = 16
    heading1_style.leading = 20
    heading1_style.textColor = colors.HexColor("#0f172a")

    heading2_style = styles["Heading2"]
    heading2_style.fontSize = 13
    heading2_style.leading = 16
    heading2_style.textColor = colors.HexColor("#334155")

    story = []

    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            story.append(Spacer(1, 8))
            continue

        if p.style.name.startswith("Heading 1"):
            story.append(Paragraph(txt, heading1_style))
            story.append(Spacer(1, 6))
        elif p.style.name.startswith("Heading 2") or p.style.name.startswith("Heading"):
            story.append(Paragraph(txt, heading2_style))
            story.append(Spacer(1, 4))
        else:
            safe_text = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe_text, normal_style))
            story.append(Spacer(1, 4))

    for table in doc.tables:
        table_data = []
        for row in table.rows:
            row_data = [cell.text.strip() for cell in row.cells]
            table_data.append(row_data)
        if table_data:
            t = Table(table_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ]))
            story.append(t)
            story.append(Spacer(1, 10))

    if not story:
        story.append(Paragraph("Empty Document", normal_style))

    pdf_doc.build(story)
    return output_pdf


def convert_docx_to_pdf(docx_file, output_pdf=None):
    """
    Converts a DOCX file to PDF. Attempts Microsoft Word COM automation first (via docx2pdf),
    with an automatic fallback to pure-Python rendering.
    """
    if not output_pdf:
        temp_dir = tempfile.mkdtemp()
        output_pdf = os.path.join(temp_dir, "document.pdf")

    # Try docx2pdf (Fast & pixel-perfect when Word is present)
    try:
        import docx2pdf
        docx2pdf.convert(docx_file, output_pdf)
        if os.path.exists(output_pdf) and os.path.getsize(output_pdf) > 0:
            return output_pdf
    except Exception:
        pass

    # Automatic pure-Python fallback
    return convert_docx_to_pdf_pure_python(docx_file, output_pdf)


def process_pdf_to_pdf(pdf_input, mode="clean_flatten", output_pdf=None):
    """
    Re-processes a PDF file (clean syntax, flatten interactive annotations/forms, optimize streams).
    Outputs a standardized, sanitized PDF.
    """
    if isinstance(pdf_input, (bytes, bytearray)):
        pdf_stream = io.BytesIO(pdf_input)
    elif hasattr(pdf_input, "read"):
        pdf_stream = pdf_input
    else:
        pdf_stream = open(pdf_input, "rb")

    reader = pypdf.PdfReader(pdf_stream)
    writer = pypdf.PdfWriter()

    for page in reader.pages:
        if mode in ("optimize", "clean_flatten"):
            try:
                page.compress_content_streams()
            except Exception:
                pass
        writer.add_page(page)

    if mode in ("flatten", "clean_flatten"):
        try:
            for page in writer.pages:
                if "/Annots" in page:
                    del page["/Annots"]
        except Exception:
            pass

    if not output_pdf:
        temp_dir = tempfile.mkdtemp()
        output_pdf = os.path.join(temp_dir, "processed.pdf")

    with open(output_pdf, "wb") as f:
        writer.write(f)

    return output_pdf