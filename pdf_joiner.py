import io
import os
import zipfile
from PIL import Image, ImageOps
from pypdf import PdfReader, PdfWriter

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS.union({".pdf"})


def get_file_info(file_source, filename="Document"):
    """
    Inspects any supported file (PDF or Image) and returns metadata:
      - 'filename': str
      - 'file_type': 'pdf' | 'image'
      - 'format_label': e.g. 'PDF', 'PNG', 'JPEG', etc.
      - 'page_count': int
      - 'size_bytes': int
      - 'dimensions': (w, h) or None
      - 'is_encrypted': bool
      - 'valid': bool
      - 'error': str or None
    """
    size_bytes = 0
    ext = os.path.splitext(filename)[1].lower()

    # Obtain bytes
    try:
        if isinstance(file_source, (bytes, bytearray)):
            raw_bytes = file_source
        elif hasattr(file_source, "read"):
            raw_bytes = file_source.read()
            if hasattr(file_source, "seek"):
                file_source.seek(0)
        else:
            with open(file_source, "rb") as f:
                raw_bytes = f.read()

        size_bytes = len(raw_bytes)
        if size_bytes == 0:
            return {
                "filename": filename,
                "file_type": "unknown",
                "format_label": ext.upper().lstrip(".") or "UNKNOWN",
                "page_count": 0,
                "size_bytes": 0,
                "dimensions": None,
                "is_encrypted": False,
                "valid": False,
                "error": "File is empty (0 bytes)."
            }

        # Check if PDF
        if ext == ".pdf" or raw_bytes.startswith(b"%PDF"):
            try:
                reader = PdfReader(io.BytesIO(raw_bytes))
                is_encrypted = reader.is_encrypted
                if is_encrypted:
                    try:
                        reader.decrypt("")
                    except Exception:
                        pass
                page_count = len(reader.pages)
                return {
                    "filename": filename,
                    "file_type": "pdf",
                    "format_label": "PDF",
                    "page_count": page_count,
                    "size_bytes": size_bytes,
                    "dimensions": None,
                    "is_encrypted": is_encrypted,
                    "valid": True,
                    "error": None
                }
            except Exception as e:
                return {
                    "filename": filename,
                    "file_type": "pdf",
                    "format_label": "PDF",
                    "page_count": 0,
                    "size_bytes": size_bytes,
                    "dimensions": None,
                    "is_encrypted": False,
                    "valid": False,
                    "error": f"Invalid PDF: {e}"
                }

        # Check if Image
        try:
            with Image.open(io.BytesIO(raw_bytes)) as img:
                img_format = (img.format or ext.lstrip(".")).upper()
                # Check for multi-frame images like animated GIF / multi-page TIFF
                frame_count = getattr(img, "n_frames", 1)
                dims = (img.width, img.height)

                return {
                    "filename": filename,
                    "file_type": "image",
                    "format_label": img_format,
                    "page_count": frame_count,
                    "size_bytes": size_bytes,
                    "dimensions": dims,
                    "is_encrypted": False,
                    "valid": True,
                    "error": None
                }
        except Exception as img_err:
            return {
                "filename": filename,
                "file_type": "unknown",
                "format_label": ext.upper().lstrip(".") or "UNKNOWN",
                "page_count": 0,
                "size_bytes": size_bytes,
                "dimensions": None,
                "is_encrypted": False,
                "valid": False,
                "error": f"Unsupported or corrupted file: {img_err}"
            }

    except Exception as exc:
        return {
            "filename": filename,
            "file_type": "unknown",
            "format_label": ext.upper().lstrip(".") or "UNKNOWN",
            "page_count": 0,
            "size_bytes": size_bytes,
            "dimensions": None,
            "is_encrypted": False,
            "valid": False,
            "error": str(exc)
        }


# Alias for backward compatibility
get_pdf_info = get_file_info


def convert_image_to_pdf_bytes(image_source, filename="image"):
    """
    Converts a single image or multi-frame image (TIFF) into a PDF byte buffer.
    Handles color space conversion (RGBA/Palette -> RGB) and EXIF orientation.
    """
    if isinstance(image_source, (bytes, bytearray)):
        raw_bytes = image_source
    elif hasattr(image_source, "read"):
        raw_bytes = image_source.read()
        if hasattr(image_source, "seek"):
            image_source.seek(0)
    else:
        with open(image_source, "rb") as f:
            raw_bytes = f.read()

    with Image.open(io.BytesIO(raw_bytes)) as img:
        frames = []
        n_frames = getattr(img, "n_frames", 1)

        for frame_idx in range(n_frames):
            img.seek(frame_idx)
            frame = img.copy()
            # Transpose according to EXIF orientation
            try:
                frame = ImageOps.exif_transpose(frame)
            except Exception:
                pass

            # Convert to RGB for PDF output
            if frame.mode in ("RGBA", "LA"):
                # Composite over white background
                bg = Image.new("RGB", frame.size, (255, 255, 255))
                alpha = frame.split()[-1]
                bg.paste(frame.convert("RGB"), mask=alpha)
                frame = bg
            elif frame.mode != "RGB":
                frame = frame.convert("RGB")

            frames.append(frame)

        pdf_buffer = io.BytesIO()
        if len(frames) == 1:
            frames[0].save(pdf_buffer, format="PDF", resolution=150.0)
        else:
            frames[0].save(
                pdf_buffer,
                format="PDF",
                save_all=True,
                append_images=frames[1:],
                resolution=150.0
            )

        return pdf_buffer.getvalue()


def merge_files(
    items,
    output_filename="merged_document",
    output_format="PDF",
    add_bookmarks=True,
    render_dpi=150
):
    """
    Merges multiple files (PDFs and Images) in exact user order and outputs
    in the requested target format:
      - 'PDF': Consolidated PDF document (.pdf)
      - 'PNG_ZIP': Archive of high-res individual PNG images (.zip)
      - 'JPEG_ZIP': Archive of compressed JPEG images (.zip)
      - 'TIFF': Multi-page TIFF document (.tiff)
      
    Returns a dict:
      - 'bytes': bytes of the result
      - 'output_filename': full name with proper extension
      - 'mime_type': MIME type string for download button
      - 'total_files': count of input files merged
      - 'total_pages': total synthesized pages
      - 'total_size_bytes': output size in bytes
      - 'file_breakdown': list of per-file page intervals
      - 'format': chosen export format
      - 'pdf_bytes': raw synthesized PDF bytes (for preview or secondary download)
    """
    if not items:
        raise ValueError("At least one file must be provided for joining.")

    writer = PdfWriter()
    file_breakdown = []
    current_page_index = 0

    for idx, item in enumerate(items, start=1):
        raw_source = item.get("bytes")
        filename = item.get("filename", f"Document_{idx}")
        ext = os.path.splitext(filename)[1].lower()

        if not raw_source:
            continue

        # Check if source is image or PDF
        is_pdf = (ext == ".pdf" or raw_source.startswith(b"%PDF"))

        if not is_pdf:
            # Convert image to PDF page(s)
            pdf_bytes = convert_image_to_pdf_bytes(raw_source, filename=filename)
        else:
            pdf_bytes = raw_source

        reader = PdfReader(io.BytesIO(pdf_bytes))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise ValueError(f"File '{filename}' is password-protected and cannot be merged.")

        file_page_count = len(reader.pages)
        if file_page_count == 0:
            continue

        start_page_1based = current_page_index + 1
        first_page_ref = None

        for page in reader.pages:
            added_page = writer.add_page(page)
            if first_page_ref is None:
                first_page_ref = added_page
            current_page_index += 1

        end_page_1based = current_page_index

        if add_bookmarks and first_page_ref is not None:
            clean_title = os.path.splitext(filename)[0].replace("_", " ").title()
            writer.add_outline_item(
                title=f"{idx}. {clean_title}",
                page_number=start_page_1based - 1
            )

        file_breakdown.append({
            "order": idx,
            "filename": filename,
            "file_type": "PDF" if is_pdf else "Image",
            "start_page": start_page_1based,
            "end_page": end_page_1based,
            "pages": file_page_count
        })

    if current_page_index == 0:
        raise ValueError("No valid document or image pages found to join.")

    # Generate the base merged PDF
    merged_pdf_buf = io.BytesIO()
    writer.write(merged_pdf_buf)
    merged_pdf_bytes = merged_pdf_buf.getvalue()

    base_name = os.path.splitext(output_filename)[0]

    # Handle requested export formats
    fmt_normalized = output_format.upper()

    if fmt_normalized == "PDF":
        final_filename = f"{base_name}.pdf"
        return {
            "bytes": merged_pdf_bytes,
            "pdf_bytes": merged_pdf_bytes,
            "output_filename": final_filename,
            "mime_type": "application/pdf",
            "total_files": len(file_breakdown),
            "total_pages": current_page_index,
            "total_size_bytes": len(merged_pdf_bytes),
            "file_breakdown": file_breakdown,
            "format": "PDF"
        }

    # If image export is requested (PNG_ZIP, JPEG_ZIP, TIFF), render pages
    if pdfium is None:
        raise ImportError("pypdfium2 is required for rendering pages to images. Run: pip install pypdfium2")

    doc = pdfium.PdfDocument(merged_pdf_bytes)
    scale = max(1.0, render_dpi / 72.0)
    rendered_images = []

    for p_idx in range(len(doc)):
        page = doc[p_idx]
        pil_image = page.render(scale=scale).to_pil()
        rendered_images.append(pil_image)

    if fmt_normalized in ("PNG_ZIP", "PNG"):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for p_num, img in enumerate(rendered_images, start=1):
                img_buf = io.BytesIO()
                img.save(img_buf, format="PNG")
                zf.writestr(f"{base_name}_page_{p_num:03d}.png", img_buf.getvalue())
        zip_bytes = zip_buf.getvalue()
        final_filename = f"{base_name}_png_pages.zip"
        return {
            "bytes": zip_bytes,
            "pdf_bytes": merged_pdf_bytes,
            "output_filename": final_filename,
            "mime_type": "application/zip",
            "total_files": len(file_breakdown),
            "total_pages": current_page_index,
            "total_size_bytes": len(zip_bytes),
            "file_breakdown": file_breakdown,
            "format": "PNG_ZIP"
        }

    elif fmt_normalized in ("JPEG_ZIP", "JPEG", "JPG"):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for p_num, img in enumerate(rendered_images, start=1):
                img_buf = io.BytesIO()
                rgb_img = img.convert("RGB") if img.mode != "RGB" else img
                rgb_img.save(img_buf, format="JPEG", quality=90)
                zf.writestr(f"{base_name}_page_{p_num:03d}.jpg", img_buf.getvalue())
        zip_bytes = zip_buf.getvalue()
        final_filename = f"{base_name}_jpg_pages.zip"
        return {
            "bytes": zip_bytes,
            "pdf_bytes": merged_pdf_bytes,
            "output_filename": final_filename,
            "mime_type": "application/zip",
            "total_files": len(file_breakdown),
            "total_pages": current_page_index,
            "total_size_bytes": len(zip_bytes),
            "file_breakdown": file_breakdown,
            "format": "JPEG_ZIP"
        }

    elif fmt_normalized == "TIFF":
        tiff_buf = io.BytesIO()
        rgb_frames = [im.convert("RGB") for im in rendered_images]
        if len(rgb_frames) == 1:
            rgb_frames[0].save(tiff_buf, format="TIFF")
        else:
            rgb_frames[0].save(
                tiff_buf,
                format="TIFF",
                save_all=True,
                append_images=rgb_frames[1:]
            )
        tiff_bytes = tiff_buf.getvalue()
        final_filename = f"{base_name}.tiff"
        return {
            "bytes": tiff_bytes,
            "pdf_bytes": merged_pdf_bytes,
            "output_filename": final_filename,
            "mime_type": "image/tiff",
            "total_files": len(file_breakdown),
            "total_pages": current_page_index,
            "total_size_bytes": len(tiff_bytes),
            "file_breakdown": file_breakdown,
            "format": "TIFF"
        }

    else:
        raise ValueError(f"Unsupported output format: {output_format}")


# Backwards compatibility
merge_pdfs = merge_files
