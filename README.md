# LaTeX to Document Converter

A web-based application that converts LaTeX content into editable Microsoft Word documents and optionally exports them as PDF files.

## Overview

LaTeX is widely used for creating academic papers, technical reports, research documents, and professional publications. However, many institutions and organizations require documents in Microsoft Word format for editing, collaboration, or submission.

This project provides a simple solution by allowing users to enter LaTeX code directly or upload `.tex` files and generate Word documents with minimal effort. Users can also convert the generated Word document into PDF format.

## Features

### Input Options

* Paste LaTeX code directly into the application
* Upload `.tex` files

### Validation

* Detect unbalanced braces
* Detect LaTeX environment mismatches
* Display validation warnings before conversion

### Document Generation

* Convert LaTeX content into editable `.docx` files
* Download generated Word documents instantly

### PDF Export

* Convert generated Word documents into PDF format
* Download PDF files directly from the application

### User Interface

* Clean and intuitive web interface
* Fast document generation workflow
* Easy-to-use conversion process

## Technology Stack

| Technology | Purpose                   |
| ---------- | ------------------------- |
| Python     | Backend Logic             |
| Streamlit  | Web Application Framework |
| Pandoc     | LaTeX to DOCX Conversion  |
| pypandoc   | Python Wrapper for Pandoc |
| docx2pdf   | DOCX to PDF Conversion    |

## Project Structure

```text
latexCodeConverter/
│
├── app.py
├── converter.py
├── validator.py
├── requirements.txt
└── README.md
```

## Installation

### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/latexToWord-pdf.git
cd latexToWord-pdf
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Pandoc

Download and install Pandoc:

https://pandoc.org/installing.html

Verify installation:

```bash
pandoc --version
```

### Microsoft Word Requirement

PDF conversion uses the `docx2pdf` library and requires Microsoft Word to be installed on Windows.

## Running the Application

```bash
streamlit run app.py
```

The application will start locally and open in your default web browser.

## Usage

### Method 1: Paste LaTeX

1. Select **Paste Text**
2. Enter LaTeX content
3. Click **Generate DOCX**
4. Download the generated Word document

### Method 2: Upload a File

1. Select **Upload File**
2. Upload a `.tex` file
3. Click **Generate DOCX**
4. Download the generated document

### Optional PDF Conversion

1. Generate a DOCX file
2. Click **Convert DOCX to PDF**
3. Download the PDF document

## Future Enhancements

* Live LaTeX rendering
* Mathematical equation preview
* AI-assisted LaTeX error correction
* Batch document conversion
* HTML export support
* Conversion history
* User authentication
* Cloud deployment

## Motivation

The objective of this project is to simplify document conversion workflows for students, researchers, educators, and professionals who regularly work with LaTeX documents but need editable Word or PDF versions for sharing and collaboration.

## Author

Siddhartha Kuchana

## License

This project is licensed under the MIT License.
