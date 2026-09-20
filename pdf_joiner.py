import io
import os
from pypdf import PdfReader, PdfWriter


def get_pdf_info(pdf_source, filename="Document"):
    """
    Extracts summary information for a single PDF source (bytes, file-like, or path).
    Returns a dictionary:
      - 'filename': str
      - 'page_count': int
      - 'size_bytes': int
      - 'is_encrypted': bool
      - 'valid': bool
      - 'error': str or None
    """
    size_bytes = 0
    try:
        if isinstance(pdf_source, (bytes, bytearray)):
            size_bytes = len(pdf_source)
            reader = PdfReader(io.BytesIO(pdf_source))
        elif hasattr(pdf_source, "read"):
            pdf_bytes = pdf_source.read()
            size_bytes = len(pdf_bytes)
            if hasattr(pdf_source, "seek"):
                pdf_source.seek(0)
            reader = PdfReader(io.BytesIO(pdf_bytes))
        else:
            size_bytes = os.path.getsize(pdf_source)
            reader = PdfReader(pdf_source)

        is_encrypted = reader.is_encrypted
        if is_encrypted:
            # Try empty password decrypt if needed
            try:
                reader.decrypt("")
            except Exception:
                pass

        page_count = len(reader.pages)

        return {
            "filename": filename,
            "page_count": page_count,
            "size_bytes": size_bytes,
            "is_encrypted": is_encrypted,
            "valid": True,
            "error": None
        }
    except Exception as exc:
        return {
            "filename": filename,
            "page_count": 0,
            "size_bytes": size_bytes,
            "is_encrypted": False,
            "valid": False,
            "error": str(exc)
        }


def merge_pdfs(pdf_items, output_filename="merged_document.pdf", add_bookmarks=True):
    """
    Merges multiple PDF inputs in the exact order provided.
    
    Args:
        pdf_items: List of dictionaries or objects containing:
                   - 'bytes': bytes buffer of the PDF file
                   - 'filename': display name for the document
        output_filename: Desired output filename.
        add_bookmarks: If True, adds an outline bookmark for each document pointing
                       to its first page in the merged file.
                       
    Returns a dictionary:
      - 'pdf_bytes': bytes of the resulting merged PDF
      - 'output_filename': final output filename
      - 'total_files': number of files merged
      - 'total_pages': total number of pages in the output
      - 'total_size_bytes': size of the merged PDF in bytes
      - 'file_breakdown': list of dicts with each source file's page ranges:
            [{'filename': str, 'start_page': int, 'end_page': int, 'pages': int}]
    """
    if not pdf_items:
        raise ValueError("At least one PDF file must be provided for joining.")

    writer = PdfWriter()
    file_breakdown = []
    current_page_index = 0  # 0-indexed across writer

    for idx, item in enumerate(pdf_items, start=1):
        raw_source = item.get("bytes")
        if raw_source is None and "source" in item:
            source_obj = item["source"]
            if isinstance(source_obj, (bytes, bytearray)):
                raw_source = source_obj
            elif hasattr(source_obj, "read"):
                raw_source = source_obj.read()
                if hasattr(source_obj, "seek"):
                    source_obj.seek(0)
            elif isinstance(source_obj, str) and os.path.exists(source_obj):
                with open(source_obj, "rb") as f:
                    raw_source = f.read()

        if not raw_source:
            continue

        filename = item.get("filename", f"Document_{idx}.pdf")
        reader = PdfReader(io.BytesIO(raw_source))

        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise ValueError(f"File '{filename}' is password-protected and cannot be joined without decrypting.")

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
            # Clean filename for bookmark title
            bookmark_title = os.path.splitext(filename)[0].replace("_", " ").title()
            writer.add_outline_item(
                title=f"{idx}. {bookmark_title}",
                page_number=start_page_1based - 1
            )

        file_breakdown.append({
            "order": idx,
            "filename": filename,
            "start_page": start_page_1based,
            "end_page": end_page_1based,
            "pages": file_page_count
        })

    if current_page_index == 0:
        raise ValueError("No valid PDF pages were found in the uploaded documents.")

    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    merged_bytes = output_buffer.getvalue()

    if not output_filename.lower().endswith(".pdf"):
        output_filename = f"{output_filename}.pdf"

    return {
        "pdf_bytes": merged_bytes,
        "output_filename": output_filename,
        "total_files": len(file_breakdown),
        "total_pages": current_page_index,
        "total_size_bytes": len(merged_bytes),
        "file_breakdown": file_breakdown
    }
