import pypandoc
import tempfile
import os
from docx2pdf import convert


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

    pypandoc.convert_file(
        tex_file,
        "docx",
        outputfile=docx_file
    )

    return docx_file


def convert_docx_to_pdf(docx_file):

    pdf_file = docx_file.replace(
        ".docx",
        ".pdf"
    )

    convert(
        docx_file,
        pdf_file
    )

    return pdf_file