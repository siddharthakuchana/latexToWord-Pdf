# Constellation Document & PDF Studio Pro 🌌

A deep-space themed web application designed to **join multiple PDF documents**, **split & extract PDF page ranges**, **compress PDFs and images to exact target sizes or qualities**, and **convert LaTeX documents into editable Microsoft Word (`.docx`) and PDF formats**.

---

## Overview

Working with research papers, technical reports, multi-part documentation, and high-resolution scans often requires several disparate tools. 

This suite provides a unified, constellation-themed web application powered by **Streamlit** and **pypdf**:
1. **🌌 Multi-PDF File Joiner & Merger (Supernova)**: Select and combine two or more PDFs with interactive orbital reordering (⬆️ / ⬇️), page range calculation, and automatic table of contents bookmarking.
2. **☄️ PDF Page Splitter & Extractor (Comet)**: Divide any multi-page PDF into single-page star PDFs (downloadable individually or as a `.zip` archive) or slice out specific page intervals ("From Page X to Page Y").
3. **🕳️ Universal File Compressor (Gravity Engine)**: Intelligently shrink PDFs and images (JPEG, PNG, WEBP, TIFF, BMP) down to a precise target file size (KB / MB) or desired visual quality percentage.
4. **📜 LaTeX to Word & PDF Conversion (Celestial Scribe)**: Convert `.tex` source code or uploaded files into editable Word documents (`.docx`) and publication-ready PDFs with syntax validation.
5. **🛰️ Mission Control Dropdown & Constellation Hub**: Seamless tool switching with synchronized cards and dropdown control.

---

## Key Features

### 🌌 Multi-File Joiner & Universal Document Synthesizer (Enhanced!)
* **Universal File Support**: Upload and join **PDFs, JPEGs, PNGs, WEBPs, BMPs, and TIFFs** in any sequence.
* **Incremental Batch Uploading**: Select one file, then click **➕ Add More Files** at any time to append additional documents without losing existing items.
* **Flexible Extraction & Export Formats**:
  - 📄 **Consolidated PDF (`.pdf`)**: Unified multi-page document with automatic Table of Contents bookmarks.
  - 🖼️ **Lossless Image Package (`.zip`)**: Individual high-resolution PNG images of all merged pages.
  - 🖼️ **Optimized JPEG Package (`.zip`)**: Compressed JPEG images of all pages.
  - 📑 **Multi-Page TIFF (`.tiff`)**: Single unified multi-page TIFF file.
* **Interactive Document Queue**: Inspect each file's format, page count or resolution, and size.
* **Orbital Reordering**: Move files up (⬆️) or down (⬇️) or reverse order to set the exact merge sequence.
* **Page Breakdown Matrix**: Inspect the exact page interval of each document within the consolidated output.

### ✂️ PDF Page Splitting & Range Extraction Features
* **Divide into Single Pages**: Automatically split a multi-page PDF into individual 1-page PDF files packaged in a single `.zip` file or available for individual download.
* **Extract Page Range**: Select custom start and end boundaries to extract a trimmed PDF.
* **Direct Upload & LaTeX Integration**: Works on directly uploaded PDFs or files generated within the app.

### 🗜️ Universal File Compressor Features
* **Dual Control Modes**: Optimize by visual quality percentage (5% – 95%) or enforce a strict target file size in KB or MB.
* **Format Conversion**: Convert images to modern WebP or standard JPEG for additional size reduction.
* **Side-by-Side Comparison**: Visual comparison and compression percentage metrics.

### 📝 LaTeX Converter Features
* **Input Methods**: Direct text paste or `.tex` file upload.
* **Syntax Validation**: Automatic detection of unbalanced braces `{}` and environment mismatches (`\begin` / `\end`).
* **Document Generation**: High fidelity conversion to `.docx` format via Pandoc.
* **PDF Export**: One-click DOCX-to-PDF conversion via `docx2pdf`.

---

## Technology Stack

| Technology | Purpose |
| ---------- | ------- |
| Python 3 | Core backend processing engine |
| Streamlit | Modern reactive web application UI |
| pypdf | PDF merging, page counting, single-page splitting, & extraction |
| Pillow | Image stream handling, format conversion, & EXIF orientation |
| pypdfium2 | High-fidelity rendering of PDF pages to raster images (PNG/JPEG/TIFF) |
| Pandoc / pypandoc | LaTeX to DOCX conversion |
| docx2pdf | DOCX to PDF conversion (requires Word on Windows) |

---

## Project Structure

```text
latexToWord-Pdf/
│
├── app.py           # Streamlit web application with modern Feature Hub UI
├── pdf_joiner.py    # Multi-PDF joining, ordering & bookmark generation logic
├── pdf_splitter.py  # PDF page counting, single-page splitting & range extraction
├── compressor.py    # Multi-format compression engine (PDF, JPEG, PNG, WEBP)
├── converter.py     # LaTeX to DOCX & DOCX to PDF conversion logic
├── validator.py     # LaTeX syntax validation rules
├── requirements.txt # Python dependencies
└── README.md        # Comprehensive documentation
```

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/latexToWord-pdf.git
cd latexToWord-pdf
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Pandoc (Optional, for LaTeX conversion)
Download and install Pandoc:
[https://pandoc.org/installing.html](https://pandoc.org/installing.html)

---

## Running the Application

Launch the Streamlit web application:
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

---

## Usage Guide

### 🧭 Feature Hub & Navigation
* Use the top **Feature Cards Hub**, the segmented pill buttons, or the sidebar menu to view all features and switch to any tool instantly.

### 1. 🔗 PDF Joiner & Merger
1. Select **🔗 PDF Joiner & Merger**.
2. Upload two or more PDF files via drag-and-drop or file browser.
3. Review the file queue. Use **⬆️ Up** and **⬇️ Down** buttons to set the exact merge order.
4. Specify an output filename and choose whether to add outline bookmarks.
5. Click **🚀 Merge All PDFs Now**.
6. Review the resulting page breakdown and click **⬇️ Download Merged PDF**.

### 2. ✂️ PDF Page Splitter & Extractor
1. Upload a multi-page PDF document.
2. Select **Divide PDF into Single Pages** to generate individual 1-page PDFs as a ZIP.
3. Or select **Extract Specific Page Range** to extract pages from X to Y.

### 3. 🗜️ Universal File Compressor
1. Upload any PDF or image file.
2. Select **Target Quality (%)** or **Target File Size (KB / MB)**.
3. Click **🗜️ Compress File Now** and inspect before/after metrics.

### 4. 📝 LaTeX to Document Converter
1. Select **Paste Text** or **Upload File** (`.tex`).
2. Click **Generate DOCX** and optionally convert to PDF.

---

## Author
Siddhartha Kuchana
