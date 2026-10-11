"""
FastAPI Backend Server for OmniDoc Studio Pro.
Exposes all 10 document-processing tools as REST API endpoints.
"""

import io
import os
import base64
import tempfile
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from compressor import compress_file, format_size
from converter import convert_latex_to_docx, convert_docx_to_pdf
from validator import validate_latex
from pdf_splitter import get_pdf_page_count, split_pdf_to_single_pages, extract_pdf_pages
from pdf_joiner import get_file_info, merge_files, get_pdf_info
from pdf_security import (
    encrypt_pdf, decrypt_pdf, watermark_pdf,
    get_pdf_metadata, update_pdf_metadata, strip_pdf_metadata
)
from pdf_organizer import rotate_pdf_pages, reorder_and_delete_pages, add_page_numbers
from pdf_to_images import convert_pdf_to_images
from pdf_comparator import compare_pdfs
from pdf_extractor_ocr import extract_native_text, extract_ocr_text, check_ocr_availability
from pdf_audio import extract_text_for_speech, generate_speech_audio, GTTS_AVAILABLE
from latex_studio import (
    FORMULA_CATALOG, render_latex_equation_image, validate_bibtex_entry, MATPLOTLIB_AVAILABLE
)

app = FastAPI(
    title="OmniDoc Studio Pro API",
    description="10-in-1 Document & PDF Power Suite Backend",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# HEALTH & STATUS
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    ocr_ready, ocr_msg = check_ocr_availability()
    return {
        "status": "ok",
        "tools": 10,
        "gtts_available": GTTS_AVAILABLE,
        "matplotlib_available": MATPLOTLIB_AVAILABLE,
        "ocr_available": ocr_ready,
        "ocr_message": ocr_msg,
    }


@app.get("/api/tools")
async def list_tools():
    """Return metadata for every tool for the frontend Feature Hub."""
    return [
        {"id": "joiner", "icon": "📑", "name": "OmniMerge", "tag": "MULTI-FORMAT", "tagColor": "emerald",
         "desc": "Join PDFs and images (JPG, PNG, WEBP, TIFF) into a unified PDF or image archive."},
        {"id": "splitter", "icon": "✂️", "name": "PageSlicer", "tag": "EXTRACTOR", "tagColor": "sky",
         "desc": "Divide multi-page PDFs into single-page files or extract custom page intervals."},
        {"id": "organizer", "icon": "🔄", "name": "PageForge", "tag": "ORGANIZER", "tagColor": "pink",
         "desc": "Rotate pages, reorder sequences, delete pages, stamp dynamic page numbers."},
        {"id": "security", "icon": "🔐", "name": "GuardPDF", "tag": "SECURITY", "tagColor": "red",
         "desc": "Password encryption, permissions, custom watermarks, and metadata scrubbing."},
        {"id": "raster", "icon": "🖼️", "name": "PixelRender", "tag": "DPI-RASTER", "tagColor": "indigo",
         "desc": "Export PDF pages into crisp PNG, JPEG, WEBP, or TIFF images at custom DPI."},
        {"id": "diff", "icon": "⚖️", "name": "DiffVision", "tag": "PIXEL-DIFF", "tagColor": "cyan",
         "desc": "Compare two PDF versions side-by-side with pixel diff highlights and metrics."},
        {"id": "extractor", "icon": "🔍", "name": "TextScope", "tag": "TEXT / OCR", "tagColor": "emerald",
         "desc": "Extract digital text or run OCR on scanned documents; export Markdown & TXT."},
        {"id": "audio", "icon": "🎧", "name": "AudioDoc", "tag": "VOICE-AI", "tagColor": "violet",
         "desc": "Transform PDFs into spoken audiobooks; listen live or download MP3s."},
        {"id": "compressor", "icon": "🗜️", "name": "OptiCompress", "tag": "OPTIMIZER", "tagColor": "amber",
         "desc": "Compress PDFs & images to exact target KB/MB or quality sliders."},
        {"id": "latex", "icon": "📝", "name": "TeXPublish", "tag": "DOCX / MATH", "tagColor": "purple",
         "desc": "Convert LaTeX to Word & PDF, render math formulas, validate BibTeX."},
    ]


# ---------------------------------------------------------------------------
# TOOL 0: PDF & IMAGE JOINER (OMNIMERGE)
# ---------------------------------------------------------------------------

@app.post("/api/joiner/merge")
async def joiner_merge(
    files: list[UploadFile] = File(...),
    output_filename: str = Form("merged_document"),
    output_format: str = Form("PDF"),
    add_bookmarks: bool = Form(True),
    render_dpi: int = Form(150)
):
    try:
        items = []
        for f in files:
            content = await f.read()
            items.append({
                "filename": f.filename or "file",
                "bytes": content
            })
        result = merge_files(
            items=items,
            output_filename=output_filename,
            output_format=output_format,
            add_bookmarks=add_bookmarks,
            render_dpi=render_dpi
        )
        return StreamingResponse(
            io.BytesIO(result["bytes"]),
            media_type=result["mime_type"],
            headers={"Content-Disposition": f'attachment; filename="{result["output_filename"]}"'}
        )
    except Exception as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------------
# TOOL 1: PDF SPLITTER
# ---------------------------------------------------------------------------

@app.post("/api/splitter/info")
async def splitter_info(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    try:
        pages = get_pdf_page_count(pdf_bytes)
        return {"filename": file.filename, "pages": pages, "size": len(pdf_bytes)}
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/splitter/split")
async def splitter_split(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    base = os.path.splitext(file.filename or "document")[0]
    try:
        res = split_pdf_to_single_pages(pdf_bytes, base_filename=base)
        return StreamingResponse(
            io.BytesIO(res["zip_bytes"]),
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{res["zip_filename"]}"'}
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/splitter/extract")
async def splitter_extract(
    file: UploadFile = File(...),
    start_page: int = Form(1),
    end_page: int = Form(1)
):
    pdf_bytes = await file.read()
    base = os.path.splitext(file.filename or "document")[0]
    try:
        res = extract_pdf_pages(pdf_bytes, start_page, end_page, base_filename=base)
        return StreamingResponse(
            io.BytesIO(res["pdf_bytes"]),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{res["filename"]}"'}
        )
    except Exception as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------------
# TOOL 2: ORGANIZER (ROTATE, REORDER, NUMBERS)
# ---------------------------------------------------------------------------

@app.post("/api/organizer/rotate")
async def organizer_rotate(
    file: UploadFile = File(...),
    angle: int = Form(90),
    target_mode: str = Form("all"),
    custom_pages: str = Form("")
):
    pdf_bytes = await file.read()
    try:
        result = rotate_pdf_pages(pdf_bytes, angle, target_mode=target_mode, custom_pages_str=custom_pages)
        return StreamingResponse(
            io.BytesIO(result),
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="rotated.pdf"'}
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/organizer/reorder")
async def organizer_reorder(
    file: UploadFile = File(...),
    order_str: str = Form(""),
    delete_pages: str = Form(""),
    reverse: bool = Form(False)
):
    pdf_bytes = await file.read()
    try:
        result = reorder_and_delete_pages(pdf_bytes, order_str=order_str, delete_pages_str=delete_pages, reverse_order=reverse)
        return StreamingResponse(
            io.BytesIO(result),
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="reordered.pdf"'}
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/organizer/page-numbers")
async def organizer_page_numbers(
    file: UploadFile = File(...),
    template: str = Form("Page {page} of {total}"),
    position: str = Form("bottom_center"),
    font_size: int = Form(10),
    margin: float = Form(30.0)
):
    pdf_bytes = await file.read()
    try:
        result = add_page_numbers(pdf_bytes, format_template=template, position=position,
                                  font_size=font_size, margin_pts=margin)
        return StreamingResponse(
            io.BytesIO(result),
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="numbered.pdf"'}
        )
    except Exception as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------------
# TOOL 3: SECURITY
# ---------------------------------------------------------------------------

@app.post("/api/security/encrypt")
async def security_encrypt(
    file: UploadFile = File(...),
    user_password: str = Form(...),
    owner_password: str = Form(""),
    allow_printing: bool = Form(True),
    allow_copying: bool = Form(True)
):
    pdf_bytes = await file.read()
    try:
        result = encrypt_pdf(pdf_bytes, user_password,
                             owner_password=owner_password if owner_password else None,
                             allow_printing=allow_printing, allow_copying=allow_copying)
        return StreamingResponse(
            io.BytesIO(result), media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="protected.pdf"'}
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/security/decrypt")
async def security_decrypt(file: UploadFile = File(...), password: str = Form(...)):
    pdf_bytes = await file.read()
    try:
        result = decrypt_pdf(pdf_bytes, password)
        return StreamingResponse(
            io.BytesIO(result), media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="unlocked.pdf"'}
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/security/watermark")
async def security_watermark(
    file: UploadFile = File(...),
    text: str = Form("CONFIDENTIAL"),
    opacity: float = Form(0.25),
    angle: float = Form(45),
    font_size: int = Form(36),
    position: str = Form("center"),
    color: str = Form("gray")
):
    pdf_bytes = await file.read()
    color_map = {
        "gray": (0.5, 0.5, 0.5),
        "red": (0.85, 0.1, 0.1),
        "blue": (0.1, 0.3, 0.85),
        "green": (0.1, 0.6, 0.2),
    }
    rgb = color_map.get(color, (0.5, 0.5, 0.5))
    try:
        result = watermark_pdf(pdf_bytes, text=text, opacity=opacity, angle=angle,
                               font_size=font_size, color_rgb=rgb, position=position)
        return StreamingResponse(
            io.BytesIO(result), media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="watermarked.pdf"'}
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/security/metadata")
async def security_metadata(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    try:
        meta = get_pdf_metadata(pdf_bytes)
        return meta
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/security/strip-metadata")
async def security_strip_metadata(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    try:
        result = strip_pdf_metadata(pdf_bytes)
        return StreamingResponse(
            io.BytesIO(result), media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="sanitized.pdf"'}
        )
    except Exception as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------------
# TOOL 4: RASTERIZER
# ---------------------------------------------------------------------------

@app.post("/api/raster/convert")
async def raster_convert(
    file: UploadFile = File(...),
    dpi: int = Form(150),
    output_format: str = Form("PNG"),
    quality: int = Form(85)
):
    pdf_bytes = await file.read()
    base = os.path.splitext(file.filename or "document")[0]
    try:
        res = convert_pdf_to_images(pdf_bytes, dpi=dpi, output_format=output_format,
                                    jpeg_quality=quality, base_filename=base)
        return StreamingResponse(
            io.BytesIO(res["zip_bytes"]),
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{res["zip_filename"]}"'}
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/raster/preview")
async def raster_preview(
    file: UploadFile = File(...),
    dpi: int = Form(72)
):
    """Return base64 thumbnail previews of each page (max 10 pages)."""
    pdf_bytes = await file.read()
    base = os.path.splitext(file.filename or "document")[0]
    try:
        res = convert_pdf_to_images(pdf_bytes, dpi=dpi, output_format="JPEG",
                                    jpeg_quality=60, base_filename=base)
        previews = []
        for p in res["pages"][:10]:
            b64 = base64.b64encode(p["bytes"]).decode("ascii")
            previews.append({
                "page": p["page_number"],
                "width": p["width"],
                "height": p["height"],
                "data_url": f"data:image/jpeg;base64,{b64}"
            })
        return {"total_pages": res["total_pages"], "previews": previews}
    except Exception as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------------
# TOOL 5: COMPARATOR
# ---------------------------------------------------------------------------

@app.post("/api/diff/compare")
async def diff_compare(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    dpi: int = Form(150),
    threshold: int = Form(25)
):
    bytes_a = await file_a.read()
    bytes_b = await file_b.read()
    try:
        res = compare_pdfs(bytes_a, bytes_b, dpi=dpi, threshold=threshold)
        pages_summary = []
        for p in res["pages"]:
            b64 = base64.b64encode(p["composite_bytes"]).decode("ascii")
            pages_summary.append({
                "page": p["page_number"],
                "similarity": p["similarity_pct"],
                "change": p["change_pct"],
                "changed_pixels": p["changed_pixels"],
                "composite_url": f"data:image/jpeg;base64,{b64}"
            })
        return {
            "pages_a": res["pages_a"],
            "pages_b": res["pages_b"],
            "overall_similarity": res["overall_similarity"],
            "pages": pages_summary
        }
    except Exception as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------------
# TOOL 6: TEXT EXTRACTOR
# ---------------------------------------------------------------------------

@app.post("/api/extractor/extract")
async def extractor_extract(
    file: UploadFile = File(...),
    mode: str = Form("native")
):
    pdf_bytes = await file.read()
    try:
        if mode == "ocr":
            res = extract_ocr_text(pdf_bytes)
        else:
            res = extract_native_text(pdf_bytes)
        # Remove pil images etc, keep only serializable data
        safe_pages = [{k: v for k, v in p.items()} for p in res["pages"]]
        return {
            "mode": res["mode"],
            "total_pages": res["total_pages"],
            "total_words": res["total_words"],
            "total_chars": res["total_chars"],
            "reading_time_mins": res["reading_time_mins"],
            "empty_pages_count": res["empty_pages_count"],
            "markdown": res["markdown"],
            "plain_text": res["plain_text"],
            "pages": safe_pages
        }
    except Exception as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------------
# TOOL 7: AUDIO
# ---------------------------------------------------------------------------

@app.post("/api/audio/generate")
async def audio_generate(
    file: UploadFile = File(...),
    start_page: int = Form(1),
    end_page: int = Form(5),
    accent: str = Form("com"),
    slow: bool = Form(False)
):
    if not GTTS_AVAILABLE:
        raise HTTPException(503, "gTTS library is not available.")
    pdf_bytes = await file.read()
    try:
        text_info = extract_text_for_speech(pdf_bytes, start_page=start_page, end_page=end_page)
        if not text_info["text"]:
            raise HTTPException(400, "No readable text found on the selected pages.")
        audio_res = generate_speech_audio(text_info["text"], lang="en", tld=accent, slow=slow)
        return StreamingResponse(
            io.BytesIO(audio_res["audio_bytes"]),
            media_type="audio/mp3",
            headers={"Content-Disposition": 'attachment; filename="narration.mp3"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------------
# TOOL 8: COMPRESSOR
# ---------------------------------------------------------------------------

@app.post("/api/compressor/compress")
async def compressor_compress(
    file: UploadFile = File(...),
    quality: int = Form(65),
    target_size_kb: Optional[float] = Form(None),
    output_format: Optional[str] = Form(None)
):
    file_bytes = await file.read()
    try:
        res = compress_file(
            file_source=file_bytes,
            filename=file.filename,
            quality=quality,
            target_size_kb=target_size_kb,
            output_format=output_format
        )
        # Return metadata + base64 preview
        preview_b64 = ""
        if res.get("file_type") == "image":
            preview_b64 = base64.b64encode(res["bytes"][:500_000]).decode("ascii")

        return StreamingResponse(
            io.BytesIO(res["bytes"]),
            media_type=res["mime_type"],
            headers={
                "Content-Disposition": f'attachment; filename="{res["output_filename"]}"',
                "X-Original-Size": str(res["original_size"]),
                "X-Compressed-Size": str(res["compressed_size"]),
                "X-Saved-Percent": str(round(res["saved_percent"], 2)),
            }
        )
    except Exception as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------------
# TOOL 9: LATEX
# ---------------------------------------------------------------------------

@app.get("/api/latex/formulas")
async def latex_formulas():
    return FORMULA_CATALOG


@app.post("/api/latex/render-equation")
async def latex_render_equation(
    formula: str = Form(...),
    fontsize: int = Form(26),
    dpi: int = Form(300),
    transparent: bool = Form(True)
):
    if not MATPLOTLIB_AVAILABLE:
        raise HTTPException(503, "matplotlib is not available.")
    try:
        img_bytes = render_latex_equation_image(formula, fontsize=fontsize, dpi=dpi, transparent=transparent)
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/latex/validate-bibtex")
async def latex_validate_bibtex(bibtex: str = Form(...)):
    return validate_bibtex_entry(bibtex)


@app.post("/api/latex/validate")
async def latex_validate(content: str = Form(...)):
    errors = validate_latex(content)
    return {"valid": len(errors) == 0, "errors": errors}


@app.post("/api/latex/convert-latex")
async def latex_convert(
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Form(None),
    target_format: str = Form("docx")
):
    try:
        raw_tex = ""
        if file:
            b = await file.read()
            raw_tex = b.decode("utf-8", errors="ignore")
        elif content:
            raw_tex = content
        else:
            raise HTTPException(400, "Provide either a .tex file or LaTeX source content.")

        docx_path = convert_latex_to_docx(raw_tex)
        if target_format.lower() == "pdf":
            try:
                pdf_path = convert_docx_to_pdf(docx_path)
                with open(pdf_path, "rb") as f:
                    data = f.read()
                return StreamingResponse(
                    io.BytesIO(data),
                    media_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="converted.pdf"'}
                )
            except Exception:
                with open(docx_path, "rb") as f:
                    data = f.read()
                return StreamingResponse(
                    io.BytesIO(data),
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": 'attachment; filename="converted.docx"'}
                )
        else:
            with open(docx_path, "rb") as f:
                data = f.read()
            return StreamingResponse(
                io.BytesIO(data),
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": 'attachment; filename="converted.docx"'}
            )
    except Exception as e:
        raise HTTPException(400, str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

