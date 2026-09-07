# LaTeX & PDF Processing Suite

A comprehensive web-based application that converts LaTeX content into editable Microsoft Word (`.docx`) documents, exports them to PDF, divides multi-page PDF documents into single-page PDF files, and extracts custom page ranges ("from page X to page Y").

---

## Overview

LaTeX is widely used for creating academic papers, technical reports, research documents, and professional publications. However, working with PDFs and Word documents often requires specialized manipulation tools.

This suite provides a unified solution:
1. **LaTeX to Word & PDF Conversion**: Convert `.tex` code or files to Word (`.docx`) and PDF.
2. **PDF Page Splitter**: Split any multi-page PDF into individual single-page PDF files (packaged as a `.zip` file for bulk download as well as individual downloads).
3. **PDF Page Range Extractor**: Extract specific page ranges (e.g. from page 2 to page 5) from any uploaded or generated PDF.

---

## Key Features

### 📝 LaTeX Converter Features
* **Input Methods**: Direct text paste or `.tex` file upload.
* **Syntax Validation**: Automatic detection of unbalanced braces `{}` and environment mismatches (`\begin` / `\end`).
* **Document Generation**: Quick conversion to `.docx` format via Pandoc.
* **PDF Export**: One-click DOCX-to-PDF conversion via `docx2pdf`.

### ✂️ PDF Page Splitting & Range Extraction Features
* **Divide into Single Pages**: Automatically split a multi-page PDF into individual 1-page PDF files. Download all single-page PDFs in a single `.zip` file or download individual pages.
* **Extract Page Range**: Select a custom start page ("From Page X") and end page ("To Page Y") to extract a trimmed PDF.
* **Direct Upload Support**: Split or extract pages from any external `.pdf` file.
* **Integrated Workflow**: Operates directly on LaTeX-generated PDFs without requiring extra file uploads.

---

## Technology Stack

| Technology | Purpose |
| ---------- | ------- |
| Python | Backend logic & processing |
| Streamlit | Modern web application framework |
| pypdf | PDF page counting, single-page splitting, & page extraction |
| Pandoc | LaTeX to DOCX conversion |
| pypandoc | Python wrapper for Pandoc |
| docx2pdf | DOCX to PDF conversion |

---

## Project Structure

```text
latexToWord-Pdf/
│
├── app.py           # Streamlit web application & tabbed UI
├── converter.py     # LaTeX to DOCX & DOCX to PDF conversion logic
├── pdf_splitter.py  # PDF page counting, single-page splitting & range extraction
├── validator.py     # LaTeX syntax validation rules
├── requirements.txt # Python dependencies (streamlit, pypandoc, docx2pdf, pypdf)
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

### 3. Install Pandoc
Download and install Pandoc for LaTeX conversion support:
[https://pandoc.org/installing.html](https://pandoc.org/installing.html)

Verify Pandoc installation:
```bash
pandoc --version
```

### 4. Microsoft Word Requirement (For DOCX to PDF)
PDF conversion from `.docx` uses `docx2pdf` and requires Microsoft Word installed on Windows. (Note: PDF Splitting and Range Extraction functions use `pypdf` and work standalone on all platforms without Microsoft Word).

---

## Running the Application

Launch the Streamlit web application:
```bash
streamlit run app.py
```

The application will open in your default browser (default: `http://localhost:8501`).

---

## Usage Guide

### Tab 1: 📝 LaTeX to Document Converter
1. Select **Paste Text** or **Upload File** (`.tex`).
2. Click **Generate DOCX** to create a `.docx` Word document.
3. Download the `.docx` file or click **Convert DOCX to PDF**.
4. Once the PDF is generated, use the inline PDF tools to split it into single pages or extract page ranges.

### Tab 2: ✂️ PDF Page Splitter & Extractor
1. Upload any multi-page PDF document.
2. View total page count statistics.
3. Choose an operation:
   - **Divide PDF into Single Pages**: Click **Split PDF into Single Pages** to generate individual 1-page PDFs and download the `.zip` archive or individual pages.
   - **Extract Specific Page Range**: Enter **From Page** and **To Page** numbers, then click **Extract Pages** to download the custom PDF snippet.

---

## Author
Siddhartha Kuchana
