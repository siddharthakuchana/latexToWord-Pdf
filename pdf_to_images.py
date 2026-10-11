"""
Dedicated PDF-to-Image & High-Res Rasterizer for OmniDoc Studio Pro.
Converts PDF documents into high-fidelity image formats (PNG, JPEG, WEBP, TIFF)
with customizable DPI presets (72, 150, 300) and package them into ZIP archives.
"""

import io
import zipfile
from typing import List, Dict, Any, Optional
from PIL import Image
import pypdfium2 as pdfium


def convert_pdf_to_images(
    pdf_bytes: bytes,
    dpi: int = 150,
    output_format: str = "PNG",
    jpeg_quality: int = 85,
    base_filename: str = "document"
) -> Dict[str, Any]:
    """
    Renders all pages of a PDF to high-fidelity images using pypdfium2.
    Returns individual images and a unified ZIP archive.
    """
    fmt_upper = output_format.upper()
    if fmt_upper not in ["PNG", "JPEG", "JPG", "WEBP", "TIFF"]:
        fmt_upper = "PNG"

    ext_map = {
        "PNG": "png",
        "JPEG": "jpg",
        "JPG": "jpg",
        "WEBP": "webp",
        "TIFF": "tiff"
    }
    file_ext = ext_map.get(fmt_upper, "png")
    mime_map = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "webp": "image/webp",
        "tiff": "image/tiff"
    }
    mime_type = mime_map.get(file_ext, "image/png")

    pdf_doc = pdfium.PdfDocument(pdf_bytes)
    total_pages = len(pdf_doc)

    # Scale factor relative to 72 points per inch
    scale = max(0.5, float(dpi) / 72.0)

    pages_data: List[Dict[str, Any]] = []
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for p_idx in range(total_pages):
            page = pdf_doc.get_page(p_idx)
            # Render page to bitmap
            bitmap = page.render(scale=scale)
            pil_image = bitmap.to_pil()

            # Prepare image stream
            img_io = io.BytesIO()
            save_fmt = "JPEG" if fmt_upper in ["JPEG", "JPG"] else fmt_upper

            if save_fmt == "JPEG":
                # Convert RGBA to RGB with white background
                if pil_image.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", pil_image.size, (255, 255, 255))
                    if pil_image.mode == "P":
                        pil_image = pil_image.convert("RGBA")
                    bg.paste(pil_image, mask=pil_image.split()[3])
                    pil_image = bg
                pil_image.save(img_io, format="JPEG", quality=jpeg_quality, optimize=True)
            elif save_fmt == "WEBP":
                pil_image.save(img_io, format="WEBP", quality=jpeg_quality)
            else:
                pil_image.save(img_io, format=save_fmt)

            img_bytes = img_io.getvalue()
            page_num = p_idx + 1
            filename = f"{base_filename}_page_{page_num:03d}.{file_ext}"

            # Add to zip
            zf.writestr(filename, img_bytes)

            pages_data.append({
                "page_number": page_num,
                "filename": filename,
                "bytes": img_bytes,
                "pil_image": pil_image,
                "width": pil_image.width,
                "height": pil_image.height,
                "size_bytes": len(img_bytes),
                "mime_type": mime_type
            })

    zip_bytes = zip_buffer.getvalue()
    zip_filename = f"{base_filename}_images_{dpi}dpi.zip"

    return {
        "total_pages": total_pages,
        "dpi": dpi,
        "format": fmt_upper,
        "pages": pages_data,
        "zip_bytes": zip_bytes,
        "zip_filename": zip_filename,
        "zip_size_bytes": len(zip_bytes)
    }
