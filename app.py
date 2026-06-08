import streamlit as st

from converter import (
    convert_latex_to_docx,
    convert_docx_to_pdf
)

from validator import validate_latex


st.set_page_config(
    page_title="LaTeX to Document Converter",
    layout="wide"
)

st.title("📄 LaTeX to Document Converter")

# SESSION STORAGE

if "docx_file" not in st.session_state:
    st.session_state.docx_file = None

# INPUT METHOD

input_method = st.radio(
    "Choose Input Method",
    ["Paste Text", "Upload File"]
)

latex_content = ""

# PASTE

if input_method == "Paste Text":

    latex_content = st.text_area(
        "Paste LaTeX Code",
        height=350
    )

# UPLOAD

else:

    uploaded_file = st.file_uploader(
        "Upload .tex File",
        type=["tex"]
    )

    if uploaded_file:

        latex_content = uploaded_file.read().decode(
            "utf-8"
        )

# PREVIEW

if latex_content:

    st.subheader("Preview")

    st.code(
        latex_content,
        language="latex"
    )

    errors = validate_latex(
        latex_content
    )

    if errors:

        st.error(
            "Validation Errors Found"
        )

        for error in errors:

            st.write(
                "•",
                error
            )

    else:

        st.success(
            "No Validation Errors Found"
        )

# DOCX CONVERSION

if st.button("Generate DOCX"):

    if not latex_content.strip():

        st.warning(
            "Please enter LaTeX content."
        )

    else:

        try:

            docx_file = convert_latex_to_docx(
                latex_content
            )

            st.session_state.docx_file = docx_file

            st.success(
                "DOCX Generated Successfully"
            )

        except Exception as e:

            st.error(
                f"Conversion Failed: {e}"
            )

# DOCX DOWNLOAD

if st.session_state.docx_file:

    with open(
        st.session_state.docx_file,
        "rb"
    ) as f:

        st.download_button(
            "⬇ Download DOCX",
            data=f,
            file_name="converted.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    st.markdown("---")

    st.subheader(
        "Need a PDF too?"
    )

    if st.button(
        "Convert DOCX to PDF"
    ):

        try:

            pdf_file = convert_docx_to_pdf(
                st.session_state.docx_file
            )

            st.session_state.pdf_file = pdf_file

            st.success(
                "PDF Generated Successfully"
            )

        except Exception as e:

            st.error(
                f"PDF Conversion Failed: {e}"
            )

# PDF DOWNLOAD

if "pdf_file" in st.session_state:

    with open(
        st.session_state.pdf_file,
        "rb"
    ) as f:

        st.download_button(
            "⬇ Download PDF",
            data=f,
            file_name="converted.pdf",
            mime="application/pdf"
        )