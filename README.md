# OmniDoc Studio Pro 📑⚡

A modern, professional 10-in-1 document and PDF power suite designed to **synthesize multi-format documents**, **split & slice page ranges**, **rotate & reorganize pages**, **encrypt & watermark**, **render high-resolution images**, **compare visual diffs**, **extract text & OCR**, **generate audiobooks**, **compress files to exact target sizes**, and **compile LaTeX documents into editable Microsoft Word (`.docx`) and publication-ready PDFs**.

---

## 🧭 The 10-Tool Power Suite

| Tool | Codename | Purpose | Supported Formats |
| :--- | :--- | :--- | :--- |
| 1. **Universal File Merger** | 📑 **OmniMerge** | Join and synthesize multi-page PDFs and images in any custom order with bookmarks | PDF, PNG, JPG, WEBP, TIFF, BMP |
| 2. **Page Splitter & Slicer** | ✂️ **PageSlicer** | Divide PDFs into single pages or slice out specific start-end intervals | PDF (ZIP / single pages) |
| 3. **Page Organizer & Numbers** | 🔄 **PageForge** | Rotate pages (90°/180°/270°), reorder sequences, delete pages, and stamp dynamic headers/footers | PDF |
| 4. **Security & Watermarking** | 🔐 **GuardPDF** | 128-bit AES password encryption, permissions, custom text/logo watermarking, & privacy metadata scrubbing | PDF |
| 5. **High-Res PDF Rasterizer** | 🖼️ **PixelRender** | Export all PDF pages into images at selectable DPI resolutions (72, 100, 150, 200, 300 DPI) | PNG, JPEG, WEBP, TIFF (ZIP archive) |
| 6. **Visual PDF Comparator** | ⚖️ **DiffVision** | Compare two document versions side-by-side with pixel-level diff overlays and change metrics | PDF vs PDF (ZIP diff reports) |
| 7. **OCR & Text Extraction** | 🔍 **TextScope** | Extract digital text or run OCR on scanned pages with reading telemetry; export to Markdown & TXT | PDF → MD, TXT |
| 8. **Audiobook Voice Reader** | 🎧 **AudioDoc** | Synthesize natural voice audiobooks from PDF text with multiple accents and speeds | PDF → MP3 |
| 9. **Smart File Compressor** | 🗜️ **OptiCompress** | Compress PDFs and images to exact target KB/MB sizes or visual quality sliders | PDF, JPEG, PNG, WEBP, TIFF, BMP |
| 10. **LaTeX & Math Studio** | 📝 **TeXPublish** | Compile LaTeX to Word & PDF, render math formulas to 300 DPI PNG, and validate BibTeX | `.tex` / text → DOCX, PDF, PNG |

---

## 🌟 Key Features

### 📑 1. OmniMerge: Universal Multi-File Joiner & Synthesizer
* **Universal File Support**: Upload and join **PDFs, JPEGs, PNGs, WEBPs, BMPs, and TIFFs** in any sequence.
* **Incremental Batch Uploading**: Select files, then click **➕ Add More Files** at any time to append additional documents without losing existing items.
* **Flexible Extraction & Export Formats**:
  - 📄 **Consolidated PDF (`.pdf`)**: Unified multi-page document with automatic Table of Contents bookmarks.
  - 🖼️ **Lossless Image Package (`.zip`)**: Individual high-resolution PNG images of all merged pages.
  - 🖼️ **Optimized JPEG Package (`.zip`)**: Compressed JPEG images of all pages.
  - 📑 **Multi-Page TIFF (`.tiff`)**: Single unified multi-page TIFF file.
* **Interactive Document Queue**: Move files up (⬆️) or down (⬇️) or reverse order to set the exact merge sequence.

### ✂️ 2. PageSlicer: PDF Page Splitter & Range Extractor
* **Divide into Single Pages**: Automatically split a multi-page PDF into individual 1-page PDF files packaged in a single `.zip` file or available for individual download.
* **Extract Page Range**: Select custom start and end boundaries to extract a trimmed PDF.

### 🔄 3. PageForge: PDF Page Manipulator & Dynamic Numbering
* **Visual Page Rotation**: Rotate all pages, odd pages, even pages, or specific pages by 90°, 180°, or 270°.
* **Reorder & Discard**: Customize page sequences (e.g. `1, 3, 2, 4-8`) or drop unwanted/blank sheets.
* **Dynamic Header/Footer Stamping**: Stamp `Page {page} of {total}` at Bottom Center, Bottom Right, Top Center, etc., with font size and margin controls.

### 🔐 4. GuardPDF: Security, Watermark & Privacy Suite
* **Password Encryption**: Set User passwords (required to view) and Owner passwords with printing and copying permissions.
* **Decryption**: Unlock protected PDFs to save clean copies.
* **Custom Watermarking**: Overlay text stamps (e.g., `"CONFIDENTIAL"`, custom opacity, rotation angle, font color) or PNG logos.
* **Metadata Privacy Scrubbing**: Inspect document metadata (Author, Producer, Creation Date) or wipe all metadata clean before public release.

### 🖼️ 5. PixelRender: High-Res PDF to Images
* **Configurable DPI**: 72 DPI (Web), 150 DPI (Screens), 300 DPI (High-Resolution Print).
* **Multiple Output Formats**: PNG, JPEG, WebP, and TIFF with gallery preview and bulk ZIP downloads.

### ⚖️ 6. DiffVision: Visual PDF Comparator
* **Side-by-Side Comparison**: Upload Version 1 and Version 2 of a PDF to view changes.
* **Visual Difference Overlays**: Automatically generates 3-panel composites `[ Doc A | Visual Diff Highlight | Doc B ]` with changed pixels marked in vibrant magenta/red.
* **Quantitative Telemetry**: Displays overall document match percentage and changed pixel count.

### 🔍 7. TextScope: Text, Table & OCR Extraction Studio
* **Native Digital Extraction**: Fast text extraction via `pypdf` with word count, character count, and estimated reading time.
* **OCR Scanned Document Engine**: Optical character recognition powered by Tesseract / `pytesseract`.
* **Export Options**: Download as structured Markdown (`.md`) or plain text (`.txt`).

### 🎧 8. AudioDoc: PDF Audiobook Voice Reader
* **Voice Narration**: Convert document text into spoken audiobooks using `gTTS`.
* **Accents & Pace**: Select US English, British English, Australian English, or Indian English with normal or slower speaking speeds.
* **In-Browser Audio Player**: Listen directly in the app or download the `.mp3` file.

### 🗜️ 9. OptiCompress: Universal File Compressor
* **Dual Control Modes**: Optimize by visual quality percentage (5% – 95%) or enforce a strict target file size in KB or MB.
* **Format Conversion**: Convert images to modern WebP or standard JPEG for additional size reduction.
* **Side-by-Side Comparison**: Visual comparison and compression percentage metrics.

### 📝 10. TeXPublish: LaTeX Document & Math Studio
* **LaTeX to DOCX & PDF**: High fidelity conversion via Pandoc and `docx2pdf`.
* **Syntax Validation**: Automatic detection of unbalanced braces `{}` and environment mismatches (`\begin` / `\end{}`).
* **🧮 Math Formula Studio**: Rich catalog of math templates (Calculus, Linear Algebra, Physics, Probability) with live KaTeX rendering and 300 DPI transparent PNG exports.
* **📚 BibTeX Assistant**: Syntax validator, missing standard field warnings, and clean code beautification.

---

## 🛠️ Technology Stack

| Technology | Purpose |
| :--- | :--- |
| **Python 3** | Core backend processing engine |
| **Streamlit** | Modern reactive web application UI with constellation design |
| **pypdf** | PDF merging, page splitting, rotation, reordering, encryption, & metadata |
| **reportlab** | Vector watermark stamping, header/footer page numbering |
| **Pillow** | Image processing, alpha blending, format conversion |
| **pypdfium2** | High-fidelity rendering of PDF pages to raster images (PNG/JPEG/TIFF) |
| **gTTS** | Text-to-speech audio narration (MP3) |
| **matplotlib** | 300 DPI LaTeX mathematical formula rendering |
| **pytesseract** | Optical Character Recognition (OCR) for scanned PDFs |
| **pypandoc / Pandoc** | LaTeX to DOCX compilation |
| **docx2pdf** | Word DOCX to PDF compilation |

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/latexToWord-pdf.git
cd latexToWord-pdf
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Optional External Tools
* **Pandoc**: Required for compiling LaTeX to DOCX ([https://pandoc.org](https://pandoc.org))
* **Tesseract OCR**: Required for scanned PDF text extraction ([https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract))

---

## 💻 Running the Application

### Option A: Next.js + FastAPI Modern React Stack (Recommended)

1. **Start the FastAPI Backend Server** (Port 8000):
```bash
python server.py
# or: uvicorn server:app --reload --port 8000
```

2. **Start the Next.js React Frontend** (Port 3000):
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to experience the interactive UI with `PatternWaves`, `MicroSlats`, and `FlexCarousel`.

---

### Option B: Streamlit Web Application

Launch the classic all-in-one Streamlit interface:
```bash
streamlit run app.py
```
The application will open in your default browser at [http://localhost:8501](http://localhost:8501).

---

## 👤 Author
Siddhartha Kuchana
