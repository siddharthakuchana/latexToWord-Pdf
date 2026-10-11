import os
import io
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
from pdf_security import (
    encrypt_pdf,
    decrypt_pdf,
    watermark_pdf,
    get_pdf_metadata,
    update_pdf_metadata,
    strip_pdf_metadata
)
from pdf_organizer import (
    rotate_pdf_pages,
    reorder_and_delete_pages,
    add_page_numbers
)
from pdf_to_images import convert_pdf_to_images
from pdf_comparator import compare_pdfs
from pdf_extractor_ocr import (
    extract_native_text,
    extract_ocr_text,
    check_ocr_availability
)
from pdf_audio import (
    extract_text_for_speech,
    generate_speech_audio,
    GTTS_AVAILABLE
)
from latex_studio import (
    FORMULA_CATALOG,
    render_latex_equation_image,
    validate_bibtex_entry,
    MATPLOTLIB_AVAILABLE
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
FEATURE_ORGANIZER = "🔄 PageForge (Rotate, Reorder & Number)"
FEATURE_SECURITY = "🔐 GuardPDF (Protect, Watermark & Scrub)"
FEATURE_RASTER = "🖼️ PixelRender (High-Res PDF to Images)"
FEATURE_DIFF = "⚖️ DiffVision (Visual PDF Comparator)"
FEATURE_EXTRACTOR = "🔍 TextScope (OCR & Text Extraction)"
FEATURE_AUDIO = "🎧 AudioDoc (PDF Voice & Narration Reader)"
FEATURE_COMPRESSOR = "🗜️ Smart File Compressor (Size & Quality)"
FEATURE_LATEX = "📝 TeXPublish (LaTeX Documents & Math Studio)"

ALL_FEATURES = [
    FEATURE_JOINER,
    FEATURE_SPLITTER,
    FEATURE_ORGANIZER,
    FEATURE_SECURITY,
    FEATURE_RASTER,
    FEATURE_DIFF,
    FEATURE_EXTRACTOR,
    FEATURE_AUDIO,
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
    .badge-guard {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(248, 113, 113, 0.4);
    }
    .badge-forge {
        background: rgba(236, 72, 153, 0.2);
        color: #f472b6;
        border: 1px solid rgba(244, 114, 182, 0.4);
    }
    .badge-diff {
        background: rgba(6, 182, 212, 0.2);
        color: #22d3ee;
        border: 1px solid rgba(34, 211, 238, 0.4);
    }
    .badge-audio {
        background: rgba(139, 92, 246, 0.2);
        color: #a78bfa;
        border: 1px solid rgba(167, 139, 250, 0.4);
    }
    .badge-pixel {
        background: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        border: 1px solid rgba(129, 140, 248, 0.4);
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
    <div class="stardust-badge">⚡ 10-in-1 Professional Document & PDF Power Suite</div>
    <div class="cosmic-title">OmniDoc Studio Pro</div>
    <div class="cosmic-subtitle">
        An all-in-one suite to <strong>merge multi-format files</strong>, <strong>split & slice pages</strong>, 
        <strong>rotate & reorder</strong>, <strong>encrypt & watermark</strong>, <strong>rasterize high-res images</strong>, 
        <strong>compare visual diffs</strong>, <strong>extract text & OCR</strong>, <strong>listen to audio narrations</strong>, 
        <strong>compress to target sizes</strong>, and <strong>compile LaTeX into Word & PDF</strong>.
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# FEATURE CARDS HUB (VISUAL TOOL SHOWCASE)
# ==============================================================================

st.markdown("### 🧭 Feature Hub — All 10 Professional Tools")
st.caption("Click any feature card below or select from the dropdown to activate any tool instantly.")

# Row 1: Document Structure & Compression
st.markdown("##### 📑 Document Structure & Optimization")
r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)

with r1_c1:
    is_act = (st.session_state.current_tool == FEATURE_JOINER)
    card_cls = "constellation-card orbiting" if is_act else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-supernova">MULTI-FORMAT</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">📑 OmniMerge</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 44px;">
            Join PDFs and images (JPG, PNG, WEBP, TIFF) into a unified PDF or image archive.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✅ Active" if is_act else "👉 OmniMerge", key="btn_hub_joiner", type="primary" if is_act else "secondary", use_container_width=True, on_click=set_active_tool, args=(FEATURE_JOINER,))

with r1_c2:
    is_act = (st.session_state.current_tool == FEATURE_SPLITTER)
    card_cls = "constellation-card orbiting" if is_act else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-comet">EXTRACTOR</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">✂️ PageSlicer</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 44px;">
            Divide multi-page PDFs into single-page files (ZIP) or extract custom page intervals.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✅ Active" if is_act else "👉 PageSlicer", key="btn_hub_splitter", type="primary" if is_act else "secondary", use_container_width=True, on_click=set_active_tool, args=(FEATURE_SPLITTER,))

with r1_c3:
    is_act = (st.session_state.current_tool == FEATURE_ORGANIZER)
    card_cls = "constellation-card orbiting" if is_act else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-forge">ORGANIZER</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">🔄 PageForge</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 44px;">
            Rotate pages, reorder sequences, delete unwanted pages, and stamp dynamic page numbers.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✅ Active" if is_act else "👉 PageForge", key="btn_hub_organizer", type="primary" if is_act else "secondary", use_container_width=True, on_click=set_active_tool, args=(FEATURE_ORGANIZER,))

with r1_c4:
    is_act = (st.session_state.current_tool == FEATURE_COMPRESSOR)
    card_cls = "constellation-card orbiting" if is_act else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-gravity">OPTIMIZER</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">🗜️ OptiCompress</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 44px;">
            Compress PDFs & images down to exact target KB/MB or adjustable quality sliders.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✅ Active" if is_act else "👉 OptiCompress", key="btn_hub_comp", type="primary" if is_act else "secondary", use_container_width=True, on_click=set_active_tool, args=(FEATURE_COMPRESSOR,))

# Row 2: Security, Inspection & Comparison
st.markdown("##### 🔐 Security, Inspection & Comparison")
r2_c1, r2_c2, r2_c3 = st.columns(3)

with r2_c1:
    is_act = (st.session_state.current_tool == FEATURE_SECURITY)
    card_cls = "constellation-card orbiting" if is_act else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-guard">SECURITY</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">🔐 GuardPDF</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 44px;">
            Password encryption, permissions, custom text/logo watermarking, and metadata privacy scrubbing.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✅ Active" if is_act else "👉 GuardPDF", key="btn_hub_security", type="primary" if is_act else "secondary", use_container_width=True, on_click=set_active_tool, args=(FEATURE_SECURITY,))

with r2_c2:
    is_act = (st.session_state.current_tool == FEATURE_DIFF)
    card_cls = "constellation-card orbiting" if is_act else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-diff">PIXEL-DIFF</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">⚖️ DiffVision</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 44px;">
            Compare two PDF versions side-by-side with pixel diff highlights, metrics, and report exports.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✅ Active" if is_act else "👉 DiffVision", key="btn_hub_diff", type="primary" if is_act else "secondary", use_container_width=True, on_click=set_active_tool, args=(FEATURE_DIFF,))

with r2_c3:
    is_act = (st.session_state.current_tool == FEATURE_EXTRACTOR)
    card_cls = "constellation-card orbiting" if is_act else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-supernova">TEXT / OCR</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">🔍 TextScope</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 44px;">
            Extract digital text or run OCR on scanned documents; export to formatted Markdown and TXT.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✅ Active" if is_act else "👉 TextScope", key="btn_hub_extractor", type="primary" if is_act else "secondary", use_container_width=True, on_click=set_active_tool, args=(FEATURE_EXTRACTOR,))

# Row 3: Media, Audio & Publishing
st.markdown("##### 🎨 Media, Audio & Publishing")
r3_c1, r3_c2, r3_c3 = st.columns(3)

with r3_c1:
    is_act = (st.session_state.current_tool == FEATURE_RASTER)
    card_cls = "constellation-card orbiting" if is_act else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-pixel">DPI-RASTER</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">🖼️ PixelRender</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 44px;">
            Export PDF pages into crisp PNG, JPEG, WEBP, or TIFF images with customizable DPI (72-300).
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✅ Active" if is_act else "👉 PixelRender", key="btn_hub_raster", type="primary" if is_act else "secondary", use_container_width=True, on_click=set_active_tool, args=(FEATURE_RASTER,))

with r3_c2:
    is_act = (st.session_state.current_tool == FEATURE_AUDIO)
    card_cls = "constellation-card orbiting" if is_act else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-audio">VOICE-AI</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">🎧 AudioDoc</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 44px;">
            Transform PDFs into spoken audiobooks; listen live in-browser or download high-fidelity MP3s.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✅ Active" if is_act else "👉 AudioDoc", key="btn_hub_audio", type="primary" if is_act else "secondary", use_container_width=True, on_click=set_active_tool, args=(FEATURE_AUDIO,))

with r3_c3:
    is_act = (st.session_state.current_tool == FEATURE_LATEX)
    card_cls = "constellation-card orbiting" if is_act else "constellation-card"
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="cosmic-badge badge-scribe">DOCX / FORMULAS</span>
        <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">📝 TeXPublish</h4>
        <p style="font-size: 0.83rem; color: #94a3b8; margin: 0 0 10px 0; min-height: 44px;">
            Convert LaTeX to Word & PDF, render math formulas to 300 DPI PNG, and validate BibTeX.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✅ Active" if is_act else "👉 TeXPublish", key="btn_hub_latex", type="primary" if is_act else "secondary", use_container_width=True, on_click=set_active_tool, args=(FEATURE_LATEX,))


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
            Select any tool from the suite
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

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
    st.caption("All-in-One 10-Tool Document Powerhouse")
    st.info(f"**Currently Active**:\n{st.session_state.current_tool}")

    st.markdown("---")
    st.markdown("#### ⚡ Quick Switcher")
    tool_icons = {
        FEATURE_JOINER: "📑 OmniMerge",
        FEATURE_SPLITTER: "✂️ PageSlicer",
        FEATURE_ORGANIZER: "🔄 PageForge",
        FEATURE_SECURITY: "🔐 GuardPDF",
        FEATURE_RASTER: "🖼️ PixelRender",
        FEATURE_DIFF: "⚖️ DiffVision",
        FEATURE_EXTRACTOR: "🔍 TextScope",
        FEATURE_AUDIO: "🎧 AudioDoc",
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
# TOOL 1: 📑 OMNIMERGE (MULTI-FILE JOINER & SYNTHESIZER)
# ==============================================================================

if st.session_state.current_tool == FEATURE_JOINER:
    st.header("🌌 Multi-File Joiner & Universal Document Synthesizer")
    st.markdown(
        "Join **PDFs, JPEGs, PNGs, WEBPs, BMPs, or TIFFs** into a unified document or image package. "
        "Upload files individually or in batches, arrange their order, and **choose your preferred extraction format**."
    )

    with st.container(border=True):
        up_h1, up_h2 = st.columns([3, 1])
        with up_h1:
            st.markdown("#### 📥 Select or Drag Files to Join")
            st.caption("Supports **PDF, JPEG, PNG, WEBP, TIFF, BMP** documents and images.")
        with up_h2:
            if st.button("➕ Add More Files", key="btn_add_more_files_top", use_container_width=True):
                st.session_state.uploader_round += 1
                st.rerun()

        uploaded_join_files = st.file_uploader(
            "Select files to join (PDF, Images)",
            type=["pdf", "png", "jpg", "jpeg", "webp", "bmp", "tiff", "tif"],
            accept_multiple_files=True,
            key=f"pdf_joiner_uploader_{st.session_state.uploader_round}",
            label_visibility="collapsed"
        )

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
        st.success(f"✅ **{len(queue)} file(s) currently in queue.** Use **➕ Add More Files** above to append additional items.")

        total_q_files = len(queue)
        total_q_pages = sum(item["pages"] for item in queue if item["valid"])
        total_q_size = sum(item["size_bytes"] for item in queue)

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
                st.metric("⚡ Status", f"{valid_count}/{total_q_files} Valid")

        st.markdown("### 📋 Document Merge Sequence")
        st.caption("Arrange files in your exact preferred reading sequence using ⬆️ Up and ⬇️ Down buttons.")

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
                    index=0
                )
                fmt_code = "PDF"
                if "PNG" in export_format_choice:
                    fmt_code = "PNG_ZIP"
                elif "JPEG" in export_format_choice:
                    fmt_code = "JPEG_ZIP"
                elif "TIFF" in export_format_choice:
                    fmt_code = "TIFF"

                output_base_name = st.text_input("Base Output Filename", value="synthesized_document")

            with s2:
                if fmt_code == "PDF":
                    add_toc_bookmarks = st.checkbox("📑 Generate Table of Contents (Outline Bookmarks)", value=True)
                    selected_dpi = 150
                else:
                    add_toc_bookmarks = False
                    selected_dpi = st.select_slider("Image Rendering Resolution (DPI)", options=[100, 150, 200, 300], value=150)

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
                    st.success(f"🎉 Successfully joined {merge_res['total_files']} files ({merge_res['total_pages']} pages)!")
                except Exception as e:
                    st.error(f"Join & extraction failed: {e}")

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

                with st.expander("📑 View Document Sequence Matrix", expanded=True):
                    for item in res["file_breakdown"]:
                        b_col1, b_col2, b_col3 = st.columns([1, 6, 3])
                        with b_col1:
                            st.write(f"**#{item['order']}**")
                        with b_col2:
                            t_badge = "📄 PDF" if item["file_type"] == "PDF" else "🖼️ Image"
                            st.write(f"{item['filename']} `({t_badge})`")
                        with b_col3:
                            st.write(f"Pages **{item['start_page']}** – **{item['end_page']}** ({item['pages']} page{'s' if item['pages']>1 else ''})")

                st.download_button(
                    label=f"⬇️ Download {res['output_filename']} ({format_size(res['total_size_bytes'])})",
                    data=res["bytes"],
                    file_name=res["output_filename"],
                    mime=res["mime_type"],
                    type="primary",
                    use_container_width=True
                )
                if res["format"] != "PDF" and "pdf_bytes" in res:
                    st.download_button(
                        label=f"📄 Also Download as Single Consolidated PDF ({format_size(len(res['pdf_bytes']))})",
                        data=res["pdf_bytes"],
                        file_name=f"{os.path.splitext(res['output_filename'])[0]}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )


# ==============================================================================
# TOOL 2: ✂️ PAGESLICER (PDF PAGE SPLITTER & EXTRACTOR)
# ==============================================================================

elif st.session_state.current_tool == FEATURE_SPLITTER:
    st.header("✂️ PageSlicer — PDF Page Splitter & Range Extractor")
    st.markdown("Divide multi-page PDFs into single-page files (individual or ZIP) or extract specific page ranges.")

    uploaded_pdf = st.file_uploader("Upload PDF Document", type=["pdf"], key="direct_pdf_uploader")

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
                st.write(f"Split **{total_pages}-page** PDF into **{total_pages} individual single-page PDF documents**.")

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
                col_from, col_to = st.columns(2)
                with col_from:
                    from_page = st.number_input("From Page (Start)", min_value=1, max_value=total_pages, value=1, step=1)
                with col_to:
                    to_page = st.number_input("To Page (End)", min_value=1, max_value=total_pages, value=total_pages, step=1)

                if from_page > to_page:
                    st.error("⚠️ Invalid range: 'From Page' must be less than or equal to 'To Page'.")
                else:
                    selected_count = to_page - from_page + 1
                    st.info(f"Extracting **{selected_count} page(s)** (Page {from_page} through Page {to_page} of {total_pages} total).")

                    if st.button(f"✂️ Extract Pages {from_page} to {to_page}", type="primary", use_container_width=True):
                        with st.spinner(f"Extracting pages {from_page} to {to_page}..."):
                            ext_res = extract_pdf_pages(pdf_bytes, start_page=from_page, end_page=to_page, base_filename=pdf_name)
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
# TOOL 3: 🔄 PAGEFORGE (ROTATE, REORDER & NUMBER)
# ==============================================================================

elif st.session_state.current_tool == FEATURE_ORGANIZER:
    st.header("🔄 PageForge — Rotate, Reorder & Dynamic Numbering")
    st.markdown("Rotate upside-down pages, customize reading sequences, delete unwanted sheets, or stamp clean page numbers.")

    up_organizer_pdf = st.file_uploader("Upload PDF Document to Organize", type=["pdf"], key="forge_uploader")

    if up_organizer_pdf:
        org_bytes = up_organizer_pdf.read()
        base_name = os.path.splitext(up_organizer_pdf.name)[0]
        total_p = get_pdf_page_count(org_bytes)

        with st.container(border=True):
            m1, m2, m3 = st.columns(3)
            m1.metric("📁 Document", up_organizer_pdf.name)
            m2.metric("📄 Total Pages", f"{total_p} page(s)")
            m3.metric("📦 Size", format_size(len(org_bytes)))

        tab_rot, tab_reord, tab_nums = st.tabs(["🔄 Rotate Pages", "🔀 Reorder & Delete", "🔢 Dynamic Page Numbering"])

        # Tab 1: Rotate Pages
        with tab_rot:
            st.subheader("Rotate Pages")
            st.caption("Fix scanned or rotated pages by rotating 90°, 180°, or 270°.")

            col_deg, col_target = st.columns(2)
            with col_deg:
                rot_choice = st.selectbox(
                    "Rotation Direction & Angle:",
                    ["90° Clockwise ↷", "180° Upside Down ↻", "90° Counter-Clockwise ↶ (270°)"]
                )
                angle_deg = 90
                if "180" in rot_choice:
                    angle_deg = 180
                elif "Counter-Clockwise" in rot_choice:
                    angle_deg = 270

            with col_target:
                target_mode = st.selectbox(
                    "Apply Rotation To:",
                    ["All Pages", "Odd Pages Only (1, 3, 5...)", "Even Pages Only (2, 4, 6...)", "Custom Pages Selection"]
                )

            custom_pages = ""
            if "Custom" in target_mode:
                custom_pages = st.text_input("Enter Page Numbers to Rotate (e.g., 1, 3-5):", value="1")

            mode_key = "all"
            if "Odd" in target_mode:
                mode_key = "odd"
            elif "Even" in target_mode:
                mode_key = "even"
            elif "Custom" in target_mode:
                mode_key = "custom"

            if st.button("🚀 Apply Page Rotation", type="primary", use_container_width=True):
                try:
                    with st.spinner("Rotating pages..."):
                        rotated_bytes = rotate_pdf_pages(org_bytes, angle_deg, target_mode=mode_key, custom_pages_str=custom_pages)
                    st.success("Pages rotated successfully!")
                    st.download_button(
                        "⬇️ Download Rotated PDF",
                        data=rotated_bytes,
                        file_name=f"{base_name}_rotated.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Rotation failed: {e}")

        # Tab 2: Reorder & Delete Pages
        with tab_reord:
            st.subheader("Reorder & Delete Pages")
            st.caption("Specify new reading order or discard blank and unwanted pages.")

            ord_in = st.text_input(
                "New Page Order (leave blank to keep current order):",
                placeholder=f"e.g., 1, 3, 2, 4-{total_p}",
                help="Specify the exact page order. Ranges like 4-7 are fully supported."
            )
            del_in = st.text_input(
                "Pages to Delete / Discard (optional):",
                placeholder="e.g., 2, 5",
                help="Any page numbers listed here will be removed from the final output."
            )
            rev_flag = st.checkbox("🔄 Reverse Document (flip entire page order)", value=False)

            if st.button("🚀 Reorder & Clean Document", type="primary", use_container_width=True):
                try:
                    with st.spinner("Processing page order..."):
                        reordered_bytes = reorder_and_delete_pages(
                            org_bytes,
                            order_str=ord_in,
                            delete_pages_str=del_in,
                            reverse_order=rev_flag
                        )
                    new_p_count = get_pdf_page_count(reordered_bytes)
                    st.success(f"Document successfully reorganized! Output has {new_p_count} page(s).")
                    st.download_button(
                        f"⬇️ Download Reordered PDF ({new_p_count} pages)",
                        data=reordered_bytes,
                        file_name=f"{base_name}_reordered.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Reordering failed: {e}")

        # Tab 3: Dynamic Page Numbering
        with tab_nums:
            st.subheader("Dynamic Page Numbering & Headers")
            st.caption("Stamp elegant page numbers across all pages.")

            col_fmt, col_pos = st.columns(2)
            with col_fmt:
                template_choice = st.selectbox(
                    "Numbering Format Template:",
                    [
                        "Page {page} of {total}",
                        "- {page} -",
                        "{page} / {total}",
                        "Page {page}",
                        "Custom Template"
                    ]
                )
                if template_choice == "Custom Template":
                    custom_template = st.text_input("Enter Template (use {page} and {total}):", value="Doc • Page {page}")
                else:
                    custom_template = template_choice

            with col_pos:
                pos_choice = st.selectbox(
                    "Stamp Placement Position:",
                    [
                        "Bottom Center (Standard Footer)",
                        "Bottom Right",
                        "Bottom Left",
                        "Top Center (Standard Header)",
                        "Top Right",
                        "Top Left"
                    ]
                )
                pos_map = {
                    "Bottom Center (Standard Footer)": "bottom_center",
                    "Bottom Right": "bottom_right",
                    "Bottom Left": "bottom_left",
                    "Top Center (Standard Header)": "top_center",
                    "Top Right": "top_right",
                    "Top Left": "top_left"
                }
                pos_code = pos_map.get(pos_choice, "bottom_center")

            c_fsize, c_margin = st.columns(2)
            with c_fsize:
                font_sz = st.slider("Font Size (Points):", min_value=8, max_value=18, value=10)
            with c_margin:
                margin_pt = st.slider("Page Margin (Points):", min_value=15, max_value=60, value=30)

            if st.button("🚀 Stamp Page Numbers Now", type="primary", use_container_width=True):
                try:
                    with st.spinner("Stamping page numbers..."):
                        numbered_bytes = add_page_numbers(
                            org_bytes,
                            format_template=custom_template,
                            position=pos_code,
                            font_size=font_sz,
                            margin_pts=float(margin_pt)
                        )
                    st.success("Page numbers stamped successfully!")
                    st.download_button(
                        "⬇️ Download Numbered PDF",
                        data=numbered_bytes,
                        file_name=f"{base_name}_numbered.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Failed to add page numbers: {e}")


# ==============================================================================
# TOOL 4: 🔐 GUARDPDF (PROTECT, WATERMARK & SCRUB)
# ==============================================================================

elif st.session_state.current_tool == FEATURE_SECURITY:
    st.header("🔐 GuardPDF — Security, Watermark & Privacy Suite")
    st.markdown("Password protect, decrypt, apply text/logo watermarks, and scrub identifying metadata from documents.")

    sec_file = st.file_uploader("Upload PDF Document to Secure", type=["pdf"], key="guard_uploader")

    if sec_file:
        sec_bytes = sec_file.read()
        base_name = os.path.splitext(sec_file.name)[0]

        try:
            meta_info = get_pdf_metadata(sec_bytes)
            with st.container(border=True):
                m1, m2, m3 = st.columns(3)
                m1.metric("📁 Document", sec_file.name)
                m2.metric("📄 Pages", f"{meta_info['page_count']} page(s)")
                m3.metric("🔒 Encryption Status", "Encrypted 🔒" if meta_info["is_encrypted"] else "Unencrypted 🔓")

            sec_tab1, sec_tab2, sec_tab3, sec_tab4 = st.tabs([
                "🔒 Password Protect",
                "🔓 Decrypt / Unlock",
                "💧 Watermark Overlay",
                "🛡️ Metadata & Privacy"
            ])

            # Tab 1: Password Protect
            with sec_tab1:
                st.subheader("Encrypt PDF with Password")
                st.caption("Set a user password to lock viewing and configure fine-grained permissions.")

                col_pw1, col_pw2 = st.columns(2)
                with col_pw1:
                    u_pwd = st.text_input("User Password (Required to Open):", type="password", key="sec_u_pwd")
                with col_pw2:
                    o_pwd = st.text_input("Owner Password (Optional, for admin permissions):", type="password", key="sec_o_pwd")

                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    perm_print = st.checkbox("Allow Document Printing", value=True)
                with col_p2:
                    perm_copy = st.checkbox("Allow Text & Content Copying", value=True)

                if st.button("🔒 Encrypt Document Now", type="primary", use_container_width=True):
                    if not u_pwd:
                        st.warning("Please enter a User Password to protect the document.")
                    else:
                        try:
                            with st.spinner("Encrypting PDF with 128-bit AES..."):
                                enc_bytes = encrypt_pdf(
                                    sec_bytes,
                                    user_password=u_pwd,
                                    owner_password=o_pwd if o_pwd else None,
                                    allow_printing=perm_print,
                                    allow_copying=perm_copy
                                )
                            st.success("PDF protected successfully!")
                            st.download_button(
                                "⬇️ Download Protected PDF",
                                data=enc_bytes,
                                file_name=f"{base_name}_protected.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Encryption failed: {e}")

            # Tab 2: Unlock / Decrypt
            with sec_tab2:
                st.subheader("Remove Password Protection")
                st.caption("Unlock a password-protected PDF to generate an open, unencrypted copy.")

                unlock_pwd = st.text_input("Enter Document Password to Unlock:", type="password", key="sec_unlock_pwd")
                if st.button("🔓 Decrypt & Remove Password", type="primary", use_container_width=True):
                    if not unlock_pwd:
                        st.warning("Please enter the password to unlock this file.")
                    else:
                        try:
                            with st.spinner("Decrypting PDF..."):
                                dec_bytes = decrypt_pdf(sec_bytes, password=unlock_pwd)
                            st.success("Document successfully unlocked!")
                            st.download_button(
                                "⬇️ Download Unlocked PDF",
                                data=dec_bytes,
                                file_name=f"{base_name}_unlocked.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Decryption failed: {e}")

            # Tab 3: Watermark Overlay
            with sec_tab3:
                st.subheader("Apply Custom Watermark")
                st.caption("Stamp confidential notices or company logos across all pages.")

                wm_mode = st.radio("Watermark Type:", ["Text Watermark", "Image / Logo Watermark"], horizontal=True)

                if wm_mode == "Text Watermark":
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        wm_text = st.text_input("Watermark Text:", value="CONFIDENTIAL")
                        wm_angle = st.slider("Rotation Angle (°):", min_value=-90, max_value=90, value=45)
                    with col_t2:
                        wm_pos = st.selectbox("Placement Position:", ["Center Diagonal (Standard)", "Header", "Footer", "Tiled Repeating Matrix"])
                        wm_pos_map = {
                            "Center Diagonal (Standard)": "center",
                            "Header": "header",
                            "Footer": "footer",
                            "Tiled Repeating Matrix": "tile"
                        }
                        pos_code = wm_pos_map.get(wm_pos, "center")
                        wm_font_sz = st.slider("Font Size:", min_value=16, max_value=72, value=40)

                    c_opac, c_col = st.columns(2)
                    with c_opac:
                        wm_opacity = st.slider("Opacity / Transparency:", min_value=0.05, max_value=1.0, value=0.25, step=0.05)
                    with c_col:
                        wm_color_choice = st.selectbox("Text Color:", ["Muted Gray", "Crimson Red", "Royal Blue", "Forest Green"])
                        color_map = {
                            "Muted Gray": (0.5, 0.5, 0.5),
                            "Crimson Red": (0.85, 0.1, 0.1),
                            "Royal Blue": (0.1, 0.3, 0.85),
                            "Forest Green": (0.1, 0.6, 0.2)
                        }
                        chosen_rgb = color_map.get(wm_color_choice, (0.5, 0.5, 0.5))

                    if st.button("🚀 Apply Text Watermark", type="primary", use_container_width=True):
                        try:
                            with st.spinner("Applying text watermark..."):
                                wm_bytes = watermark_pdf(
                                    sec_bytes,
                                    text=wm_text,
                                    opacity=wm_opacity,
                                    angle=wm_angle,
                                    font_size=wm_font_sz,
                                    color_rgb=chosen_rgb,
                                    position=pos_code
                                )
                            st.success("Watermark applied successfully!")
                            st.download_button(
                                "⬇️ Download Watermarked PDF",
                                data=wm_bytes,
                                file_name=f"{base_name}_watermarked.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Watermarking failed: {e}")

                else:
                    up_logo = st.file_uploader("Upload Watermark Logo / Image (PNG / JPEG):", type=["png", "jpg", "jpeg"])
                    logo_opacity = st.slider("Logo Opacity:", min_value=0.05, max_value=1.0, value=0.3, step=0.05)
                    if up_logo and st.button("🚀 Apply Image Watermark", type="primary", use_container_width=True):
                        try:
                            with st.spinner("Overlaying watermark image..."):
                                wm_bytes = watermark_pdf(sec_bytes, image_bytes=up_logo.read(), opacity=logo_opacity)
                            st.success("Image watermark applied successfully!")
                            st.download_button(
                                "⬇️ Download Watermarked PDF",
                                data=wm_bytes,
                                file_name=f"{base_name}_watermarked.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Failed to apply logo watermark: {e}")

            # Tab 4: Metadata Inspector & Cleaner
            with sec_tab4:
                st.subheader("Metadata Inspector & Privacy Cleaner")
                st.caption("Inspect and update document properties or wipe all metadata to protect your privacy.")

                st.write("**Current Metadata Tags:**")
                st.json({k: v for k, v in meta_info.items() if k not in ["raw"]})

                col_cl1, col_cl2 = st.columns(2)
                with col_cl1:
                    new_title = st.text_input("Document Title:", value=meta_info.get("title", ""))
                    new_author = st.text_input("Author Name:", value=meta_info.get("author", ""))
                with col_cl2:
                    new_subject = st.text_input("Subject:", value=meta_info.get("subject", ""))
                    new_creator = st.text_input("Creator / Organization:", value=meta_info.get("creator", ""))

                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    if st.button("💾 Save Updated Metadata", use_container_width=True):
                        try:
                            up_bytes = update_pdf_metadata(sec_bytes, {
                                "title": new_title,
                                "author": new_author,
                                "subject": new_subject,
                                "creator": new_creator
                            })
                            st.success("Metadata updated successfully!")
                            st.download_button("⬇️ Download PDF with Updated Metadata", data=up_bytes, file_name=f"{base_name}_metadata.pdf", mime="application/pdf", use_container_width=True)
                        except Exception as e:
                            st.error(f"Failed to update metadata: {e}")

                with btn_c2:
                    if st.button("🛡️ Wipe All Metadata (Sanitize Privacy)", type="primary", use_container_width=True):
                        try:
                            scrub_bytes = strip_pdf_metadata(sec_bytes)
                            st.success("All identifying metadata stripped successfully!")
                            st.download_button("⬇️ Download Sanitized PDF", data=scrub_bytes, file_name=f"{base_name}_sanitized.pdf", mime="application/pdf", use_container_width=True)
                        except Exception as e:
                            st.error(f"Sanitization failed: {e}")

        except Exception as e:
            st.error(f"Error inspecting PDF security properties: {e}")


# ==============================================================================
# TOOL 5: 🖼️ PIXELRENDER (HIGH-RES PDF TO IMAGES)
# ==============================================================================

elif st.session_state.current_tool == FEATURE_RASTER:
    st.header("🖼️ PixelRender — Dedicated High-Res PDF to Images")
    st.markdown("Convert every page of a PDF document into crystal-clear images with custom DPI resolutions.")

    rast_file = st.file_uploader("Upload PDF Document to Rasterize", type=["pdf"], key="raster_uploader")

    if rast_file:
        rast_bytes = rast_file.read()
        base_name = os.path.splitext(rast_file.name)[0]
        total_p = get_pdf_page_count(rast_bytes)

        with st.container(border=True):
            m1, m2 = st.columns(2)
            m1.metric("📁 Document", rast_file.name)
            m2.metric("📄 Total Pages to Render", f"{total_p} page(s)")

        with st.container(border=True):
            c_dpi, c_fmt, c_qual = st.columns(3)
            with c_dpi:
                dpi_preset = st.select_slider(
                    "Rendering Resolution (DPI):",
                    options=[72, 100, 150, 200, 300],
                    value=150,
                    help="72 DPI = fast/web, 150 DPI = standard screen, 300 DPI = crystal-clear print"
                )
            with c_fmt:
                target_format = st.selectbox(
                    "Image Format:",
                    ["PNG (Lossless Quality)", "JPEG (Optimized)", "WEBP (Modern & Small)", "TIFF (Archival)"]
                )
                fmt_code = "PNG"
                if "JPEG" in target_format:
                    fmt_code = "JPEG"
                elif "WEBP" in target_format:
                    fmt_code = "WEBP"
                elif "TIFF" in target_format:
                    fmt_code = "TIFF"

            with c_qual:
                if fmt_code in ["JPEG", "WEBP"]:
                    qual_slider = st.slider("Quality (%):", min_value=20, max_value=100, value=85)
                else:
                    qual_slider = 90
                    st.caption("Lossless encoding active.")

        if st.button("🚀 Render All Pages to Images", type="primary", use_container_width=True):
            try:
                with st.spinner(f"Rasterizing {total_p} pages at {dpi_preset} DPI into {fmt_code}..."):
                    raster_res = convert_pdf_to_images(
                        rast_bytes,
                        dpi=dpi_preset,
                        output_format=fmt_code,
                        jpeg_quality=qual_slider,
                        base_filename=base_name
                    )
                st.session_state.raster_result = raster_res
                st.success(f"🎉 Successfully rendered all {raster_res['total_pages']} pages!")
            except Exception as e:
                st.error(f"Rendering failed: {e}")

        if "raster_result" in st.session_state and st.session_state.raster_result:
            res = st.session_state.raster_result
            st.markdown("---")
            st.subheader("📦 Rendered Image Gallery & Downloads")

            st.download_button(
                label=f"⬇️ Download All {res['total_pages']} Pages as ZIP ({format_size(res['zip_size_bytes'])})",
                data=res["zip_bytes"],
                file_name=res["zip_filename"],
                mime="application/zip",
                type="primary",
                use_container_width=True
            )

            st.markdown("##### Page Gallery & Individual Downloads")
            gal_cols = st.columns(min(3, res["total_pages"]))
            for idx, p_info in enumerate(res["pages"]):
                col_tgt = gal_cols[idx % len(gal_cols)]
                with col_tgt:
                    with st.container(border=True):
                        st.image(p_info["pil_image"], caption=f"Page {p_info['page_number']} ({p_info['width']}x{p_info['height']} px)")
                        st.download_button(
                            label=f"⬇️ Page {p_info['page_number']}",
                            data=p_info["bytes"],
                            file_name=p_info["filename"],
                            mime=p_info["mime_type"],
                            use_container_width=True,
                            key=f"btn_rast_dl_{p_info['page_number']}"
                        )


# ==============================================================================
# TOOL 6: ⚖️ DIFFVISION (VISUAL PDF COMPARATOR)
# ==============================================================================

elif st.session_state.current_tool == FEATURE_DIFF:
    st.header("⚖️ DiffVision — Visual PDF Comparator & Diff Engine")
    st.markdown("Compare two PDF versions side-by-side: detect changes, shifted equations, and layout edits with pixel-level precision.")

    col_up_a, col_up_b = st.columns(2)
    with col_up_a:
        st.markdown("##### 📄 Document A (Original / Version 1)")
        doc_a_file = st.file_uploader("Upload Version 1 (A)", type=["pdf"], key="diff_uploader_a")
    with col_up_b:
        st.markdown("##### 📄 Document B (Modified / Version 2)")
        doc_b_file = st.file_uploader("Upload Version 2 (B)", type=["pdf"], key="diff_uploader_b")

    if doc_a_file and doc_b_file:
        bytes_a = doc_a_file.read()
        bytes_b = doc_b_file.read()

        pages_a = get_pdf_page_count(bytes_a)
        pages_b = get_pdf_page_count(bytes_b)

        with st.container(border=True):
            m1, m2, m3 = st.columns(3)
            m1.metric("Doc A Pages", f"{pages_a} pages")
            m2.metric("Doc B Pages", f"{pages_b} pages")
            diff_pages = abs(pages_a - pages_b)
            m3.metric("Page Count Delta", f"{diff_pages} page{'s' if diff_pages!=1 else ''}")

        col_sens, col_res = st.columns(2)
        with col_sens:
            diff_sens = st.slider("Difference Sensitivity Threshold:", min_value=10, max_value=60, value=25, help="Lower = more sensitive to subtle font/rendering changes.")
        with col_res:
            diff_dpi = st.select_slider("Comparison Resolution (DPI):", options=[100, 150, 200], value=150)

        if st.button("🔍 Run Visual Comparison Now", type="primary", use_container_width=True):
            try:
                with st.spinner("Analyzing document differences across pages..."):
                    diff_res = compare_pdfs(bytes_a, bytes_b, dpi=diff_dpi, threshold=diff_sens)
                st.session_state.diff_result = diff_res
                st.success(f"Comparison finished! Overall Document Similarity: **{diff_res['overall_similarity']}%**")
            except Exception as e:
                st.error(f"Comparison failed: {e}")

        if "diff_result" in st.session_state and st.session_state.diff_result:
            res = st.session_state.diff_result
            st.markdown("---")
            st.subheader("📊 Visual Diff Results & Inspection")

            with st.container(border=True):
                r1, r2, r3 = st.columns(3)
                r1.metric("Overall Visual Match", f"{res['overall_similarity']}%")
                r2.metric("Visual Change", f"{round(100.0 - res['overall_similarity'], 2)}%")
                r3.metric("Pages Inspected", f"{res['total_compared_pages']} page(s)")

            st.download_button(
                label="⬇️ Download Visual Diff Inspection Report (ZIP of all pages)",
                data=res["zip_bytes"],
                file_name=res["zip_filename"],
                mime="application/zip",
                type="primary",
                use_container_width=True
            )

            st.markdown("##### 👁️ Page-by-Page Comparison [Doc A | Visual Diff Overlay | Doc B]")
            st.caption("Differences are highlighted in **vibrant magenta / red**.")

            for p in res["pages"]:
                with st.expander(f"Page {p['page_number']} — Similarity: {p['similarity_pct']}% ({p['changed_pixels']} differing pixels)", expanded=(p['similarity_pct'] < 99.5)):
                    st.image(p["composite_image"], caption=f"Left: Doc A (v1) | Center: Visual Diff Highlight | Right: Doc B (v2)", use_container_width=True)


# ==============================================================================
# TOOL 7: 🔍 TEXTSCOPE (OCR & TEXT EXTRACTION)
# ==============================================================================

elif st.session_state.current_tool == FEATURE_EXTRACTOR:
    st.header("🔍 TextScope — Text, Table & OCR Extraction Studio")
    st.markdown("Extract raw text, analyze reading telemetry, or run OCR on scanned documents; export to Markdown and TXT.")

    ocr_ready, ocr_msg = check_ocr_availability()

    extr_file = st.file_uploader("Upload PDF Document to Extract Text", type=["pdf"], key="extractor_uploader")

    if extr_file:
        extr_bytes = extr_file.read()
        base_name = os.path.splitext(extr_file.name)[0]
        total_p = get_pdf_page_count(extr_bytes)

        with st.container(border=True):
            m1, m2 = st.columns(2)
            m1.metric("📁 Document", extr_file.name)
            m2.metric("📄 Total Pages", f"{total_p} page(s)")

        strategy = st.radio(
            "Extraction Engine:",
            ["⚡ Digital Text Extraction (pypdf - Fast, native text)", "👁️ Optical Character Recognition (OCR - For scanned pages)"],
            horizontal=True
        )

        if "OCR" in strategy and not ocr_ready:
            st.warning(f"⚠️ {ocr_msg} Using digital extraction is recommended unless Tesseract OCR binary is installed.")

        if st.button("🚀 Extract Text Now", type="primary", use_container_width=True):
            try:
                with st.spinner("Extracting text and telemetry..."):
                    if "OCR" in strategy and ocr_ready:
                        text_res = extract_ocr_text(extr_bytes)
                    else:
                        text_res = extract_native_text(extr_bytes)
                st.session_state.extractor_result = text_res
                st.success("Text extracted successfully!")
            except Exception as e:
                st.error(f"Extraction failed: {e}")

        if "extractor_result" in st.session_state and st.session_state.extractor_result:
            res = st.session_state.extractor_result
            st.markdown("---")
            st.subheader("📊 Document Telemetry")

            with st.container(border=True):
                t1, t2, t3, t4 = st.columns(4)
                t1.metric("Total Word Count", f"{res['total_words']:,} words")
                t2.metric("Total Characters", f"{res['total_chars']:,} chars")
                t3.metric("Est. Reading Time", f"~{res['reading_time_mins']} min(s)")
                t4.metric("Blank Pages", f"{res['empty_pages_count']} page(s)")

            dl_c1, dl_c2 = st.columns(2)
            with dl_c1:
                st.download_button(
                    "⬇️ Download as Formatted Markdown (.md)",
                    data=res["markdown"],
                    file_name=f"{base_name}_extracted.md",
                    mime="text/markdown",
                    type="primary",
                    use_container_width=True
                )
            with dl_c2:
                st.download_button(
                    "⬇️ Download as Plain Text (.txt)",
                    data=res["plain_text"],
                    file_name=f"{base_name}_extracted.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            st.markdown("##### Preview Extracted Document Text")
            st.text_area("Document Content", value=res["plain_text"], height=320)


# ==============================================================================
# TOOL 8: 🎧 AUDIODOC (PDF VOICE & NARRATION READER)
# ==============================================================================

elif st.session_state.current_tool == FEATURE_AUDIO:
    st.header("🎧 AudioDoc — PDF Voice & Narration Audiobook Studio")
    st.markdown("Convert research papers, articles, and textbooks into spoken audiobooks. Listen live or download MP3 files.")

    audio_file = st.file_uploader("Upload PDF Document to Narrate", type=["pdf"], key="audio_uploader")

    if audio_file:
        audio_bytes = audio_file.read()
        base_name = os.path.splitext(audio_file.name)[0]
        total_p = get_pdf_page_count(audio_bytes)

        with st.container(border=True):
            m1, m2 = st.columns(2)
            m1.metric("📁 Document", audio_file.name)
            m2.metric("📄 Total Pages", f"{total_p} page(s)")

        col_sp, col_ep = st.columns(2)
        with col_sp:
            sp_val = st.number_input("Start From Page:", min_value=1, max_value=total_p, value=1)
        with col_ep:
            ep_val = st.number_input("End At Page:", min_value=1, max_value=total_p, value=min(total_p, 5))

        col_lang, col_speed = st.columns(2)
        with col_lang:
            accent_choice = st.selectbox(
                "Voice Accent & Locale:",
                ["US English (com)", "British English (co.uk)", "Australian English (com.au)", "Indian English (co.in)"]
            )
            tld_map = {
                "US English (com)": "com",
                "British English (co.uk)": "co.uk",
                "Australian English (com.au)": "com.au",
                "Indian English (co.in)": "co.in"
            }
            chosen_tld = tld_map.get(accent_choice, "com")
        with col_speed:
            slow_flag = st.checkbox("Slower Speaking Pace", value=False)

        if st.button("🎙️ Generate Spoken Narration (MP3)", type="primary", use_container_width=True):
            if not GTTS_AVAILABLE:
                st.error("gTTS library is not installed. Please install gTTS.")
            else:
                try:
                    with st.spinner("Extracting text and synthesizing speech..."):
                        speech_text_info = extract_text_for_speech(audio_bytes, start_page=sp_val, end_page=ep_val)
                        if not speech_text_info["text"]:
                            st.warning("No readable text found on the selected pages.")
                        else:
                            audio_res = generate_speech_audio(speech_text_info["text"], lang="en", tld=chosen_tld, slow=slow_flag)
                            audio_res["text_info"] = speech_text_info
                            st.session_state.audio_result = audio_res
                            st.success("🎉 Audiobook Narration Generated Successfully!")
                except Exception as e:
                    st.error(f"Speech synthesis failed: {e}")

        if "audio_result" in st.session_state and st.session_state.audio_result:
            res = st.session_state.audio_result
            txt_info = res["text_info"]
            st.markdown("---")
            st.subheader("🔊 Listen to Audio Narration")

            with st.container(border=True):
                m1, m2, m3 = st.columns(3)
                m1.metric("Pages Read", f"Pages {txt_info['start_page']}–{txt_info['end_page']}")
                m2.metric("Spoken Words", f"{txt_info['total_words']} words")
                m3.metric("Est. Duration", f"~{txt_info['est_duration_mins']} mins")

            # In-app audio player
            st.audio(res["audio_bytes"], format="audio/mp3")

            st.download_button(
                label=f"⬇️ Download Audiobook MP3 ({format_size(res['size_bytes'])})",
                data=res["audio_bytes"],
                file_name=f"{base_name}_narration.mp3",
                mime="audio/mp3",
                type="primary",
                use_container_width=True
            )

            with st.expander("Show Spoken Narration Transcript"):
                st.write(txt_info["text"])


# ==============================================================================
# TOOL 9: 🗜️ OPTICOMPRESS (UNIVERSAL FILE COMPRESSOR)
# ==============================================================================

elif st.session_state.current_tool == FEATURE_COMPRESSOR:
    st.header("🗜️ OptiCompress — Smart File Compressor")
    st.markdown("Compress **PDFs, Images (JPEG, PNG, WEBP, TIFF, BMP)** to any target file size (KB / MB) or visual quality level.")

    uploaded_comp_file = st.file_uploader("Upload File to Compress (PDF, Image, Document)", key="universal_compressor_uploader")

    if uploaded_comp_file is not None:
        file_bytes = uploaded_comp_file.read()
        file_name = uploaded_comp_file.name
        orig_size_bytes = len(file_bytes)
        orig_size_kb = max(1.0, orig_size_bytes / 1024.0)
        orig_size_mb = orig_size_kb / 1024.0

        with st.container(border=True):
            info_col1, info_col2, info_col3 = st.columns(3)
            info_col1.metric("📁 Selected File", file_name)
            info_col2.metric("📦 Original Size", format_size(orig_size_bytes))
            file_ext = os.path.splitext(file_name)[1].upper().lstrip(".")
            info_col3.metric("🏷️ Detected Format", file_ext if file_ext else "UNKNOWN")

        st.markdown("---")
        st.subheader("⚙️ Compression Settings & Controls")

        mode = st.radio("Select Compression Strategy:", ["Target Quality (%)", "Target File Size (KB / MB)"], horizontal=True, key="comp_mode_selector")

        target_quality = 65
        target_size_kb_arg = None

        if mode == "Target Quality (%)":
            st.markdown("##### Adjust Compression Quality")
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
                st.slider("Quality Range Slider", min_value=5, max_value=95, step=1, key="quality_slider_val", on_change=on_slider_change)
            with col_box:
                st.number_input("Quality Value (%)", min_value=5, max_value=95, step=1, key="quality_box_val", on_change=on_box_change)

            target_quality = st.session_state["quality_slider_val"]

        else:
            st.markdown("##### Set Desired Target File Size")
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
                st.slider(f"Target Size Range Slider ({size_unit})", min_value=float(round(min_limit, 2)), max_value=float(round(max_limit, 2)), step=float(step_val), key=target_slider_key, on_change=on_target_slider_change)
            with col_t_box:
                st.number_input(f"Target Size Box ({size_unit})", min_value=float(round(min_limit, 2)), max_value=float(round(max_limit, 2)), step=float(step_val), key=target_box_key, on_change=on_target_box_change)

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
                format_choice = st.selectbox("Convert Image Format", ["Keep Original Format", "Convert to WebP (Smaller & Modern)", "Convert to JPEG (Broad Compatibility)"], index=0)
                if "WebP" in format_choice:
                    output_format_opt = "WEBP"
                elif "JPEG" in format_choice:
                    output_format_opt = "JPEG"

        st.markdown("---")
        if st.button("🗜️ Compress File Now", type="primary", use_container_width=True):
            try:
                with st.spinner("Optimizing and compressing file..."):
                    comp_res = compress_file(file_source=file_bytes, filename=file_name, quality=target_quality, target_size_kb=target_size_kb_arg, output_format=output_format_opt)
                    st.session_state.compression_result = comp_res
                st.success("Compression Completed Successfully!")
            except Exception as e:
                st.error(f"Compression failed: {e}")

        if st.session_state.compression_result is not None:
            res = st.session_state.compression_result
            st.markdown("### 📊 Compression Results")
            with st.container(border=True):
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("Original Mass", format_size(res["original_size"]))
                m_col2.metric("Compressed Mass", format_size(res["compressed_size"]), delta=f"-{res['saved_percent']:.1f}%", delta_color="inverse")
                m_col3.metric("Total Space Saved", f"{format_size(res['saved_bytes'])} ({res['saved_percent']:.1f}%)")

            if res.get("file_type") == "image":
                with st.expander("👁️ Visual Comparison (Original vs Compressed)", expanded=True):
                    prev_c1, prev_c2 = st.columns(2)
                    with prev_c1:
                        st.markdown("**Original Image**")
                        st.image(file_bytes, use_container_width=True)
                    with prev_c2:
                        st.markdown("**Compressed Image**")
                        st.image(res["bytes"], use_container_width=True)

            st.download_button(
                label=f"⬇️ Download Compressed File ({res['output_filename']} - {format_size(res['compressed_size'])})",
                data=res["bytes"],
                file_name=res["output_filename"],
                mime=res["mime_type"],
                type="primary",
                use_container_width=True
            )


# ==============================================================================
# TOOL 10: 📝 TEXPUBLISH (LATEX DOCUMENTS & MATH STUDIO)
# ==============================================================================

elif st.session_state.current_tool == FEATURE_LATEX:
    st.header("📝 TeXPublish — LaTeX Document & Equation Studio")
    st.markdown("Compile LaTeX documents into Word (`.docx`) & PDF, render math formulas into crisp 300 DPI PNGs, and validate BibTeX.")

    tex_tab1, tex_tab2, tex_tab3 = st.tabs([
        "📄 LaTeX to Word & PDF Converter",
        "🧮 Math Formula Studio & Renderer",
        "📚 BibTeX Citation Assistant"
    ])

    # Tab 1: Original LaTeX to DOCX & PDF
    with tex_tab1:
        st.subheader("LaTeX to Document Converter (DOCX & PDF)")
        input_method = st.radio("Choose Input Method:", ["Paste Text", "Upload File"], horizontal=True)

        latex_content = ""
        if input_method == "Paste Text":
            latex_content = st.text_area(
                "Paste LaTeX Source Code",
                height=260,
                placeholder=r"\documentclass{article}" + "\n" + r"\begin{document}" + "\n" + "Hello World!" + "\n" + r"\end{document}"
            )
        else:
            uploaded_file = st.file_uploader("Upload .tex Document", type=["tex"], key="tex_uploader")
            if uploaded_file:
                latex_content = uploaded_file.read().decode("utf-8")

        if latex_content:
            st.subheader("LaTeX Syntax Validation")
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
                st.download_button("⬇️ Download Full PDF Document", data=pdf_bytes, file_name="converted.pdf", mime="application/pdf", use_container_width=True)

    # Tab 2: Math Formula Studio
    with tex_tab2:
        st.subheader("🧮 Math Formula Studio & Image Renderer")
        st.caption("Write or select math formulas, preview them live, and export crisp 300 DPI PNGs for Word or PowerPoint.")

        st.markdown("##### 📚 Quick Insert Formula Templates")
        cat_choice = st.selectbox("Category:", list(FORMULA_CATALOG.keys()))
        selected_cat_formulas = FORMULA_CATALOG[cat_choice]
        f_name = st.selectbox("Select Formula Template:", list(selected_cat_formulas.keys()))
        sample_formula = selected_cat_formulas[f_name]

        eq_input = st.text_area(
            "LaTeX Mathematical Formula Code:",
            value=sample_formula,
            height=100,
            help="Type LaTeX math (e.g. \\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2})"
        )

        st.markdown("##### 👁️ Live Formula Preview")
        try:
            st.latex(eq_input)
        except Exception as e:
            st.warning(f"Preview warning: {e}")

        col_opts1, col_opts2 = st.columns(2)
        with col_opts1:
            eq_fontsize = st.slider("Render Font Size:", min_value=16, max_value=48, value=26)
        with col_opts2:
            eq_trans = st.checkbox("Transparent Background (PNG)", value=True)

        if st.button("🖼️ Render Formula as 300 DPI PNG", type="primary", use_container_width=True):
            if not MATPLOTLIB_AVAILABLE:
                st.error("matplotlib is required to render formula images.")
            else:
                try:
                    with st.spinner("Rendering equation..."):
                        img_bytes = render_latex_equation_image(
                            eq_input,
                            fontsize=eq_fontsize,
                            dpi=300,
                            transparent=eq_trans
                        )
                    st.session_state.formula_image_result = img_bytes
                    st.success("Equation rendered successfully!")
                except Exception as e:
                    st.error(f"Render failed: {e}")

        if "formula_image_result" in st.session_state and st.session_state.formula_image_result:
            st.image(st.session_state.formula_image_result, caption="Rendered Formula Preview (300 DPI)")
            st.download_button(
                "⬇️ Download Formula PNG Image (300 DPI)",
                data=st.session_state.formula_image_result,
                file_name="rendered_formula.png",
                mime="image/png",
                type="primary",
                use_container_width=True
            )

    # Tab 3: BibTeX Citation Assistant
    with tex_tab3:
        st.subheader("📚 BibTeX Citation Formatter & Validator")
        st.caption("Validate citation entries, detect missing recommended fields, and beautify indentation.")

        sample_bib = """@article{einstein1905photoelectric,
  author = {Einstein, Albert},
  title = {Über einen die Erzeugung und Verwandlung des Lichtes betreffenden heuristischen Gesichtspunkt},
  journal = {Annalen der Physik},
  year = {1905},
  volume = {17},
  pages = {132--148}
}"""
        bib_input = st.text_area("Paste BibTeX Entry:", value=sample_bib, height=180)

        if st.button("🔍 Validate & Beautify BibTeX", type="primary", use_container_width=True):
            bib_res = validate_bibtex_entry(bib_input)
            if not bib_res["valid"]:
                st.error(f"⚠️ BibTeX Syntax Error: {bib_res['error']}")
            else:
                st.success(f"✅ Valid BibTeX `{bib_res['entry_type'].upper()}` entry (Key: `{bib_res['key']}`).")
                if bib_res["missing_recommended"]:
                    st.warning(f"Missing recommended standard fields: {', '.join(bib_res['missing_recommended'])}")

                st.markdown("##### Beautified BibTeX Code")
                st.code(bib_res["beautified"], language="bibtex")