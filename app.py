import streamlit as st
from converter import convert_latex_to_docx
from validator import validate_latex

st.set_page_config(
    page_title="LaTeX to Word Converter",
    layout="wide"
)

st.title("📄 LaTeX to Word Converter")

method = st.radio(
    "Choose Input Method",
    ["Paste Text", "Upload File"]
)

latex_content = ""

if method == "Paste Text":

    latex_content = st.text_area(
        "Paste LaTeX Code",
        height=350
    )

else:

    uploaded_file = st.file_uploader(
        "Upload .tex file",
        type=["tex"]
    )

    if uploaded_file:

        latex_content = uploaded_file.read().decode(
            "utf-8"
        )

        st.text_area(
            "File Content",
            latex_content,
            height=350
        )

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

        st.error("Validation Errors")

        for error in errors:
            st.write("•", error)

    else:

        st.success(
            "No Validation Errors Found"
        )

if st.button("Convert to DOCX"):

    if not latex_content.strip():

        st.warning(
            "Please enter LaTeX content."
        )

    else:

        try:

            output_file = convert_latex_to_docx(
                latex_content
            )

            st.success(
                "Conversion Successful!"
            )

            with open(
                output_file,
                "rb"
            ) as file:

                st.download_button(
                    label="Download DOCX",
                    data=file,
                    file_name="converted.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        except Exception as e:

            st.error(
                f"Conversion Failed: {e}"
            )