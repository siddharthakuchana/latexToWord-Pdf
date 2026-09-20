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
from pdf_joiner import (
    get_pdf_info,
    merge_pdfs
)


# ==============================================================================
# PAGE CONFIGURATION & METADATA
# ==============================================================================

st.set_page_config(
    page_title="Document, PDF & Compression Suite Pro",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==============================================================================
# ADVANCED CUSTOM CSS & DESIGN SYSTEM
# ==============================================================================

st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Modern Hero Container */
    .hero-banner {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.12) 0%, rgba(124, 58, 237, 0.12) 50%, rgba(236, 72, 153, 0.08) 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 18px;
        padding: 24px 30px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
    }

    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: #ffffff;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 9999px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.35);
    }

    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 8px 0;
        background: linear-gradient(135deg, #1e293b 20%, #4338ca 60%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    @media (prefers-color-scheme: dark) {
        .hero-title {
            background: linear-gradient(135deg, #f8fafc 20%, #a5b4fc 60%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    }

    .hero-desc {
        font-size: 1.02rem;
        color: #64748b;
        margin: 0;
        line-height: 1.5;
    }

    /* Feature Cards Showcase */
    .feature-card {
        border-radius: 14px;
        padding: 16px 18px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(148, 163, 184, 0.2);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .feature-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.15);
    }

    .feature-card.active {
        border-color: #6366f1;
        background: rgba(99, 102, 241, 0.08);
        box-shadow: 0 0 0 1.5px #6366f1;
    }

    .feature-pill-badge {
        font-size: 0.7rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 8px;
        display: inline-block;
        float: right;
    }
    .badge-new {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    .badge-popular {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
    }
    .badge-smart {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
    }
    .badge-convert {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
        color: white;
    }

    /* Queue Item Card */
    .queue-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s ease;
    }
    .queue-card:hover {
        background: rgba(99, 102, 241, 0.05);
        border-color: rgba(99, 102, 241, 0.35);
    }

    .file-index-badge {
        background: #4f46e5;
        color: #ffffff;
        font-weight: 700;
        font-size: 0.82rem;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
    }

    /* Clean Streamlit metric polish */
    div[data-testid="stMetricValue"] {
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================

if "docx_file" not in st.session_state:
    st.session_state.docx_file = None

if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None

if "compression_result" not in st.session_state:
    st.session_state.compression_result = None

# PDF Joiner State
if "joiner_queue" not in st.session_state:
    st.session_state.joiner_queue = []

if "joiner_seen_uids" not in st.session_state:
    st.session_state.joiner_seen_uids = set()

if "joiner_result" not in st.session_state:
    st.session_state.joiner_result = None

# Navigation state
FEATURE_JOINER = "🔗 PDF Joiner & Merger"
FEATURE_SPLITTER = "✂️ PDF Page Splitter & Extractor"
FEATURE_COMPRESSOR = "🗜️ Universal File Compressor"
FEATURE_LATEX = "📝 LaTeX to Document (DOCX & PDF)"

ALL_FEATURES = [
    FEATURE_JOINER,
    FEATURE_SPLITTER,
    FEATURE_COMPRESSOR,
    FEATURE_LATEX
]

if "selected_feature" not in st.session_state:
    st.session_state.selected_feature = FEATURE_JOINER


# ==============================================================================
# SIDEBAR NAVIGATION & TOOL DASHBOARD
# ==============================================================================

with st.sidebar:
    st.markdown("### 🛠️ PDF & Doc Studio Pro")
    st.caption("Select a tool below or use the Feature Hub on the dashboard.")

    # Synchronized feature navigation in sidebar
    chosen_sidebar_feature = st.radio(
        "Active Tool",
        options=ALL_FEATURES,
        index=ALL_FEATURES.index(st.session_state.selected_feature),
        key="sidebar_feature_radio",
        label_visibility="collapsed"
    )

    if chosen_sidebar_feature != st.session_state.selected_feature:
        st.session_state.selected_feature = chosen_sidebar_feature
        st.rerun()

    st.markdown("---")

    # Quick Feature Status
    st.markdown("#### 📊 Current Session Status")
    if st.session_state.selected_feature == FEATURE_JOINER:
        q_count = len(st.session_state.joiner_queue)
        st.info(f"**PDF Joiner Queue**: {q_count} file(s) ready")
    elif st.session_state.selected_feature == FEATURE_SPLITTER:
        st.info("**Splitter Status**: Ready for multi-page PDF")
    elif st.session_state.selected_feature == FEATURE_COMPRESSOR:
        comp_status = "Result Cached" if st.session_state.compression_result else "Idle"
        st.info(f"**Compressor**: {comp_status}")
    elif st.session_state.selected_feature == FEATURE_LATEX:
        docx_status = "Generated" if st.session_state.docx_file else "None"
        st.info(f"**LaTeX DOCX**: {docx_status}")

    st.markdown("---")
    st.markdown("#### 💡 Quick Features Guide")
    st.markdown("""
    - **🔗 PDF Joiner**: Merge multiple PDFs in any custom order with instant table of contents.
    - **✂️ PDF Splitter**: Explode pages into a zip or trim custom page ranges.
    - **🗜️ Compressor**: Shrink PDFs & images to target KB/MB or quality percentage.
    - **📝 LaTeX Suite**: Convert LaTeX text/.tex into Word `.docx` and `.pdf`.
    """)

    st.markdown("---")
    if st.button("🧹 Clear All Session Caches", use_container_width=True):
        st.session_state.docx_file = None
        st.session_state.pdf_file = None
        st.session_state.compression_result = None
        st.session_state.joiner_queue = []
        st.session_state.joiner_seen_uids = set()
        st.session_state.joiner_result = None
        st.success("Session reset!")
        st.rerun()


# ==============================================================================
# TOP HERO HEADER & INTERACTIVE FEATURE HUB
# ==============================================================================

st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">✨ Multi-Tool Document Suite Pro</div>
    <div class="hero-title">Document, PDF & Compression Studio</div>
    <div class="hero-desc">
        A unified powerhouse to <strong>join multi-page PDFs</strong>, <strong>split & extract page ranges</strong>, <strong>compress files to target sizes</strong>, and <strong>convert LaTeX to Word & PDF</strong>.
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# INTERACTIVE FEATURE HUB: VISUAL CARDS
# ------------------------------------------------------------------------------

st.markdown("### 🧭 All Features Hub — Select a Tool")
hub_cols = st.columns(4)

# Feature 1 Card: PDF Joiner
with hub_cols[0]:
    is_active = (st.session_state.selected_feature == FEATURE_JOINER)
    with st.container(border=True):
        st.markdown('**🔗 PDF Joiner** <span class="feature-pill-badge badge-new">NEW</span>', unsafe_allow_html=True)
        st.caption("Combine 2 or more PDFs into a single file with custom order and bookmarks.")
        if st.button(
            "👉 Select Joiner" if not is_active else "✅ Active Tool",
            key="hub_btn_joiner",
            type="primary" if is_active else "secondary",
            use_container_width=True
        ):
            st.session_state.selected_feature = FEATURE_JOINER
            st.rerun()

# Feature 2 Card: PDF Splitter
with hub_cols[1]:
    is_active = (st.session_state.selected_feature == FEATURE_SPLITTER)
    with st.container(border=True):
        st.markdown('**✂️ PDF Splitter** <span class="feature-pill-badge badge-popular">POPULAR</span>', unsafe_allow_html=True)
        st.caption("Divide multi-page PDFs into single pages or extract custom page ranges.")
        if st.button(
            "👉 Select Splitter" if not is_active else "✅ Active Tool",
            key="hub_btn_splitter",
            type="primary" if is_active else "secondary",
            use_container_width=True
        ):
            st.session_state.selected_feature = FEATURE_SPLITTER
            st.rerun()

# Feature 3 Card: Universal Compressor
with hub_cols[2]:
    is_active = (st.session_state.selected_feature == FEATURE_COMPRESSOR)
    with st.container(border=True):
        st.markdown('**🗜️ File Compressor** <span class="feature-pill-badge badge-smart">SMART</span>', unsafe_allow_html=True)
        st.caption("Compress PDFs and images to exact target KB/MB or adjustable quality.")
        if st.button(
            "👉 Select Compressor" if not is_active else "✅ Active Tool",
            key="hub_btn_compressor",
            type="primary" if is_active else "secondary",
            use_container_width=True
        ):
            st.session_state.selected_feature = FEATURE_COMPRESSOR
            st.rerun()

# Feature 4 Card: LaTeX Converter
with hub_cols[3]:
    is_active = (st.session_state.selected_feature == FEATURE_LATEX)
    with st.container(border=True):
        st.markdown('**📝 LaTeX Converter** <span class="feature-pill-badge badge-convert">DOCX/PDF</span>', unsafe_allow_html=True)
        st.caption("Convert LaTeX text and `.tex` files into editable DOCX and clean PDFs.")
        if st.button(
            "👉 Select LaTeX" if not is_active else "✅ Active Tool",
            key="hub_btn_latex",
            type="primary" if is_active else "secondary",
            use_container_width=True
        ):
            st.session_state.selected_feature = FEATURE_LATEX
            st.rerun()

# Segmented control selector
selected_segment = st.segmented_control(
    "Tool Selector",
    options=ALL_FEATURES,
    default=st.session_state.selected_feature,
    selection_mode="single",
    label_visibility="collapsed"
)

if selected_segment and selected_segment != st.session_state.selected_feature:
    st.session_state.selected_feature = selected_segment
    st.rerun()

st.markdown("---")


# ==============================================================================
# FEATURE 1: 🔗 MULTI-PDF JOINER & MERGER [NEW FEATURE]
# ==============================================================================

if st.session_state.selected_feature == FEATURE_JOINER:
    st.header("🔗 Multi-PDF File Joiner & Merger")
    st.markdown(
        "Upload **two or more PDF files**, arrange them in your preferred reading sequence, "
        "and merge them into a single consolidated PDF document with optional interactive bookmarks."
    )

    # File Uploader
    uploaded_join_files = st.file_uploader(
        "Select Multiple PDF Files to Join",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_joiner_uploader",
        help="You can drag & drop or select multiple PDF files at once."
    )

    # Process uploads into the persistent queue
    if uploaded_join_files:
        for f in uploaded_join_files:
            uid = f"{f.name}_{f.size}"
            if uid not in st.session_state.joiner_seen_uids:
                f_bytes = f.getvalue()
                info = get_pdf_info(f_bytes, filename=f.name)
                st.session_state.joiner_queue.append({
                    "uid": uid,
                    "filename": f.name,
                    "bytes": f_bytes,
                    "size_bytes": f.size,
                    "pages": info["page_count"],
                    "valid": info["valid"],
                    "error": info["error"]
                })
                st.session_state.joiner_seen_uids.add(uid)

    queue = st.session_state.joiner_queue

    if not queue:
        st.info("👆 Please upload **2 or more PDF files** above to start joining.")
    else:
        # Overview Metrics
        total_q_files = len(queue)
        total_q_pages = sum(item["pages"] for item in queue if item["valid"])
        total_q_size = sum(item["size_bytes"] for item in queue)

        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        with m_c1:
            st.metric("📁 Files in Queue", f"{total_q_files} PDF{'s' if total_q_files > 1 else ''}")
        with m_c2:
            st.metric("📄 Total Page Count", f"{total_q_pages} pages")
        with m_c3:
            st.metric("📦 Combined Size", format_size(total_q_size))
        with m_c4:
            valid_count = sum(1 for item in queue if item["valid"])
            st.metric("✅ Status", f"{valid_count}/{total_q_files} Valid")

        st.markdown("---")

        # Document Sequence & Reordering Queue
        st.subheader("📋 Document Merge Sequence")
        st.caption("Reorder files using the ⬆️ and ⬇️ buttons so they merge in your exact desired order.")

        # Reorder actions
        for idx, item in enumerate(queue):
            with st.container(border=True):
                col_order, col_info, col_up, col_down, col_del = st.columns([1, 6, 1.2, 1.2, 1.2])

                with col_order:
                    st.markdown(f"### `#{idx + 1}`")

                with col_info:
                    st.markdown(f"**📄 {item['filename']}**")
                    if item["valid"]:
                        st.caption(f"Pages: **{item['pages']}** | Size: **{format_size(item['size_bytes'])}**")
                    else:
                        st.error(f"⚠️ Error: {item['error']}")

                with col_up:
                    if st.button("⬆️ Up", key=f"btn_up_{idx}", disabled=(idx == 0), use_container_width=True):
                        queue[idx], queue[idx - 1] = queue[idx - 1], queue[idx]
                        st.rerun()

                with col_down:
                    if st.button("⬇️ Down", key=f"btn_down_{idx}", disabled=(idx == len(queue) - 1), use_container_width=True):
                        queue[idx], queue[idx + 1] = queue[idx + 1], queue[idx]
                        st.rerun()

                with col_del:
                    if st.button("❌ Remove", key=f"btn_del_{idx}", use_container_width=True):
                        removed = queue.pop(idx)
                        st.session_state.joiner_seen_uids.discard(removed["uid"])
                        st.session_state.joiner_result = None
                        st.rerun()

        # Bulk Queue Operations
        b_col1, b_col2, _ = st.columns([2, 2, 4])
        with b_col1:
            if st.button("🔄 Reverse Order", use_container_width=True):
                queue.reverse()
                st.rerun()
        with b_col2:
            if st.button("🗑️ Clear Entire Queue", use_container_width=True):
                st.session_state.joiner_queue = []
                st.session_state.joiner_seen_uids.clear()
                st.session_state.joiner_result = None
                st.rerun()

        st.markdown("---")

        # Merge Settings
        st.subheader("⚙️ Merge Settings")
        with st.container(border=True):
            set_col1, set_col2 = st.columns(2)
            with set_col1:
                custom_merge_filename = st.text_input(
                    "Output PDF Filename",
                    value="merged_document.pdf",
                    help="Filename for the downloaded combined document."
                )
            with set_col2:
                add_toc_bookmarks = st.checkbox(
                    "📑 Add Document Bookmarks / Table of Contents",
                    value=True,
                    help="Adds outline entries in the PDF viewer so readers can jump directly to each document."
                )

        # Merge Execution Button
        if len(queue) < 2:
            st.warning("⚠️ You need at least **2 PDF files** in the queue to perform a merge.")
        else:
            if st.button("🚀 Merge All PDFs Now", type="primary", use_container_width=True):
                try:
                    with st.spinner(f"Joining {len(queue)} PDF files into '{custom_merge_filename}'..."):
                        merge_res = merge_pdfs(
                            pdf_items=queue,
                            output_filename=custom_merge_filename,
                            add_bookmarks=add_toc_bookmarks
                        )
                        st.session_state.joiner_result = merge_res
                    st.success(f"🎉 Successfully merged {merge_res['total_files']} PDFs into a single {merge_res['total_pages']}-page document!")
                except Exception as e:
                    st.error(f"Merge operation failed: {e}")

        # Display Merge Results & Download
        if st.session_state.joiner_result is not None:
            res = st.session_state.joiner_result
            st.markdown("---")
            st.subheader("🎉 Merged Document Ready")

            with st.container(border=True):
                res_c1, res_c2, res_c3 = st.columns(3)
                with res_c1:
                    st.metric("Total Documents Joined", f"{res['total_files']} files")
                with res_c2:
                    st.metric("Total Combined Pages", f"{res['total_pages']} pages")
                with res_c3:
                    st.metric("Final Output Size", format_size(res["total_size_bytes"]))

                # Page Range Index Table
                with st.expander("📑 View Page Breakdown by Document", expanded=True):
                    for item in res["file_breakdown"]:
                        col_idx_b, col_fname_b, col_range_b = st.columns([1, 6, 3])
                        with col_idx_b:
                            st.write(f"**#{item['order']}**")
                        with col_fname_b:
                            st.write(f"📄 {item['filename']}")
                        with col_range_b:
                            st.write(f"Pages **{item['start_page']}** – **{item['end_page']}** ({item['pages']} pages)")

                st.download_button(
                    label=f"⬇️ Download Merged PDF ({res['output_filename']} - {format_size(res['total_size_bytes'])})",
                    data=res["pdf_bytes"],
                    file_name=res["output_filename"],
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )


# ==============================================================================
# FEATURE 2: ✂️ PDF PAGE SPLITTER & EXTRACTOR
# ==============================================================================

elif st.session_state.selected_feature == FEATURE_SPLITTER:
    st.header("✂️ PDF Page Splitter & Range Extractor")
    st.markdown(
        "Upload any multi-page PDF document to divide it into single-page PDFs or extract a specific range of pages (from page X to page Y)."
    )

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

            with st.container(border=True):
                m1, m2 = st.columns(2)
                m1.metric("📁 Uploaded File", uploaded_pdf.name)
                m2.metric("📄 Total Page Count", f"{total_pages} pages")

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
# FEATURE 3: 🗜️ UNIVERSAL FILE COMPRESSOR
# ==============================================================================

elif st.session_state.selected_feature == FEATURE_COMPRESSOR:
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
        with st.container(border=True):
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

            with st.container(border=True):
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


# ==============================================================================
# FEATURE 4: 📝 LATEX TO DOCUMENT CONVERTER
# ==============================================================================

elif st.session_state.selected_feature == FEATURE_LATEX:
    st.header("📝 LaTeX to Document (DOCX & PDF)")
    st.markdown(
        "Convert LaTeX source code or `.tex` files into editable Microsoft Word (`.docx`) documents and export to publication-ready PDF."
    )

    input_method = st.radio(
        "Choose Input Method",
        ["Paste Text", "Upload File"],
        horizontal=True
    )

    latex_content = ""

    if input_method == "Paste Text":
        latex_content = st.text_area(
            "Paste LaTeX Code",
            height=280,
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
        with st.container(border=True):
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
        with st.container(border=True):
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