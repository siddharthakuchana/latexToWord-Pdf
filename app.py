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
    get_file_info,
    merge_files,
    get_pdf_info
)


# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="SK OmniDoc Studio Pro — Document & PDF Power Suite",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==============================================================================
# FEATURE CONSTANTS & STATE MANAGEMENT
# ==============================================================================

FEATURE_JOINER = "📑 Universal File Merger (PDF & Images)"
FEATURE_SPLITTER = "✂️ PDF Page Splitter & Range Slicer"
FEATURE_COMPRESSOR = "🗜️ Smart File Compressor (Size & Quality)"
FEATURE_LATEX = "📝 LaTeX to Document Engine (DOCX & PDF)"

ALL_FEATURES = [
    FEATURE_JOINER,
    FEATURE_SPLITTER,
    FEATURE_COMPRESSOR,
    FEATURE_LATEX
]

# Initialize persistent session state
if "current_tool" not in st.session_state:
    st.session_state.current_tool = FEATURE_JOINER

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

if "uploader_round" not in st.session_state:
    st.session_state.uploader_round = 0


# State synchronization callback for tool switching
def set_active_tool(tool_name):
    """Safely updates active tool in session state so dropdown & cards stay in sync."""
    st.session_state.current_tool = tool_name


# ==============================================================================
# ADVANCED CONSTELLATION / SPACE THEMED CSS
# ==============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Cosmic background elements */
    .stApp {
        background: radial-gradient(ellipse at 50% -20%, #1e1b4b 0%, #090d21 45%, #030712 100%);
        color: #f1f5f9;
    }

    /* Nebula Hero Banner */
    .cosmic-hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.75) 0%, rgba(15, 23, 42, 0.85) 50%, rgba(3, 7, 18, 0.95) 100%);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 20px;
        padding: 26px 32px;
        margin-bottom: 22px;
        box-shadow: 0 0 35px rgba(99, 102, 241, 0.2), inset 0 0 30px rgba(56, 189, 248, 0.05);
        backdrop-filter: blur(14px);
    }

    .stardust-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.4), rgba(168, 85, 247, 0.3));
        border: 1px solid rgba(168, 85, 247, 0.5);
        color: #c084fc;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 4px 14px;
        border-radius: 9999px;
        margin-bottom: 12px;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.3);
    }

    .cosmic-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 8px 0;
        background: linear-gradient(135deg, #ffffff 15%, #c7d2fe 45%, #38bdf8 80%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .cosmic-subtitle {
        font-size: 1.02rem;
        color: #94a3b8;
        line-height: 1.55;
        margin: 0;
    }

    /* Constellation Card Styling */
    .constellation-card {
        border-radius: 16px;
        padding: 16px 18px;
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(99, 102, 241, 0.25);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 10px;
    }

    .constellation-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.6);
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.25);
    }

    .constellation-card.orbiting {
        border: 1.5px solid #38bdf8 !important;
        background: linear-gradient(145deg, rgba(30, 27, 75, 0.8), rgba(15, 23, 42, 0.9)) !important;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.4), inset 0 0 15px rgba(99, 102, 241, 0.3) !important;
    }

    /* Cosmic Chips */
    .cosmic-badge {
        font-size: 0.68rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        float: right;
    }
    .badge-supernova {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.4);
    }
    .badge-comet {
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
    }
    .badge-gravity {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.4);
    }
    .badge-scribe {
        background: rgba(168, 85, 247, 0.2);
        color: #c084fc;
        border: 1px solid rgba(192, 132, 252, 0.4);
    }

    /* Mission Control Dropdown Box */
    .mission-control-box {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 16px;
        padding: 16px 20px;
        margin: 16px 0 24px 0;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.12);
    }

    /* Streamlit Containers Border Theme */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(99, 102, 241, 0.25) !important;
        background: rgba(15, 23, 42, 0.45) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(10px) !important;
    }

    /* Buttons with Celestial Glow */
    button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #0284c7 100%) !important;
        border: 1px solid #38bdf8 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    button[kind="primary"]:hover {
        box-shadow: 0 0 24px rgba(56, 189, 248, 0.6) !important;
        transform: translateY(-1px) !important;
    }

    /* Metric Values */
    div[data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# HERO BANNER
# ==============================================================================

st.markdown("""
<div class="cosmic-hero">
    <div class="stardust-badge">⚡ Professional Document & PDF Suite</div>
    <div class="cosmic-title">OmniDoc Studio Pro</div>
    <div class="cosmic-subtitle">
        A unified, high-performance suite to <strong>join & synthesize multi-format files</strong>, 
        <strong>split & extract PDF page ranges</strong>, <strong>compress documents to exact target sizes</strong>, 
        and <strong>compile LaTeX into Word & PDF</strong>.
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# FEATURE CARDS HUB (VISUAL TOOL SHOWCASE)
# ==============================================================================

st.markdown("### 🧭 Feature Hub — All Available Tools")
st.caption("Click any feature card below or use the Tool Selector dropdown to switch between tools instantly.")

hub_c1, hub_c2, hub_c3, hub_c4 = st.columns(4)

# Tool 1: OmniMerge (PDF & Image Joiner)
with hub_c1:
    is_active_joiner = (st.session_state.current_tool == FEATURE_JOINER)
    card_cls = "constellation-card orbiting" if is_active_joiner else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-supernova">MULTI-FORMAT</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">📑 OmniMerge</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 48px;">
            Join PDFs and images (JPG, PNG, WEBP, TIFF) into a unified PDF or image archive.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button(
        "✅ Active Tool" if is_active_joiner else "👉 Select OmniMerge",
        key="btn_hub_joiner",
        type="primary" if is_active_joiner else "secondary",
        use_container_width=True,
        on_click=set_active_tool,
        args=(FEATURE_JOINER,)
    )

# Tool 2: PageSlicer (PDF Splitter)
with hub_c2:
    is_active_splitter = (st.session_state.current_tool == FEATURE_SPLITTER)
    card_cls = "constellation-card orbiting" if is_active_splitter else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-comet">EXTRACTOR</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">✂️ PageSlicer</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 48px;">
            Divide multi-page PDFs into single-page files (ZIP) or extract custom page intervals.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button(
        "✅ Active Tool" if is_active_splitter else "👉 Select PageSlicer",
        key="btn_hub_splitter",
        type="primary" if is_active_splitter else "secondary",
        use_container_width=True,
        on_click=set_active_tool,
        args=(FEATURE_SPLITTER,)
    )

# Tool 3: OptiCompress (File Compressor)
with hub_c3:
    is_active_comp = (st.session_state.current_tool == FEATURE_COMPRESSOR)
    card_cls = "constellation-card orbiting" if is_active_comp else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-gravity">OPTIMIZER</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">🗜️ OptiCompress</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 48px;">
            Compress PDFs & images down to exact target KB/MB or adjustable quality sliders.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button(
        "✅ Active Tool" if is_active_comp else "👉 Select OptiCompress",
        key="btn_hub_comp",
        type="primary" if is_active_comp else "secondary",
        use_container_width=True,
        on_click=set_active_tool,
        args=(FEATURE_COMPRESSOR,)
    )

# Tool 4: TeXPublish (LaTeX Scribe)
with hub_c4:
    is_active_latex = (st.session_state.current_tool == FEATURE_LATEX)
    card_cls = "constellation-card orbiting" if is_active_latex else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-scribe">DOCX / PDF</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">📝 TeXPublish</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 48px;">
            Convert raw LaTeX code or .tex files into editable Word documents and PDFs.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button(
        "✅ Active Tool" if is_active_latex else "👉 Select TeXPublish",
        key="btn_hub_latex",
        type="primary" if is_active_latex else "secondary",
        use_container_width=True,
        on_click=set_active_tool,
        args=(FEATURE_LATEX,)
    )


# ==============================================================================
# TOOL SELECTOR DROPDOWN
# ==============================================================================

st.markdown("""
<div class="mission-control-box">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
        <span style="font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 8px;">
            🎯 Active Tool Selector Dropdown
        </span>
        <span style="font-size: 0.75rem; color: #94a3b8;">
            Synchronized with Feature Cards
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Clean, single-source-of-truth selectbox dropdown
active_tool_selection = st.selectbox(
    "Select Active Tool:",
    options=ALL_FEATURES,
    key="current_tool",
    label_visibility="collapsed"
)


# ==============================================================================
# SIDEBAR NAVIGATION & CONTROLS
# ==============================================================================

with st.sidebar:
    st.markdown("### 🛠️ SK OmniDoc Studio Pro")
    st.caption("All-in-one Document & PDF Suite")

    st.info(f"**Currently Active**:\n{st.session_state.current_tool}")

    st.markdown("---")
    st.markdown("#### ⚡ Quick Tool Switcher")
    tool_icons = {
        FEATURE_JOINER: "📑 OmniMerge",
        FEATURE_SPLITTER: "✂️ PageSlicer",
        FEATURE_COMPRESSOR: "🗜️ OptiCompress",
        FEATURE_LATEX: "📝 TeXPublish"
    }
    for feat in ALL_FEATURES:
        is_cur = (st.session_state.current_tool == feat)
        display_label = tool_icons.get(feat, feat)
        st.button(
            f"{'👉 ' if is_cur else ''}{display_label}",
            key=f"sidebar_btn_{feat[:10]}",
            type="primary" if is_cur else "secondary",
            use_container_width=True,
            on_click=set_active_tool,
            args=(feat,)
        )

    st.markdown("---")
    st.markdown("#### 📊 Status")
    if st.session_state.current_tool == FEATURE_JOINER:
        st.write(f"📁 Queue: **{len(st.session_state.joiner_queue)} file(s)**")
    elif st.session_state.current_tool == FEATURE_COMPRESSOR:
        status_c = "Cached" if st.session_state.compression_result else "Idle"
        st.write(f"🗜️ Compressor: **{status_c}**")
    elif st.session_state.current_tool == FEATURE_LATEX:
        status_l = "Generated" if st.session_state.docx_file else "Idle"
        st.write(f"📝 DOCX: **{status_l}**")
    else:
        st.write("✂️ Splitter: **Ready**")

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

st.markdown("---")


# ==============================================================================
# MISSION 1: 🌌 MULTI-PDF JOINER & MERGER
# ==============================================================================

if st.session_state.current_tool == FEATURE_JOINER:
    st.header("🌌 Multi-File Joiner & Universal Document Synthesizer")
    st.markdown(
        "Join **PDFs, JPEGs, PNGs, WEBPs, BMPs, or TIFFs** into a unified document or image package. "
        "Upload files individually or in batches, arrange their order, and **choose your preferred extraction format**."
    )

    # --------------------------------------------------------------------------
    # UPLOADER & INCREMENTAL FILE SELECTION
    # --------------------------------------------------------------------------
    with st.container(border=True):
        up_h1, up_h2 = st.columns([3, 1])
        with up_h1:
            st.markdown("#### 📥 Select or Drag Files to Join")
            st.caption("Supports **PDF, JPEG, PNG, WEBP, TIFF, BMP** documents and images.")
        with up_h2:
            if st.button("➕ Add More Files", key="btn_add_more_files_top", use_container_width=True, help="Clear file picker so you can choose additional files to append to queue"):
                st.session_state.uploader_round += 1
                st.rerun()

        uploaded_join_files = st.file_uploader(
            "Select files to join (PDF, Images)",
            type=["pdf", "png", "jpg", "jpeg", "webp", "bmp", "tiff", "tif"],
            accept_multiple_files=True,
            key=f"pdf_joiner_uploader_{st.session_state.uploader_round}",
            label_visibility="collapsed"
        )

    # Process newly uploaded files into persistent queue
    if uploaded_join_files:
        for f in uploaded_join_files:
            uid = f"{f.name}_{f.size}"
            if uid not in st.session_state.joiner_seen_uids:
                f_bytes = f.getvalue()
                info = get_file_info(f_bytes, filename=f.name)
                st.session_state.joiner_queue.append({
                    "uid": uid,
                    "filename": f.name,
                    "bytes": f_bytes,
                    "size_bytes": f.size,
                    "file_type": info["file_type"],
                    "format_label": info["format_label"],
                    "pages": info["page_count"],
                    "dimensions": info.get("dimensions"),
                    "valid": info["valid"],
                    "error": info["error"]
                })
                st.session_state.joiner_seen_uids.add(uid)

    queue = st.session_state.joiner_queue

    if not queue:
        st.info("🛰️ Ready for documents. Upload one or more **PDFs or Images** above to launch the joiner.")
    else:
        # Prompt to add more files easily
        st.success(f"✅ **{len(queue)} file(s) currently in queue.** You can use **➕ Add More Files** above at any time to select and append additional files.")

        total_q_files = len(queue)
        total_q_pages = sum(item["pages"] for item in queue if item["valid"])
        total_q_size = sum(item["size_bytes"] for item in queue)

        # Overview telemetry metrics
        with st.container(border=True):
            m_c1, m_c2, m_c3, m_c4 = st.columns(4)
            with m_c1:
                st.metric("📁 Files in Queue", f"{total_q_files} item(s)")
            with m_c2:
                st.metric("📄 Total Page Mass", f"{total_q_pages} page(s)")
            with m_c3:
                st.metric("📦 Combined Size", format_size(total_q_size))
            with m_c4:
                valid_count = sum(1 for item in queue if item["valid"])
                st.metric("⚡ Inspection Status", f"{valid_count}/{total_q_files} Valid")

        st.markdown("### 📋 Document Merge Sequence")
        st.caption("Arrange files in your exact preferred reading sequence using the orbital ⬆️ Up and ⬇️ Down thrusters.")

        # Interactive document queue cards
        for idx, item in enumerate(queue):
            with st.container(border=True):
                col_ord, col_det, col_up, col_dn, col_rm = st.columns([1, 6, 1.2, 1.2, 1.2])

                with col_ord:
                    st.markdown(f"#### `#{idx + 1}`")

                with col_det:
                    is_pdf_item = (item["file_type"] == "pdf")
                    icon = "📄" if is_pdf_item else "🖼️"
                    st.markdown(f"**{icon} {item['filename']}** `{item.get('format_label', 'FILE')}`")
                    if item["valid"]:
                        if is_pdf_item:
                            st.caption(f"Type: **PDF Document** | Pages: **{item['pages']}** | Size: **{format_size(item['size_bytes'])}**")
                        else:
                            dims = item.get("dimensions")
                            dim_str = f"{dims[0]}x{dims[1]} px" if dims else "Standard"
                            st.caption(f"Type: **{item.get('format_label', 'IMAGE')} Image** | Resolution: **{dim_str}** | Size: **{format_size(item['size_bytes'])}**")
                    else:
                        st.error(f"⚠️ Inspection Error: {item['error']}")

                with col_up:
                    if st.button("⬆️ Up", key=f"btn_up_{idx}", disabled=(idx == 0), use_container_width=True):
                        queue[idx], queue[idx - 1] = queue[idx - 1], queue[idx]
                        st.rerun()

                with col_dn:
                    if st.button("⬇️ Down", key=f"btn_down_{idx}", disabled=(idx == len(queue) - 1), use_container_width=True):
                        queue[idx], queue[idx + 1] = queue[idx + 1], queue[idx]
                        st.rerun()

                with col_rm:
                    if st.button("❌ Remove", key=f"btn_del_{idx}", use_container_width=True):
                        removed = queue.pop(idx)
                        st.session_state.joiner_seen_uids.discard(removed["uid"])
                        st.session_state.joiner_result = None
                        st.rerun()

        # Bulk actions
        ba1, ba2, _ = st.columns([2, 2, 4])
        with ba1:
            if st.button("🔄 Reverse Order", use_container_width=True):
                queue.reverse()
                st.rerun()
        with ba2:
            if st.button("🗑️ Clear Entire Queue", use_container_width=True):
                st.session_state.joiner_queue = []
                st.session_state.joiner_seen_uids.clear()
                st.session_state.joiner_result = None
                st.rerun()

        st.markdown("---")

        # ----------------------------------------------------------------------
        # EXTRACTION & SYNTHESIS SETTINGS
        # ----------------------------------------------------------------------
        st.subheader("⚙️ Extraction & Export Settings")
        with st.container(border=True):
            s1, s2 = st.columns(2)
            with s1:
                export_format_choice = st.selectbox(
                    "🎯 Choose Extraction / Output Format:",
                    options=[
                        "📄 Consolidated PDF Document (.pdf)",
                        "🖼️ High-Res Image Package (.zip of PNGs)",
                        "🖼️ Compressed Image Package (.zip of JPEGs)",
                        "📑 Multi-Page TIFF Document (.tiff)"
                    ],
                    index=0,
                    help="Select which file format you want all joined files extracted or compiled into."
                )

                fmt_code = "PDF"
                if "PNG" in export_format_choice:
                    fmt_code = "PNG_ZIP"
                elif "JPEG" in export_format_choice:
                    fmt_code = "JPEG_ZIP"
                elif "TIFF" in export_format_choice:
                    fmt_code = "TIFF"

                output_base_name = st.text_input(
                    "Base Output Filename",
                    value="synthesized_document",
                    help="Name for the resulting file (extension will be added automatically based on selected format)."
                )

            with s2:
                if fmt_code == "PDF":
                    add_toc_bookmarks = st.checkbox(
                        "📑 Generate Table of Contents (Outline Bookmarks)",
                        value=True,
                        help="Creates bookmarks in the PDF viewer outline for each joined document."
                    )
                    selected_dpi = 150
                else:
                    add_toc_bookmarks = False
                    selected_dpi = st.select_slider(
                        "Image Rendering Resolution (DPI)",
                        options=[100, 150, 200, 300],
                        value=150,
                        help="150 DPI is balanced and fast; 300 DPI produces crystal-clear print quality."
                    )

        # Merge / Extract Action Button
        if len(queue) < 2:
            st.warning("⚠️ At least **2 files** (PDFs or Images) are required in the queue to perform a join.")
        else:
            if st.button("🚀 Join & Extract Files Now", type="primary", use_container_width=True):
                try:
                    with st.spinner(f"Joining {len(queue)} files and compiling into {fmt_code}..."):
                        merge_res = merge_files(
                            items=queue,
                            output_filename=output_base_name,
                            output_format=fmt_code,
                            add_bookmarks=add_toc_bookmarks,
                            render_dpi=selected_dpi
                        )
                        st.session_state.joiner_result = merge_res
                    st.success(f"🎉 Successfully joined {merge_res['total_files']} files ({merge_res['total_pages']} pages) into '{merge_res['output_filename']}'!")
                except Exception as e:
                    st.error(f"Join & extraction failed: {e}")

        # Display Merge Results & Download
        if st.session_state.joiner_result is not None:
            res = st.session_state.joiner_result
            st.markdown("---")
            st.subheader(f"🎉 Synthesized Output Ready ({res['format']})")

            with st.container(border=True):
                r1, r2, r3, r4 = st.columns(4)
                with r1:
                    st.metric("Files Merged", f"{res['total_files']} items")
                with r2:
                    st.metric("Total Synthesized Pages", f"{res['total_pages']} pages")
                with r3:
                    st.metric("Output File Size", format_size(res["total_size_bytes"]))
                with r4:
                    st.metric("Format", res["format"])

                with st.expander("📑 View Document Sequence & Page Breakdown Matrix", expanded=True):
                    for item in res["file_breakdown"]:
                        b_col1, b_col2, b_col3 = st.columns([1, 6, 3])
                        with b_col1:
                            st.write(f"**#{item['order']}**")
                        with b_col2:
                            t_badge = "📄 PDF" if item["file_type"] == "PDF" else "🖼️ Image"
                            st.write(f"{item['filename']} `({t_badge})`")
                        with b_col3:
                            st.write(f"Pages **{item['start_page']}** – **{item['end_page']}** ({item['pages']} page{'s' if item['pages']>1 else ''})")

                # Primary Download Button
                st.download_button(
                    label=f"⬇️ Download {res['output_filename']} ({format_size(res['total_size_bytes'])})",
                    data=res["bytes"],
                    file_name=res["output_filename"],
                    mime=res["mime_type"],
                    type="primary",
                    use_container_width=True
                )

                # Secondary Download Button (if image archive was exported, also offer direct PDF download)
                if res["format"] != "PDF" and "pdf_bytes" in res:
                    st.download_button(
                        label=f"📄 Also Download as Single Consolidated PDF ({format_size(len(res['pdf_bytes']))})",
                        data=res["pdf_bytes"],
                        file_name=f"{os.path.splitext(res['output_filename'])[0]}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )


# ==============================================================================
# TOOL 2: ✂️ PAGESLICER — PDF PAGE SPLITTER & EXTRACTOR
# ==============================================================================

elif st.session_state.current_tool == FEATURE_SPLITTER:
    st.header("✂️ PageSlicer — PDF Page Splitter & Range Extractor")
    st.markdown(
        "Upload any multi-page PDF document to divide it into single-page PDFs or extract a specific page interval."
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
                "Choose Splitting Action:",
                ["Divide PDF into Single Pages", "Extract Specific Page Range (From Page X to Y)"],
                horizontal=True
            )

            if operation == "Divide PDF into Single Pages":
                st.subheader("1. Single Page Splitter")
                st.write(f"This will split the **{total_pages}-page** PDF into **{total_pages} individual single-page PDF documents**.")

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

            elif operation == "Extract Specific Page Range (From Page X to Y)":
                st.subheader("2. Page Range Extractor")
                st.write("Specify orbital start and end boundaries to extract a continuous PDF slice.")

                col_from, col_to = st.columns(2)
                with col_from:
                    from_page = st.number_input(
                        "From Page (Start)",
                        min_value=1,
                        max_value=total_pages,
                        value=1,
                        step=1,
                        help="First page of slice"
                    )

                with col_to:
                    to_page = st.number_input(
                        "To Page (End)",
                        min_value=1,
                        max_value=total_pages,
                        value=total_pages,
                        step=1,
                        help="Last page of slice"
                    )

                if from_page > to_page:
                    st.error("⚠️ Invalid range: 'From Page' must be less than or equal to 'To Page'.")
                else:
                    selected_count = to_page - from_page + 1
                    st.info(f"Extracting **{selected_count} page(s)** (Page {from_page} through Page {to_page} of {total_pages} total).")

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
# TOOL 3: 🗜️ OPTICOMPRESS — UNIVERSAL FILE COMPRESSOR
# ==============================================================================

elif st.session_state.current_tool == FEATURE_COMPRESSOR:
    st.header("🗜️ OptiCompress — Smart File Compressor")
    st.markdown(
        "Compress **PDFs, Images (JPEG, PNG, WEBP, TIFF, BMP)**, or documents to any target file size (KB / MB) or visual quality level."
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
            "Select Compression Strategy:",
            ["Target Quality (%)", "Target File Size (KB / MB)"],
            horizontal=True,
            key="comp_mode_selector"
        )

        target_quality = 65
        target_size_kb_arg = None

        if mode == "Target Quality (%)":
            st.markdown("##### Adjust Compression Quality")
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
            st.markdown("##### Set Desired Target File Size")
            st.caption("The engine optimizes streams and resolutions to match or beat your target file size.")

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
                    on_change=on_target_slider_change
                )
            with col_t_box:
                st.number_input(
                    f"Target Size Box ({size_unit})",
                    min_value=float(round(min_limit, 2)),
                    max_value=float(round(max_limit, 2)),
                    step=float(step_val),
                    key=target_box_key,
                    on_change=on_target_box_change
                )

            selected_target = st.session_state[target_slider_key]
            if size_unit == "MB":
                target_size_kb_arg = selected_target * 1024.0
            else:
                target_size_kb_arg = selected_target

            target_savings_est = max(0.0, (1.0 - (target_size_kb_arg / orig_size_kb)) * 100.0)
            st.info(f"🎯 Target: **{selected_target:.2f} {size_unit}** (Estimated reduction: ~**{target_savings_est:.1f}%**)")

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

        # Display Results
        if st.session_state.compression_result is not None:
            res = st.session_state.compression_result
            st.markdown("### 📊 Compression Results")

            with st.container(border=True):
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric("Original Mass", format_size(res["original_size"]))
                with m_col2:
                    st.metric(
                        "Compressed Mass",
                        format_size(res["compressed_size"]),
                        delta=f"-{res['saved_percent']:.1f}%",
                        delta_color="inverse"
                    )
                with m_col3:
                    st.metric("Total Space Saved", f"{format_size(res['saved_bytes'])} ({res['saved_percent']:.1f}%)")

            if res.get("file_type") == "image":
                with st.expander("👁️ Visual Comparison (Original vs Compressed)", expanded=True):
                    prev_c1, prev_c2 = st.columns(2)
                    with prev_c1:
                        st.markdown("**Original Image**")
                        st.image(file_bytes, use_container_width=True)
                    with prev_c2:
                        st.markdown("**Compressed Image**")
                        st.image(res["bytes"], use_container_width=True)

            details = res.get("details", {})
            if res.get("file_type") == "pdf":
                st.caption(f"PDF Pages: {details.get('pages', 1)} | Embedded Images Re-encoded: {details.get('images_compressed', 0)}")
            elif res.get("file_type") == "image":
                dims_orig = details.get("dimensions_original", ("", ""))
                dims_comp = details.get("dimensions_compressed", ("", ""))
                st.caption(f"Original: {dims_orig[0]}x{dims_orig[1]} px | Output: {dims_comp[0]}x{dims_comp[1]} px | Quality: {details.get('quality_used', 'N/A')}")

            st.download_button(
                label=f"⬇️ Download Compressed File ({res['output_filename']} - {format_size(res['compressed_size'])})",
                data=res["bytes"],
                file_name=res["output_filename"],
                mime=res["mime_type"],
                type="primary",
                use_container_width=True
            )


# ==============================================================================
# TOOL 4: 📝 TEXPUBLISH — LATEX CONVERTER
# ==============================================================================

elif st.session_state.current_tool == FEATURE_LATEX:
    st.header("📝 TeXPublish — LaTeX to Document Converter (DOCX & PDF)")
    st.markdown(
        "Convert LaTeX source code or `.tex` documents into editable Microsoft Word (`.docx`) files and export to publication-ready PDF."
    )

    input_method = st.radio(
        "Choose Input Method:",
        ["Paste Text", "Upload File"],
        horizontal=True
    )

    latex_content = ""

    if input_method == "Paste Text":
        latex_content = st.text_area(
            "Paste LaTeX Source Code",
            height=280,
            placeholder=r"\documentclass{article}" + "\n" + r"\begin{document}" + "\n" + "Hello World!" + "\n" + r"\end{document}"
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload .tex Document",
            type=["tex"],
            key="tex_uploader"
        )
        if uploaded_file:
            latex_content = uploaded_file.read().decode("utf-8")

    if latex_content:
        st.subheader("LaTeX Syntax Telemetry & Validation")

        with st.expander("Show Raw LaTeX Source Preview", expanded=False):
            st.code(latex_content, language="latex")

        errors = validate_latex(latex_content)

        if errors:
            st.error("Validation Errors Detected:")
            for error in errors:
                st.write("•", error)
        else:
            st.success("No Validation Syntax Errors Found")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Generate DOCX Document", type="primary", use_container_width=True):
            if not latex_content.strip():
                st.warning("Please enter or upload LaTeX content first.")
            else:
                try:
                    with st.spinner("Transcribing LaTeX to DOCX..."):
                        docx_file = convert_latex_to_docx(latex_content)
                        st.session_state.docx_file = docx_file
                        st.session_state.pdf_file = None
                    st.success("DOCX Document Generated Successfully!")
                except Exception as e:
                    st.error(f"Conversion Failed: {e}")

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
                    st.success("PDF Document Generated Successfully!")
                except Exception as e:
                    st.error(f"PDF Conversion Failed: {e}")

    if st.session_state.pdf_file and os.path.exists(st.session_state.pdf_file):
        st.markdown("---")
        with st.container(border=True):
            st.subheader("3. PDF Management & Page Slicing")

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
                    "Select PDF Action:",
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