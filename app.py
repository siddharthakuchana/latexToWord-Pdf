import os
import streamlit as st

from converter import (
    convert_latex_to_docx,
    convert_docx_to_pdf
)

from validator import validate_latex
from pdf_splitter import (
    get_pdf_page_count,
    split_pdf_to_single_pages,
    extract_pdf_pages
)


st.set_page_config(
    page_title="LaTeX & PDF Tools Suite",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Document & PDF Processing Suite")
st.markdown("Convert LaTeX documents to DOCX/PDF, split multi-page PDFs into single pages, and extract specific page ranges.")

# SESSION STORAGE INITIALIZATION

if "docx_file" not in st.session_state:
    st.session_state.docx_file = None

if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None


# APP TABS SETUP

tab_latex, tab_pdf_split = st.tabs([
    "📝 LaTeX to Document (DOCX & PDF)",
    "✂️ PDF Page Splitter & Extractor"
])


# ==============================================================================
# TAB 1: LATEX TO DOCUMENT CONVERTER
# ==============================================================================

with tab_latex:
    st.header("LaTeX Converter")

    input_method = st.radio(
        "Choose Input Method",
        ["Paste Text", "Upload File"],
        horizontal=True
    )

    latex_content = ""

    if input_method == "Paste Text":
        latex_content = st.text_area(
            "Paste LaTeX Code",
            height=300,
            placeholder=r"\documentclass{article}" + "\n" + r"\begin{document}" + "\n" + "Hello World!" + "\n" + r"\end{document}"
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload .tex File",
            type=["tex"],
            key="tex_uploader"
        )
        if uploaded_file:
            latex_content = uploaded_file.read().decode("utf-8")

    # PREVIEW & VALIDATION

    if latex_content:
        st.subheader("LaTeX Preview & Validation")

        with st.expander("Show LaTeX Code Preview", expanded=False):
            st.code(latex_content, language="latex")

        errors = validate_latex(latex_content)

        if errors:
            st.error("Validation Errors Found:")
            for error in errors:
                st.write("•", error)
        else:
            st.success("No Validation Syntax Errors Found")

    # DOCX GENERATION

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Generate DOCX", type="primary", use_container_width=True):
            if not latex_content.strip():
                st.warning("Please enter or upload LaTeX content first.")
            else:
                try:
                    with st.spinner("Converting LaTeX to DOCX..."):
                        docx_file = convert_latex_to_docx(latex_content)
                        st.session_state.docx_file = docx_file
                        st.session_state.pdf_file = None  # Reset PDF state on new DOCX
                    st.success("DOCX Generated Successfully!")
                except Exception as e:
                    st.error(f"Conversion Failed: {e}")

    # DOCX DOWNLOAD & PDF CONVERSION

    if st.session_state.docx_file and os.path.exists(st.session_state.docx_file):
        st.markdown("---")
        st.subheader("1. Download DOCX Document")

        with open(st.session_state.docx_file, "rb") as f:
            st.download_button(
                "⬇️ Download DOCX File",
                data=f.read(),
                file_name="converted.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

        st.subheader("2. Optional PDF Export")

        if st.button("📄 Convert DOCX to PDF", use_container_width=True):
            try:
                with st.spinner("Converting DOCX to PDF..."):
                    pdf_file = convert_docx_to_pdf(st.session_state.docx_file)
                    st.session_state.pdf_file = pdf_file
                st.success("PDF Generated Successfully!")
            except Exception as e:
                st.error(f"PDF Conversion Failed: {e}")

    # PDF DOWNLOAD & PDF SPLITTING FOR GENERATED PDF

    if st.session_state.pdf_file and os.path.exists(st.session_state.pdf_file):
        st.markdown("---")
        st.subheader("3. PDF File & Page Management")

        with open(st.session_state.pdf_file, "rb") as f:
            pdf_bytes = f.read()

        total_pages = get_pdf_page_count(pdf_bytes)

        st.info(f"📊 PDF Page Count: **{total_pages} page(s)**")

        st.download_button(
            "⬇️ Download Full PDF Document",
            data=pdf_bytes,
            file_name="converted.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        if total_pages > 0:
            st.markdown("#### Split or Extract Pages from Generated PDF")
            action_gen = st.radio(
                "Select PDF Tool for Generated PDF:",
                ["None", "Split into Single Pages", "Extract Page Range"],
                key="gen_pdf_action",
                horizontal=True
            )

            if action_gen == "Split into Single Pages":
                split_res = split_pdf_to_single_pages(pdf_bytes, base_filename="latex_converted")
                st.success(f"Split {total_pages} page(s) into individual PDFs.")

                st.download_button(
                    label=f"📦 Download All {total_pages} Pages (ZIP)",
                    data=split_res["zip_bytes"],
                    file_name=split_res["zip_filename"],
                    mime="application/zip",
                    use_container_width=True
                )

                with st.expander("Download Single Pages Individually"):
                    for item in split_res["single_pages"]:
                        st.download_button(
                            label=f"📄 Download Page {item['page_number']}",
                            data=item["bytes"],
                            file_name=item["filename"],
                            mime="application/pdf"
                        )

            elif action_gen == "Extract Page Range":
                col_sp, col_ep = st.columns(2)
                with col_sp:
                    start_p = st.number_input("From Page", min_value=1, max_value=total_pages, value=1, key="gen_sp")
                with col_ep:
                    end_p = st.number_input("To Page", min_value=1, max_value=total_pages, value=total_pages, key="gen_ep")

                if start_p > end_p:
                    st.error("'From Page' cannot be greater than 'To Page'.")
                else:
                    ext_res = extract_pdf_pages(pdf_bytes, start_p, end_p, base_filename="latex_converted")
                    st.write(f"Extracting {ext_res['total_extracted']} page(s): Page {start_p} to Page {end_p}")

                    st.download_button(
                        label=f"⬇️ Download Extracted PDF (Pages {start_p}-{end_p})",
                        data=ext_res["pdf_bytes"],
                        file_name=ext_res["filename"],
                        mime="application/pdf",
                        use_container_width=True
                    )


# ==============================================================================
# TAB 2: PDF PAGE SPLITTER & EXTRACTOR (DIRECT PDF UPLOAD)
# ==============================================================================

with tab_pdf_split:
    st.header("✂️ PDF Page Splitter & Page Range Extractor")
    st.markdown("Upload any multi-page PDF document to divide it into single-page PDFs or extract a specific range of pages (from page X to page Y).")

    uploaded_pdf = st.file_uploader(
        "Upload PDF Document",
        type=["pdf"],
        key="direct_pdf_uploader"
    )

    if uploaded_pdf is not None:
        pdf_bytes = uploaded_pdf.read()
        pdf_name = os.path.splitext(uploaded_pdf.name)[0]

        try:
            total_pages = get_pdf_page_count(pdf_bytes)

            st.markdown("---")
            m1, m2 = st.columns(2)
            m1.metric("Uploaded File", uploaded_pdf.name)
            m2.metric("Total Page Count", f"{total_pages} pages")

            st.markdown("---")

            operation = st.radio(
                "Choose PDF Action:",
                ["Divide PDF into Single Pages", "Extract Specific Page Range (From Page X to Y)"],
                horizontal=True
            )

            # OPERATION 1: DIVIDE INTO SINGLE PAGES

            if operation == "Divide PDF into Single Pages":
                st.subheader("1. Single Page Splitter")
                st.write(f"This will split the **{total_pages}-page** PDF into **{total_pages} separate single-page PDF files**.")

                if st.button("✂️ Split PDF into Single Pages", type="primary", use_container_width=True):
                    with st.spinner("Splitting PDF pages..."):
                        split_res = split_pdf_to_single_pages(pdf_bytes, base_filename=pdf_name)

                    st.success(f"Successfully divided into {total_pages} single-page PDFs!")

                    st.download_button(
                        label=f"📦 Download All Single Pages as ZIP ({split_res['zip_filename']})",
                        data=split_res["zip_bytes"],
                        file_name=split_res["zip_filename"],
                        mime="application/zip",
                        use_container_width=True
                    )

                    st.markdown("##### Download Individual Pages")
                    page_cols = st.columns(min(3, total_pages))
                    for idx, page_info in enumerate(split_res["single_pages"]):
                        col_target = page_cols[idx % len(page_cols)]
                        with col_target:
                            st.download_button(
                                label=f"📄 Page {page_info['page_number']}",
                                data=page_info["bytes"],
                                file_name=page_info["filename"],
                                mime="application/pdf",
                                use_container_width=True,
                                key=f"btn_page_{page_info['page_number']}"
                            )

            # OPERATION 2: EXTRACT SPECIFIC PAGE RANGE

            elif operation == "Extract Specific Page Range (From Page X to Y)":
                st.subheader("2. Page Range Extractor")
                st.write("Specify page range boundaries to extract into a single continuous PDF document.")

                col_from, col_to = st.columns(2)
                with col_from:
                    from_page = st.number_input(
                        "From Page (Start)",
                        min_value=1,
                        max_value=total_pages,
                        value=1,
                        step=1,
                        help="First page to include in extraction"
                    )

                with col_to:
                    to_page = st.number_input(
                        "To Page (End)",
                        min_value=1,
                        max_value=total_pages,
                        value=total_pages,
                        step=1,
                        help="Last page to include in extraction"
                    )

                if from_page > to_page:
                    st.error("⚠️ Invalid range: 'From Page' must be less than or equal to 'To Page'.")
                else:
                    selected_count = to_page - from_page + 1
                    st.info(f"Extracting **{selected_count} page(s)** (Page {from_page} through Page {to_page} out of {total_pages} total pages).")

                    if st.button(f"✂️ Extract Pages {from_page} to {to_page}", type="primary", use_container_width=True):
                        with st.spinner(f"Extracting pages {from_page} to {to_page}..."):
                            ext_res = extract_pdf_pages(
                                pdf_bytes,
                                start_page=from_page,
                                end_page=to_page,
                                base_filename=pdf_name
                            )

                        st.success(f"Successfully extracted {selected_count} page(s)!")

                        st.download_button(
                            label=f"⬇️ Download Extracted PDF ({ext_res['filename']})",
                            data=ext_res["pdf_bytes"],
                            file_name=ext_res["filename"],
                            mime="application/pdf",
                            use_container_width=True
                        )

        except Exception as e:
            st.error(f"Failed to process PDF: {e}")