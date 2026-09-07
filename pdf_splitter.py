import io
import zipfile
from pypdf import PdfReader, PdfWriter


def get_pdf_page_count(pdf_source):
    """
    Returns the total number of pages in a PDF file or bytes buffer.
    """
    if isinstance(pdf_source, (bytes, bytearray)):
        reader = PdfReader(io.BytesIO(pdf_source))
    elif hasattr(pdf_source, "read"):
        # File-like object (e.g. Streamlit UploadedFile)
        pdf_bytes = pdf_source.read()
        if hasattr(pdf_source, "seek"):
            pdf_source.seek(0)
        reader = PdfReader(io.BytesIO(pdf_bytes))
    else:
        # File path string
        reader = PdfReader(pdf_source)

    return len(reader.pages)


def split_pdf_to_single_pages(pdf_source, base_filename="document"):
    """
    Splits a multi-page PDF into individual 1-page PDF files.
    Returns a dict containing:
      - 'page_count': Total pages
      - 'zip_bytes': Zip file bytes containing all single-page PDFs
      - 'zip_filename': Name of the zip file
      - 'single_pages': List of dicts [{'page_number': i, 'filename': str, 'bytes': bytes}]
    """
    if isinstance(pdf_source, (bytes, bytearray)):
        reader = PdfReader(io.BytesIO(pdf_source))
    elif hasattr(pdf_source, "read"):
        pdf_bytes = pdf_source.read()
        if hasattr(pdf_source, "seek"):
            pdf_source.seek(0)
        reader = PdfReader(io.BytesIO(pdf_bytes))
    else:
        reader = PdfReader(pdf_source)

    total_pages = len(reader.pages)
    single_pages = []

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for idx, page in enumerate(reader.pages, start=1):
            writer = PdfWriter()
            writer.add_page(page)

            page_buffer = io.BytesIO()
            writer.write(page_buffer)
            page_bytes = page_buffer.getvalue()

            page_filename = f"{base_filename}_page_{idx}.pdf"

            single_pages.append({
                "page_number": idx,
                "filename": page_filename,
                "bytes": page_bytes
            })

            # Add to zip file
            zip_file.writestr(page_filename, page_bytes)

    zip_buffer.seek(0)

    return {
        "page_count": total_pages,
        "zip_bytes": zip_buffer.getvalue(),
        "zip_filename": f"{base_filename}_single_pages.zip",
        "single_pages": single_pages
    }


def extract_pdf_pages(pdf_source, start_page, end_page, base_filename="document"):
    """
    Extracts a range of pages from start_page to end_page (1-indexed, inclusive).
    Returns a dict containing:
      - 'pdf_bytes': Bytes of extracted PDF
      - 'filename': Output filename
      - 'start_page': Start page
      - 'end_page': End page
      - 'total_extracted': Total pages in extracted PDF
    """
    if isinstance(pdf_source, (bytes, bytearray)):
        reader = PdfReader(io.BytesIO(pdf_source))
    elif hasattr(pdf_source, "read"):
        pdf_bytes = pdf_source.read()
        if hasattr(pdf_source, "seek"):
            pdf_source.seek(0)
        reader = PdfReader(io.BytesIO(pdf_bytes))
    else:
        reader = PdfReader(pdf_source)

    total_pages = len(reader.pages)

    if start_page < 1:
        start_page = 1
    if end_page > total_pages:
        end_page = total_pages
    if start_page > end_page:
        raise ValueError(f"Start page ({start_page}) cannot be greater than end page ({end_page}).")

    writer = PdfWriter()
    for idx in range(start_page - 1, end_page):
        writer.add_page(reader.pages[idx])

    out_buffer = io.BytesIO()
    writer.write(out_buffer)
    out_bytes = out_buffer.getvalue()

    out_filename = f"{base_filename}_pages_{start_page}_to_{end_page}.pdf"

    return {
        "pdf_bytes": out_bytes,
        "filename": out_filename,
        "start_page": start_page,
        "end_page": end_page,
        "total_extracted": (end_page - start_page + 1)
    }
