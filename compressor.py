import io
import os
import zipfile
from PIL import Image, ImageOps
import pypdf


IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif", ".gif", ".ico"
}


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable string (B, KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def _read_bytes(source) -> bytes:
    """Safely extract bytes from bytes, bytearray, or file-like object."""
    if isinstance(source, (bytes, bytearray)):
        return bytes(source)
    elif hasattr(source, "read"):
        b = source.read()
        if hasattr(source, "seek"):
            source.seek(0)
        return b
    elif isinstance(source, str) and os.path.exists(source):
        with open(source, "rb") as f:
            return f.read()
    raise ValueError("Invalid source provided to _read_bytes.")


def _save_image_to_bytes(img: Image.Image, fmt: str, quality: int) -> bytes:
    """Save a PIL image to bytes with specified format and quality settings."""
    out_buf = io.BytesIO()
    fmt_upper = fmt.upper()

    if fmt_upper in ["JPEG", "JPG"]:
        # JPEG requires RGB mode
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            if "A" in img.mode:
                bg.paste(img, mask=img.split()[-1])
            else:
                bg.paste(img)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        img.save(out_buf, format="JPEG", quality=quality, optimize=True, progressive=True)

    elif fmt_upper == "WEBP":
        img.save(out_buf, format="WEBP", quality=quality, method=6)

    elif fmt_upper == "PNG":
        # PNG is lossless, but quality can drive palette color quantization
        if quality < 90:
            colors = max(16, min(256, int(256 * (quality / 100))))
            quantized = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
            quantized.save(out_buf, format="PNG", optimize=True, compress_level=9)
        else:
            img.save(out_buf, format="PNG", optimize=True, compress_level=9)

    elif fmt_upper in ["TIFF", "TIF"]:
        img.save(out_buf, format="TIFF", compression="tiff_lzw")

    else:
        # Generic fallback format
        img.save(out_buf, format=fmt, optimize=True)

    return out_buf.getvalue()


def compress_image(
    image_source,
    quality: int = 75,
    target_size_kb: float = None,
    output_format: str = None
) -> dict:
    """
    Compress an image using Pillow.
    Supports quality % mode or target file size (KB) mode with iterative optimization.
    """
    raw_bytes = _read_bytes(image_source)
    orig_size = len(raw_bytes)

    with Image.open(io.BytesIO(raw_bytes)) as pil_img:
        pil_img = ImageOps.exif_transpose(pil_img)
        orig_w, orig_h = pil_img.size
        detected_format = pil_img.format or "JPEG"

        target_format = (output_format or detected_format).upper()
        if target_format == "JPG":
            target_format = "JPEG"

        if target_size_kb is not None and target_size_kb > 0:
            target_bytes = int(target_size_kb * 1024)

            # Iterative search across downscale factors and quality levels
            best_data = None
            best_quality = quality
            best_dimensions = (orig_w, orig_h)

            scale_candidates = [1.0, 0.9, 0.75, 0.6, 0.45, 0.3, 0.2]
            for scale in scale_candidates:
                new_w = max(16, int(orig_w * scale))
                new_h = max(16, int(orig_h * scale))
                candidate_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS) if scale < 1.0 else pil_img

                low_q = 5
                high_q = 95
                scale_best = None
                scale_best_q = 50

                while low_q <= high_q:
                    mid_q = (low_q + high_q) // 2
                    comp_data = _save_image_to_bytes(candidate_img, target_format, mid_q)
                    sz = len(comp_data)

                    if sz <= target_bytes:
                        scale_best = comp_data
                        scale_best_q = mid_q
                        # Try to find a higher quality that still stays under target
                        low_q = mid_q + 1
                    else:
                        high_q = mid_q - 1

                if scale_best is not None:
                    best_data = scale_best
                    best_quality = scale_best_q
                    best_dimensions = (new_w, new_h)
                    break
                else:
                    # If we couldn't get below target, keep the smallest so far
                    lowest_q_data = _save_image_to_bytes(candidate_img, target_format, 5)
                    if best_data is None or len(lowest_q_data) < len(best_data):
                        best_data = lowest_q_data
                        best_quality = 5
                        best_dimensions = (new_w, new_h)

            result_bytes = best_data
            final_quality = best_quality
            final_w, final_h = best_dimensions

        else:
            # Quality % mode
            # If user selected very low quality, apply slight downsampling for greater size savings
            scale = 1.0
            if quality < 30:
                scale = 0.7
            elif quality < 15:
                scale = 0.5

            if scale < 1.0:
                final_w = max(16, int(orig_w * scale))
                final_h = max(16, int(orig_h * scale))
                working_img = pil_img.resize((final_w, final_h), Image.Resampling.LANCZOS)
            else:
                final_w, final_h = orig_w, orig_h
                working_img = pil_img

            result_bytes = _save_image_to_bytes(working_img, target_format, quality)
            final_quality = quality

    comp_size = len(result_bytes)
    saved_bytes = max(0, orig_size - comp_size)
    saved_percent = (saved_bytes / orig_size * 100.0) if orig_size > 0 else 0.0

    return {
        "bytes": result_bytes,
        "original_size": orig_size,
        "compressed_size": comp_size,
        "saved_bytes": saved_bytes,
        "saved_percent": saved_percent,
        "format": target_format,
        "dimensions_original": (orig_w, orig_h),
        "dimensions_compressed": (final_w, final_h),
        "quality_used": final_quality
    }


def _compress_pdf_pass(pdf_bytes: bytes, quality: int, scale: float = 1.0) -> tuple[bytes, int]:
    """Execute a single compression pass on a PDF file, recompressing images and streams."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    writer = pypdf.PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    images_count = 0
    for page in writer.pages:
        try:
            for img_obj in page.images:
                images_count += 1
                try:
                    pil_img = img_obj.image
                    if scale < 1.0:
                        nw = max(16, int(pil_img.width * scale))
                        nh = max(16, int(pil_img.height * scale))
                        new_img = pil_img.resize((nw, nh), Image.Resampling.LANCZOS)
                    else:
                        new_img = pil_img

                    # Replace with re-compressed image
                    img_obj.replace(new_img, quality=max(5, min(95, quality)))
                except Exception:
                    # Ignore individual unprocessable images
                    pass
        except Exception:
            pass

        try:
            page.compress_content_streams()
        except Exception:
            pass

    try:
        writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    except Exception:
        pass

    out_buf = io.BytesIO()
    writer.write(out_buf)
    return out_buf.getvalue(), images_count


def compress_pdf(
    pdf_source,
    quality: int = 75,
    target_size_kb: float = None
) -> dict:
    """
    Compress a PDF document using pypdf and Pillow image recompression.
    Supports quality % mode and target file size (KB) mode with iterative adjustments.
    """
    raw_bytes = _read_bytes(pdf_source)
    orig_size = len(raw_bytes)

    reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
    total_pages = len(reader.pages)

    if target_size_kb is not None and target_size_kb > 0:
        target_bytes = int(target_size_kb * 1024)

        best_bytes = None
        images_processed = 0

        # Iteratively try combinations of image quality and resolution scaling
        candidates = [
            (85, 1.0),
            (60, 0.9),
            (40, 0.75),
            (25, 0.6),
            (15, 0.4),
            (10, 0.3)
        ]

        for q, s in candidates:
            res_bytes, img_count = _compress_pdf_pass(raw_bytes, quality=q, scale=s)
            images_processed = img_count
            sz = len(res_bytes)

            if sz <= target_bytes:
                best_bytes = res_bytes
                break
            if best_bytes is None or sz < len(best_bytes):
                best_bytes = res_bytes

        result_bytes = best_bytes
    else:
        # Quality % mode
        scale = 1.0
        if quality < 35:
            scale = 0.7
        elif quality < 20:
            scale = 0.5

        result_bytes, images_processed = _compress_pdf_pass(raw_bytes, quality=quality, scale=scale)

    comp_size = len(result_bytes)
    saved_bytes = max(0, orig_size - comp_size)
    saved_percent = (saved_bytes / orig_size * 100.0) if orig_size > 0 else 0.0

    return {
        "bytes": result_bytes,
        "original_size": orig_size,
        "compressed_size": comp_size,
        "saved_bytes": saved_bytes,
        "saved_percent": saved_percent,
        "pages": total_pages,
        "images_compressed": images_processed
    }


def compress_generic_file(file_source, filename: str = "file") -> dict:
    """Compress arbitrary files using maximum zip compression."""
    raw_bytes = _read_bytes(file_source)
    orig_size = len(raw_bytes)

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr(filename, raw_bytes)

    result_bytes = zip_buf.getvalue()
    comp_size = len(result_bytes)
    saved_bytes = max(0, orig_size - comp_size)
    saved_percent = (saved_bytes / orig_size * 100.0) if orig_size > 0 else 0.0

    return {
        "bytes": result_bytes,
        "original_size": orig_size,
        "compressed_size": comp_size,
        "saved_bytes": saved_bytes,
        "saved_percent": saved_percent,
        "output_filename": f"{os.path.splitext(filename)[0]}.zip",
        "mime_type": "application/zip"
    }


def compress_file(
    file_source,
    filename: str,
    quality: int = 75,
    target_size_kb: float = None,
    output_format: str = None
) -> dict:
    """
    Unified compression dispatcher. Detects file type and runs appropriate compression engine.
    """
    raw_bytes = _read_bytes(file_source)
    ext = os.path.splitext(filename)[1].lower()
    base_name = os.path.splitext(filename)[0]

    # Check if PDF
    if ext == ".pdf" or raw_bytes.startswith(b"%PDF"):
        res = compress_pdf(raw_bytes, quality=quality, target_size_kb=target_size_kb)
        return {
            "bytes": res["bytes"],
            "original_size": res["original_size"],
            "compressed_size": res["compressed_size"],
            "saved_bytes": res["saved_bytes"],
            "saved_percent": res["saved_percent"],
            "output_filename": f"{base_name}_compressed.pdf",
            "mime_type": "application/pdf",
            "file_type": "pdf",
            "details": res
        }

    # Check if Image
    is_image = ext in IMAGE_EXTENSIONS
    if not is_image:
        try:
            with Image.open(io.BytesIO(raw_bytes)):
                is_image = True
        except Exception:
            is_image = False

    if is_image:
        target_fmt = output_format or ("JPEG" if ext in [".jpg", ".jpeg"] else ext.lstrip(".").upper())
        if not target_fmt:
            target_fmt = "JPEG"

        res = compress_image(
            raw_bytes,
            quality=quality,
            target_size_kb=target_size_kb,
            output_format=target_fmt
        )

        out_ext = ".jpg" if res["format"].lower() == "jpeg" else f".{res['format'].lower()}"
        mime_types = {
            "jpeg": "image/jpeg",
            "jpg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
            "bmp": "image/bmp",
            "tiff": "image/tiff"
        }
        mime = mime_types.get(res["format"].lower(), "application/octet-stream")

        return {
            "bytes": res["bytes"],
            "original_size": res["original_size"],
            "compressed_size": res["compressed_size"],
            "saved_bytes": res["saved_bytes"],
            "saved_percent": res["saved_percent"],
            "output_filename": f"{base_name}_compressed{out_ext}",
            "mime_type": mime,
            "file_type": "image",
            "details": res
        }

    # Generic file fallback
    res = compress_generic_file(raw_bytes, filename=filename)
    return {
        "bytes": res["bytes"],
        "original_size": res["original_size"],
        "compressed_size": res["compressed_size"],
        "saved_bytes": res["saved_bytes"],
        "saved_percent": res["saved_percent"],
        "output_filename": res["output_filename"],
        "mime_type": res["mime_type"],
        "file_type": "generic",
        "details": res
    }
