"""
PDF Page Manipulator & Organizer for OmniDoc Studio Pro.
Provides:
- Page Rotation (90, 180, 270 degrees for all, odd, even, or custom page selections)
- Page Reordering & Deletion (reorder via ranges/indices, delete unwanted pages, reverse)
- Dynamic Page Numbering & Header/Footer stamping
"""

import io
from typing import List, Tuple, Optional
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color


def parse_page_indices(page_str: str, total_pages: int) -> List[int]:
    """
    Parses a page selection string (e.g., '1, 3, 5-8') into 0-indexed integer list.
    """
    pages = []
    if not page_str or not page_str.strip():
        return list(range(total_pages))

    tokens = [t.strip() for t in page_str.split(",") if t.strip()]
    for token in tokens:
        if "-" in token:
            parts = token.split("-")
            if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                start = max(1, int(parts[0].strip()))
                end = min(total_pages, int(parts[1].strip()))
                if start <= end:
                    for p in range(start, end + 1):
                        pages.append(p - 1)
                else:
                    for p in range(start, end - 1, -1):
                        pages.append(p - 1)
        elif token.isdigit():
            p = int(token)
            if 1 <= p <= total_pages:
                pages.append(p - 1)

    return pages


def rotate_pdf_pages(
    pdf_bytes: bytes,
    rotation_angle: int,
    target_mode: str = "all",
    custom_pages_str: str = ""
) -> bytes:
    """
    Rotates selected pages of a PDF by rotation_angle (90, 180, 270, or -90).
    target_mode can be 'all', 'odd', 'even', or 'custom'.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    total_pages = len(reader.pages)

    if target_mode == "all":
        targets = set(range(total_pages))
    elif target_mode == "odd":
        targets = {i for i in range(total_pages) if (i + 1) % 2 != 0}
    elif target_mode == "even":
        targets = {i for i in range(total_pages) if (i + 1) % 2 == 0}
    elif target_mode == "custom":
        targets = set(parse_page_indices(custom_pages_str, total_pages))
    else:
        targets = set(range(total_pages))

    for idx, page in enumerate(reader.pages):
        if idx in targets:
            # pypdf supports page.rotate(angle)
            page.rotate(rotation_angle)
        writer.add_page(page)

    out_stream = io.BytesIO()
    writer.write(out_stream)
    return out_stream.getvalue()


def reorder_and_delete_pages(
    pdf_bytes: bytes,
    order_str: str = "",
    delete_pages_str: str = "",
    reverse_order: bool = False
) -> bytes:
    """
    Reorders and deletes pages according to user instructions.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    total_pages = len(reader.pages)

    if order_str and order_str.strip():
        chosen_indices = parse_page_indices(order_str, total_pages)
    else:
        chosen_indices = list(range(total_pages))

    if delete_pages_str and delete_pages_str.strip():
        to_delete = set(parse_page_indices(delete_pages_str, total_pages))
        chosen_indices = [idx for idx in chosen_indices if idx not in to_delete]

    if reverse_order:
        chosen_indices.reverse()

    if not chosen_indices:
        raise ValueError("Resulting document has 0 pages. Please verify your page order or deletion selections.")

    for idx in chosen_indices:
        if 0 <= idx < total_pages:
            writer.add_page(reader.pages[idx])

    out_stream = io.BytesIO()
    writer.write(out_stream)
    return out_stream.getvalue()


def add_page_numbers(
    pdf_bytes: bytes,
    format_template: str = "Page {page} of {total}",
    position: str = "bottom_center",
    font_size: int = 10,
    margin_pts: float = 30.0,
    color_rgb: Tuple[float, float, float] = (0.25, 0.25, 0.25),
    start_page: int = 1
) -> bytes:
    """
    Stamps dynamic page numbers or headers/footers on each page of a PDF.
    position can be: 'bottom_center', 'bottom_right', 'bottom_left', 'top_center', 'top_right', 'top_left'.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    total_pages = len(reader.pages)

    for idx, page in enumerate(reader.pages):
        page_box = page.mediabox
        p_width = float(page_box.width)
        p_height = float(page_box.height)

        cur_num = idx + start_page
        text_str = format_template.format(page=cur_num, total=total_pages)

        # Generate single page overlay
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(p_width, p_height))
        can.setFont("Helvetica", font_size)
        can.setFillColor(Color(color_rgb[0], color_rgb[1], color_rgb[2]))

        # Calculate coordinates based on position
        if position == "bottom_center":
            can.drawCentredString(p_width / 2.0, margin_pts, text_str)
        elif position == "bottom_right":
            can.drawRightString(p_width - margin_pts, margin_pts, text_str)
        elif position == "bottom_left":
            can.drawString(margin_pts, margin_pts, text_str)
        elif position == "top_center":
            can.drawCentredString(p_width / 2.0, p_height - margin_pts, text_str)
        elif position == "top_right":
            can.drawRightString(p_width - margin_pts, p_height - margin_pts, text_str)
        elif position == "top_left":
            can.drawString(margin_pts, p_height - margin_pts, text_str)
        else:
            can.drawCentredString(p_width / 2.0, margin_pts, text_str)

        can.showPage()
        can.save()

        packet.seek(0)
        overlay_reader = PdfReader(packet)
        overlay_page = overlay_reader.pages[0]

        page.merge_page(overlay_page)
        writer.add_page(page)

    out_stream = io.BytesIO()
    writer.write(out_stream)
    return out_stream.getvalue()
