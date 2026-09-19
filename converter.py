import tempfile
import os



def convert_latex_to_docx(content):

    temp_dir = tempfile.mkdtemp()

    tex_file = os.path.join(
        temp_dir,
        "document.tex"
    )

    with open(
        tex_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(content)

    docx_file = os.path.join(
        temp_dir,
        "document.docx"
    )

    try:
        import pypandoc
    except ImportError:
        raise ImportError("pypandoc is required for LaTeX conversion. Please run: pip install pypandoc")

    pypandoc.convert_file(
        tex_file,
        "docx",
        outputfile=docx_file
    )

    return docx_file


def convert_docx_to_pdf(docx_file):
    try:
        from docx2pdf import convert
    except ImportError:
        raise ImportError("docx2pdf is required for DOCX to PDF conversion. Please run: pip install docx2pdf")

    pdf_file = docx_file.replace(
        ".docx",
        ".pdf"
    )

    convert(
        docx_file,
        pdf_file
    )

    return pdf_file