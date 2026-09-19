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
from compressor import (
    compress_file,
    format_size
)



st.set_page_config(
    page_title="Document, PDF & Compression Suite",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Document, PDF & Compression Suite")
st.markdown("Convert LaTeX documents to DOCX/PDF, split & extract PDF pages, and compress PDFs, images, or documents to any target file size or quality.")

# SESSION STORAGE INITIALIZATION

if "docx_file" not in st.session_state:
    st.session_state.docx_file = None

if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None

if "compression_result" not in st.session_state:
    st.session_state.compression_result = None

# APP TABS SETUP

tab_latex, tab_pdf_split, tab_compress = st.tabs([
    "📝 LaTeX to Document (DOCX & PDF)",
    "✂️ PDF Page Splitter & Extractor",
    "🗜️ Universal File Compressor"
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


# ==============================================================================
# TAB 3: UNIVERSAL FILE COMPRESSOR
# ==============================================================================

with tab_compress:
    st.header("🗜️ Universal File Compressor")
    st.markdown(
        "Compress **PDFs, Images (JPEG, PNG, WEBP, TIFF, BMP)**, or documents to any target file size or quality level using interactive sliders and range boxes."
    )

    uploaded_comp_file = st.file_uploader(
        "Upload File to Compress (PDF, Image, Document)",
        key="universal_compressor_uploader"
    )

    if uploaded_comp_file is not None:
        file_bytes = uploaded_comp_file.read()
        file_name = uploaded_comp_file.name
        orig_size_bytes = len(file_bytes)
        orig_size_kb = max(1.0, orig_size_bytes / 1024.0)
        orig_size_mb = orig_size_kb / 1024.0

        # File Overview Cards
        st.markdown("---")
        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.metric("📁 Selected File", file_name)
        with info_col2:
            st.metric("📦 Original Size", format_size(orig_size_bytes))
        with info_col3:
            file_ext = os.path.splitext(file_name)[1].upper().lstrip(".")
            st.metric("🏷️ Detected Format", file_ext if file_ext else "UNKNOWN")

        st.markdown("---")
        st.subheader("⚙️ Compression Settings & Controls")

        mode = st.radio(
            "Select Compression Mode:",
            ["Target Quality (%)", "Target File Size (KB / MB)"],
            horizontal=True,
            key="comp_mode_selector"
        )

        target_quality = 65
        target_size_kb_arg = None

        if mode == "Target Quality (%)":
            st.markdown("##### Adjust Compression Quality (Slider & Numeric Box)")
            st.caption("Lower quality achieves maximum compression; higher quality preserves fine detail.")

            # Quick presets
            preset_cols = st.columns(4)
            with preset_cols[0]:
                if st.button("🔥 Extreme (20%)", use_container_width=True):
                    st.session_state["quality_slider_val"] = 20
                    st.session_state["quality_box_val"] = 20
            with preset_cols[1]:
                if st.button("⚖️ Balanced (60%)", use_container_width=True):
                    st.session_state["quality_slider_val"] = 60
                    st.session_state["quality_box_val"] = 60
            with preset_cols[2]:
                if st.button("✨ High Quality (85%)", use_container_width=True):
                    st.session_state["quality_slider_val"] = 85
                    st.session_state["quality_box_val"] = 85
            with preset_cols[3]:
                if st.button("🔄 Reset (65%)", use_container_width=True):
                    st.session_state["quality_slider_val"] = 65
                    st.session_state["quality_box_val"] = 65

            if "quality_slider_val" not in st.session_state:
                st.session_state["quality_slider_val"] = 65
            if "quality_box_val" not in st.session_state:
                st.session_state["quality_box_val"] = st.session_state["quality_slider_val"]

            def on_slider_change():
                st.session_state["quality_box_val"] = st.session_state["quality_slider_val"]

            def on_box_change():
                st.session_state["quality_slider_val"] = st.session_state["quality_box_val"]

            col_slider, col_box = st.columns([3, 1])
            with col_slider:
                st.slider(
                    "Quality Range Slider",
                    min_value=5,
                    max_value=95,
                    step=1,
                    key="quality_slider_val",
                    on_change=on_slider_change,
                    help="Slide to adjust compression quality percentage"
                )
            with col_box:
                st.number_input(
                    "Quality Value (%)",
                    min_value=5,
                    max_value=95,
                    step=1,
                    key="quality_box_val",
                    on_change=on_box_change,
                    help="Type exact quality number"
                )

            target_quality = st.session_state["quality_slider_val"]

        else:
            # Mode: Target File Size
            st.markdown("##### Set Desired Target File Size (Slider & Range Box)")
            st.caption("The engine will optimize stream and image encoding to achieve or beat your target file size.")

            unit_col, _ = st.columns([1, 3])
            with unit_col:
                size_unit = st.radio("Size Unit", ["KB", "MB"], horizontal=True, key="size_unit_choice")

            max_limit = orig_size_mb if size_unit == "MB" else orig_size_kb
            min_limit = max(0.01, max_limit * 0.02)
            default_val = max(min_limit, min(max_limit * 0.5, max_limit - 0.01))

            target_slider_key = f"target_size_slider_{size_unit}"
            target_box_key = f"target_size_box_{size_unit}"

            if target_slider_key not in st.session_state:
                st.session_state[target_slider_key] = round(default_val, 2 if size_unit == "MB" else 0)
            if target_box_key not in st.session_state:
                st.session_state[target_box_key] = st.session_state[target_slider_key]

            def on_target_slider_change():
                st.session_state[target_box_key] = st.session_state[target_slider_key]

            def on_target_box_change():
                st.session_state[target_slider_key] = st.session_state[target_box_key]

            col_t_slider, col_t_box = st.columns([3, 1])
            with col_t_slider:
                step_val = 0.05 if size_unit == "MB" else 5.0
                st.slider(
                    f"Target Size Range Slider ({size_unit})",
                    min_value=float(round(min_limit, 2)),
                    max_value=float(round(max_limit, 2)),
                    step=float(step_val),
                    key=target_slider_key,
                    on_change=on_target_slider_change,
                    help=f"Select target file size between {min_limit:.2f} {size_unit} and {max_limit:.2f} {size_unit}"
                )
            with col_t_box:
                st.number_input(
                    f"Target Size Box ({size_unit})",
                    min_value=float(round(min_limit, 2)),
                    max_value=float(round(max_limit, 2)),
                    step=float(step_val),
                    key=target_box_key,
                    on_change=on_target_box_change,
                    help=f"Enter exact target file size in {size_unit}"
                )

            selected_target = st.session_state[target_slider_key]
            if size_unit == "MB":
                target_size_kb_arg = selected_target * 1024.0
            else:
                target_size_kb_arg = selected_target

            target_savings_est = max(0.0, (1.0 - (target_size_kb_arg / orig_size_kb)) * 100.0)
            st.info(f"🎯 Target: **{selected_target:.2f} {size_unit}** (Estimated size reduction: ~**{target_savings_est:.1f}%**)")

        # Optional format conversion for images
        output_format_opt = None
        ext_lower = os.path.splitext(file_name)[1].lower()
        if ext_lower in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]:
            with st.expander("🖼️ Image Format Options (Optional)", expanded=False):
                format_choice = st.selectbox(
                    "Convert Image Format",
                    ["Keep Original Format", "Convert to WebP (Smaller & Modern)", "Convert to JPEG (Broad Compatibility)"],
                    index=0
                )
                if "WebP" in format_choice:
                    output_format_opt = "WEBP"
                elif "JPEG" in format_choice:
                    output_format_opt = "JPEG"

        st.markdown("---")

        if st.button("🗜️ Compress File Now", type="primary", use_container_width=True):
            try:
                with st.spinner("Optimizing and compressing file..."):
                    comp_res = compress_file(
                        file_source=file_bytes,
                        filename=file_name,
                        quality=target_quality,
                        target_size_kb=target_size_kb_arg,
                        output_format=output_format_opt
                    )
                    st.session_state.compression_result = comp_res
                st.success("Compression Completed Successfully!")
            except Exception as e:
                st.error(f"Compression failed: {e}")

        # DISPLAY COMPRESSION RESULTS
        if st.session_state.compression_result is not None:
            res = st.session_state.compression_result
            st.markdown("### 📊 Compression Results")

            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric("Original Size", format_size(res["original_size"]))
            with m_col2:
                st.metric(
                    "Compressed Size",
                    format_size(res["compressed_size"]),
                    delta=f"-{res['saved_percent']:.1f}%",
                    delta_color="inverse"
                )
            with m_col3:
                st.metric("Total Space Saved", f"{format_size(res['saved_bytes'])} ({res['saved_percent']:.1f}%)")

            # Image Before & After Preview
            if res.get("file_type") == "image":
                with st.expander("👁️ Visual Comparison (Original vs Compressed)", expanded=True):
                    prev_c1, prev_c2 = st.columns(2)
                    with prev_c1:
                        st.markdown("**Original Image**")
                        st.image(file_bytes, use_container_width=True)
                    with prev_c2:
                        st.markdown("**Compressed Image**")
                        st.image(res["bytes"], use_container_width=True)

            # Details
            details = res.get("details", {})
            if res.get("file_type") == "pdf":
                st.caption(f"PDF Pages: {details.get('pages', 1)} | Embedded Images Re-encoded: {details.get('images_compressed', 0)}")
            elif res.get("file_type") == "image":
                dims_orig = details.get("dimensions_original", ("", ""))
                dims_comp = details.get("dimensions_compressed", ("", ""))
                st.caption(f"Original Dimensions: {dims_orig[0]}x{dims_orig[1]} px | Output Dimensions: {dims_comp[0]}x{dims_comp[1]} px | Quality: {details.get('quality_used', 'N/A')}")

            # DOWNLOAD BUTTON
            st.download_button(
                label=f"⬇️ Download Compressed File ({res['output_filename']} - {format_size(res['compressed_size'])})",
                data=res["bytes"],
                file_name=res["output_filename"],
                mime=res["mime_type"],
                type="primary",
                use_container_width=True
            )