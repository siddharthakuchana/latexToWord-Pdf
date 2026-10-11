"""
PDF Text, Table & OCR Extraction Studio for OmniDoc Studio Pro.
Provides:
- Native text extraction per page with word & character counts via pypdf
- OCR text extraction from scanned documents via pytesseract with graceful fallbacks
- Formatted Markdown and TXT export
"""

import io
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    PYTESSERACT_AVAILABLE = False


def check_ocr_availability() -> Tuple[bool, str]:
    """
    Checks whether pytesseract package and Tesseract binary are installed and functional.
    """
    if not PYTESSERACT_AVAILABLE:
        return False, "pytesseract library not installed."
    try:
        pytesseract.get_tesseract_version()
        return True, "Tesseract OCR engine is active and ready."
    except Exception as e:
        return False, f"Tesseract engine binary not found on system PATH: {e}"


def extract_native_text(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Extracts text from all pages using pypdf.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)
    pages_text: List[Dict[str, Any]] = []

    total_words = 0
    total_chars = 0

    full_markdown_lines = []
    full_plain_lines = []

    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        raw_text = page.extract_text() or ""
        clean_text = raw_text.strip()

        words = len(clean_text.split()) if clean_text else 0
        chars = len(clean_text)

        total_words += words
        total_chars += chars

        pages_text.append({
            "page_number": page_num,
            "text": clean_text,
            "word_count": words,
            "char_count": chars,
            "is_empty": (words == 0)
        })

        full_markdown_lines.append(f"## Page {page_num}\n\n{clean_text if clean_text else '*(No text detected on this page)*'}\n")
        full_plain_lines.append(f"--- PAGE {page_num} ---\n\n{clean_text}\n")

    markdown_doc = "\n".join(full_markdown_lines)
    plain_doc = "\n".join(full_plain_lines)

    # Estimate reading time (average 200 words per minute)
    reading_time_mins = max(1, round(total_words / 200.0)) if total_words > 0 else 0

    return {
        "mode": "native",
        "total_pages": total_pages,
        "total_words": total_words,
        "total_chars": total_chars,
        "reading_time_mins": reading_time_mins,
        "pages": pages_text,
        "markdown": markdown_doc,
        "plain_text": plain_doc,
        "empty_pages_count": sum(1 for p in pages_text if p["is_empty"])
    }


def extract_ocr_text(
    pdf_bytes: bytes,
    dpi: int = 150,
    lang: str = "eng"
) -> Dict[str, Any]:
    """
    Renders pages via pypdfium2 and performs Optical Character Recognition via pytesseract.
    """
    is_available, status_msg = check_ocr_availability()
    if not is_available:
        raise RuntimeError(f"OCR engine is not available: {status_msg}")

    pdf_doc = pdfium.PdfDocument(pdf_bytes)
    total_pages = len(pdf_doc)
    scale = max(0.5, float(dpi) / 72.0)

    pages_text: List[Dict[str, Any]] = []
    total_words = 0
    total_chars = 0

    full_markdown_lines = []
    full_plain_lines = []

    for p_idx in range(total_pages):
        page_num = p_idx + 1
        page = pdf_doc.get_page(p_idx)
        bmp = page.render(scale=scale)
        pil_img = bmp.to_pil().convert("L")  # Grayscale for better OCR speed/accuracy

        ocr_text = pytesseract.image_to_string(pil_img, lang=lang) or ""
        clean_text = ocr_text.strip()

        words = len(clean_text.split()) if clean_text else 0
        chars = len(clean_text)

        total_words += words
        total_chars += chars

        pages_text.append({
            "page_number": page_num,
            "text": clean_text,
            "word_count": words,
            "char_count": chars,
            "is_empty": (words == 0)
        })

        full_markdown_lines.append(f"## Page {page_num} (OCR)\n\n{clean_text if clean_text else '*(No OCR text detected)*'}\n")
        full_plain_lines.append(f"--- PAGE {page_num} (OCR) ---\n\n{clean_text}\n")

    markdown_doc = "\n".join(full_markdown_lines)
    plain_doc = "\n".join(full_plain_lines)
    reading_time_mins = max(1, round(total_words / 200.0)) if total_words > 0 else 0

    return {
        "mode": "ocr",
        "total_pages": total_pages,
        "total_words": total_words,
        "total_chars": total_chars,
        "reading_time_mins": reading_time_mins,
        "pages": pages_text,
        "markdown": markdown_doc,
        "plain_text": plain_doc,
        "empty_pages_count": sum(1 for p in pages_text if p["is_empty"])
    }
