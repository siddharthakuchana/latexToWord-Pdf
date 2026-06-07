import pypandoc
import tempfile
import os


def convert_latex_to_docx(latex_content):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".tex",
        mode="w",
        encoding="utf-8"
    ) as temp_file:

        temp_file.write(latex_content)

        tex_path = temp_file.name

    output_docx = tex_path.replace(".tex", ".docx")

    pypandoc.convert_file(
        tex_path,
        "docx",
        outputfile=output_docx
    )

    return output_docx