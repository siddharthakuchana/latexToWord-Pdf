"""
Visual Document Comparator & Diff Engine for OmniDoc Studio Pro.
Compares two versions of a PDF document (v1 vs v2) side-by-side:
- Computes pixel-level difference maps
- Generates 3-panel visual diff composites (Doc A | Visual Diff Highlight | Doc B)
- Calculates similarity score and change percentage metrics
- Exports diff inspection report packages (ZIP)
"""

import io
import zipfile
from typing import List, Dict, Any, Tuple
import numpy as np
from PIL import Image, ImageOps
import pypdfium2 as pdfium


def compare_pages(
    img_a: Image.Image,
    img_b: Image.Image,
    threshold: int = 25
) -> Tuple[Image.Image, Image.Image, float, int]:
    """
    Compares two PIL images of the same page.
    Returns:
    - diff_highlight_img: Diff mask showing changes highlighted in vibrant magenta/red.
    - composite_img: 3-panel comparison (Doc A | Diff Overlay | Doc B).
    - similarity_pct: Percentage of matching pixels (0.0 to 100.0).
    - changed_pixels: Total count of pixels differing beyond threshold.
    """
    # Normalize sizes to maximum dimensions
    target_w = max(img_a.width, img_b.width)
    target_h = max(img_a.height, img_b.height)

    # Pad images if dimensions differ
    def pad_image(img: Image.Image) -> Image.Image:
        if img.width == target_w and img.height == target_h:
            return img.convert("RGB")
        new_img = Image.new("RGB", (target_w, target_h), (255, 255, 255))
        new_img.paste(img.convert("RGB"), (0, 0))
        return new_img

    norm_a = pad_image(img_a)
    norm_b = pad_image(img_b)

    arr_a = np.array(norm_a, dtype=np.int16)
    arr_b = np.array(norm_b, dtype=np.int16)

    # Absolute difference per channel
    abs_diff = np.abs(arr_a - arr_b)
    diff_magnitude = np.max(abs_diff, axis=2)

    diff_mask = diff_magnitude > threshold
    changed_pixels = int(np.sum(diff_mask))
    total_pixels = target_w * target_h
    similarity_pct = max(0.0, min(100.0, (1.0 - (changed_pixels / total_pixels)) * 100.0))

    # Create highlighted diff image
    # Background: muted gray/white version of Doc B
    bg_gray = np.array(ImageOps.grayscale(norm_b).convert("RGB"), dtype=np.uint8)
    bg_gray = (bg_gray * 0.7 + 76).astype(np.uint8)  # soften background

    diff_visual = bg_gray.copy()
    # Where pixels differ: bright red/magenta overlay (244, 63, 94)
    diff_visual[diff_mask] = [244, 63, 94]
    diff_highlight_img = Image.fromarray(diff_visual, "RGB")

    # Build 3-panel composite: [Doc A | Visual Diff Highlight | Doc B]
    separator_width = 10
    total_comp_w = (target_w * 3) + (separator_width * 2)
    composite_img = Image.new("RGB", (total_comp_w, target_h), (30, 41, 59))

    composite_img.paste(norm_a, (0, 0))
    composite_img.paste(diff_highlight_img, (target_w + separator_width, 0))
    composite_img.paste(norm_b, ((target_w * 2) + (separator_width * 2), 0))

    return diff_highlight_img, composite_img, similarity_pct, changed_pixels


def compare_pdfs(
    pdf_bytes_a: bytes,
    pdf_bytes_b: bytes,
    dpi: int = 150,
    threshold: int = 30
) -> Dict[str, Any]:
    """
    Renders and compares all pages between two PDF documents.
    """
    doc_a = pdfium.PdfDocument(pdf_bytes_a)
    doc_b = pdfium.PdfDocument(pdf_bytes_b)

    count_a = len(doc_a)
    count_b = len(doc_b)
    max_pages = max(count_a, count_b)
    scale = max(0.5, float(dpi) / 72.0)

    page_results: List[Dict[str, Any]] = []
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for p_idx in range(max_pages):
            page_num = p_idx + 1

            # Render page A
            if p_idx < count_a:
                bmp_a = doc_a.get_page(p_idx).render(scale=scale)
                img_a = bmp_a.to_pil().convert("RGB")
            else:
                img_a = Image.new("RGB", (600, 800), (240, 240, 240))

            # Render page B
            if p_idx < count_b:
                bmp_b = doc_b.get_page(p_idx).render(scale=scale)
                img_b = bmp_b.to_pil().convert("RGB")
            else:
                img_b = Image.new("RGB", (600, 800), (240, 240, 240))

            diff_img, comp_img, sim_pct, changed_px = compare_pages(img_a, img_b, threshold=threshold)

            # Save composite image bytes
            comp_io = io.BytesIO()
            comp_img.save(comp_io, format="JPEG", quality=85)
            comp_bytes = comp_io.getvalue()

            diff_filename = f"diff_page_{page_num:03d}.jpg"
            zf.writestr(diff_filename, comp_bytes)

            page_results.append({
                "page_number": page_num,
                "in_doc_a": (p_idx < count_a),
                "in_doc_b": (p_idx < count_b),
                "similarity_pct": round(sim_pct, 2),
                "change_pct": round(100.0 - sim_pct, 2),
                "changed_pixels": changed_px,
                "composite_bytes": comp_bytes,
                "composite_image": comp_img,
                "img_a": img_a,
                "img_b": img_b,
                "diff_img": diff_img
            })

    zip_bytes = zip_buffer.getvalue()
    overall_sim = np.mean([p["similarity_pct"] for p in page_results]) if page_results else 100.0

    return {
        "pages_a": count_a,
        "pages_b": count_b,
        "total_compared_pages": max_pages,
        "overall_similarity": round(float(overall_sim), 2),
        "pages": page_results,
        "zip_bytes": zip_bytes,
        "zip_filename": "pdf_visual_diff_report.zip"
    }
