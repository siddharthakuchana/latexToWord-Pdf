"""
PDF Security & Privacy Suite for OmniDoc Studio Pro.
Provides:
- Encryption & Password Protection (User & Owner passwords with fine-grained permissions)
- Decryption / Password Removal
- Custom Watermarking (Text & Image overlay with opacity, angle, and positioning)
- Metadata Inspection, Editing, and Privacy Scrubbing
"""

import io
from typing import Dict, Any, Optional, Tuple
from pypdf import PdfReader, PdfWriter
from pypdf.constants import UserAccessPermissions
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from PIL import Image


def encrypt_pdf(
    pdf_bytes: bytes,
    user_password: str,
    owner_password: Optional[str] = None,
    allow_printing: bool = True,
    allow_copying: bool = True
) -> bytes:
    """
    Encrypts a PDF with user and optional owner password.
    Configures permissions for printing and copying content.
    """
    if not user_password:
        raise ValueError("User password must be provided.")

    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    owner_pwd = owner_password if owner_password else user_password

    # Configure encryption flags
    perms = UserAccessPermissions(0)
    if allow_printing:
        perms |= UserAccessPermissions.PRINT | UserAccessPermissions.PRINT_TO_REPRESENTATION
    if allow_copying:
        perms |= UserAccessPermissions.EXTRACT | UserAccessPermissions.EXTRACT_TEXT_AND_GRAPHICS
    perms |= UserAccessPermissions.FILL_FORM_FIELDS

    writer.encrypt(
        user_password=user_password,
        owner_password=owner_pwd,
        use_128bit=True,
        permissions_flag=perms
    )

    out_stream = io.BytesIO()
    writer.write(out_stream)
    return out_stream.getvalue()


def decrypt_pdf(pdf_bytes: bytes, password: str) -> bytes:
    """
    Decrypts a password-protected PDF and returns an unencrypted PDF stream.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    if reader.is_encrypted:
        decrypt_success = reader.decrypt(password)
        if not decrypt_success:
            raise ValueError("Incorrect password. Unable to unlock document.")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    out_stream = io.BytesIO()
    writer.write(out_stream)
    return out_stream.getvalue()


def create_text_watermark_page(
    width: float,
    height: float,
    text: str,
    font_size: int = 36,
    angle: float = 45,
    opacity: float = 0.25,
    color_rgb: Tuple[float, float, float] = (0.5, 0.5, 0.5),
    position: str = "center"
) -> bytes:
    """
    Generates a single-page transparent PDF in memory containing the specified watermark text.
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))

    # Configure font and transparency
    can.setFont("Helvetica-Bold", font_size)
    can.setFillColor(Color(color_rgb[0], color_rgb[1], color_rgb[2], alpha=opacity))

    can.saveState()

    if position == "center":
        can.translate(width / 2.0, height / 2.0)
        can.rotate(angle)
        can.drawCentredString(0, 0, text)
    elif position == "header":
        can.translate(width / 2.0, height - 40)
        can.drawCentredString(0, 0, text)
    elif position == "footer":
        can.translate(width / 2.0, 30)
        can.drawCentredString(0, 0, text)
    elif position == "tile":
        # Tiled diagonal watermarks
        can.rotate(angle)
        for x in range(int(-width), int(width * 2), 200):
            for y in range(int(-height), int(height * 2), 120):
                can.drawCentredString(x, y, text)

    can.restoreState()
    can.showPage()
    can.save()

    packet.seek(0)
    return packet.getvalue()


def create_image_watermark_page(
    width: float,
    height: float,
    image_bytes: bytes,
    opacity: float = 0.3,
    max_scale: float = 0.5
) -> bytes:
    """
    Generates a single-page PDF containing a centered watermark image with alpha transparency.
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))

    img = Image.open(io.BytesIO(image_bytes))
    img_w, img_h = img.size

    # Fit image to max_scale percentage of page width/height
    scale_w = (width * max_scale) / img_w
    scale_h = (height * max_scale) / img_h
    scale = min(scale_w, scale_h, 1.0)

    target_w = img_w * scale
    target_h = img_h * scale
    pos_x = (width - target_w) / 2.0
    pos_y = (height - target_h) / 2.0

    # Ensure image supports transparency or convert
    img_stream = io.BytesIO()
    img.save(img_stream, format="PNG")
    img_stream.seek(0)

    from reportlab.lib.utils import ImageReader
    ir = ImageReader(img_stream)

    can.saveState()
    can.setFillAlpha(opacity)
    can.drawImage(ir, pos_x, pos_y, width=target_w, height=target_h, mask='auto', preserveAspectRatio=True)
    can.restoreState()
    can.showPage()
    can.save()

    packet.seek(0)
    return packet.getvalue()


def watermark_pdf(
    pdf_bytes: bytes,
    text: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    opacity: float = 0.25,
    angle: float = 45,
    font_size: int = 36,
    color_rgb: Tuple[float, float, float] = (0.5, 0.5, 0.5),
    position: str = "center"
) -> bytes:
    """
    Applies a watermark (text or image) to each page of a PDF document.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    for page in reader.pages:
        page_box = page.mediabox
        p_width = float(page_box.width)
        p_height = float(page_box.height)

        if image_bytes:
            wm_pdf_bytes = create_image_watermark_page(
                width=p_width,
                height=p_height,
                image_bytes=image_bytes,
                opacity=opacity
            )
        else:
            wm_text = text if text else "CONFIDENTIAL"
            wm_pdf_bytes = create_text_watermark_page(
                width=p_width,
                height=p_height,
                text=wm_text,
                font_size=font_size,
                angle=angle,
                opacity=opacity,
                color_rgb=color_rgb,
                position=position
            )

        wm_reader = PdfReader(io.BytesIO(wm_pdf_bytes))
        wm_page = wm_reader.pages[0]

        # Merge watermark on top of page content
        page.merge_page(wm_page)
        writer.add_page(page)

    out_stream = io.BytesIO()
    writer.write(out_stream)
    return out_stream.getvalue()


def get_pdf_metadata(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Extracts all metadata and page information from a PDF.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    meta = reader.metadata or {}

    def clean_val(val):
        return str(val) if val is not None else ""

    return {
        "title": clean_val(meta.get("/Title")),
        "author": clean_val(meta.get("/Author")),
        "subject": clean_val(meta.get("/Subject")),
        "creator": clean_val(meta.get("/Creator")),
        "producer": clean_val(meta.get("/Producer")),
        "creation_date": clean_val(meta.get("/CreationDate")),
        "mod_date": clean_val(meta.get("/ModDate")),
        "page_count": len(reader.pages),
        "is_encrypted": reader.is_encrypted,
        "raw": {k: str(v) for k, v in meta.items()}
    }


def update_pdf_metadata(pdf_bytes: bytes, metadata_updates: Dict[str, str]) -> bytes:
    """
    Updates specific metadata fields on a PDF.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Convert readable keys to PDF metadata keys
    key_mapping = {
        "title": "/Title",
        "author": "/Author",
        "subject": "/Subject",
        "creator": "/Creator",
        "producer": "/Producer"
    }

    meta_to_add = {}
    for k, v in metadata_updates.items():
        pdf_key = key_mapping.get(k.lower(), k)
        meta_to_add[pdf_key] = v

    writer.add_metadata(meta_to_add)

    out_stream = io.BytesIO()
    writer.write(out_stream)
    return out_stream.getvalue()


def strip_pdf_metadata(pdf_bytes: bytes) -> bytes:
    """
    Wipes all author, creation tool, producer, and identifying metadata from the PDF.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Empty metadata dictionary
    writer.add_metadata({})

    out_stream = io.BytesIO()
    writer.write(out_stream)
    return out_stream.getvalue()
