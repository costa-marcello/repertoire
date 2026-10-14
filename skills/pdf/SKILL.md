---
name: pdf
description: "Extracts text and tables from PDFs, creates new documents, merges/splits files, fills forms, and converts markdown to PDF. Use when working with PDF files, when the user mentions PDFs, document extraction, form filling, OCR, or markdown-to-PDF conversion."
license: MIT
---

# PDF Processing

<instructions>

## Step 1: Identify the Task

Match the user's request to one workflow. Default to **Extract Text** when unclear.

| Task | Primary Tool | Fallback |
|------|-------------|----------|
| Extract text | pdfplumber | pdftotext CLI |
| Extract tables to DataFrame | pdfplumber + pandas | -- |
| OCR scanned PDFs | pytesseract + pdf2image | -- |
| Create new PDF | reportlab (Platypus for complex, Canvas for simple) | -- |
| Merge/split/rotate | pypdf | qpdf CLI |
| Add watermark | pypdf merge_page() | -- |
| Password protect/decrypt | pypdf encrypt()/qpdf | -- |
| Fill PDF forms | Read `references/forms.md` and follow its steps | -- |
| Markdown to PDF | `python scripts/md_to_pdf.py input.md output.pdf` | -- |
| Batch markdown to PDF | `python scripts/batch_convert.py *.md --output-dir ./pdfs/` | -- |
| Extract images | `pdfimages -j input.pdf output_prefix` (poppler-utils) | pypdfium2 |
| Render pages to images | pypdfium2 | pdftoppm CLI |

## Step 2: Install Dependencies

Check what is available before writing code:

```bash
pip list 2>/dev/null | grep -iE "pypdf|pdfplumber|reportlab|pypdfium2|weasyprint|pytesseract|pdf2image"
which pdftotext qpdf pdftk pdfimages 2>/dev/null
```

Install only what the task needs. Do not install everything.

| Task | Install |
|------|---------|
| Text/table extraction | `pip install pdfplumber` |
| OCR | `pip install pytesseract pdf2image` + system poppler |
| Merge/split/rotate/encrypt | `pip install pypdf` |
| Create PDFs | `pip install reportlab` |
| Render to images | `pip install pypdfium2` |
| Markdown to PDF | `pip install weasyprint markdown` |

## Step 3: Execute the Workflow

Use the code patterns in `references/cookbook.md` for implementation details.
Use `references/advanced-features.md` for pypdfium2, pdf-lib (JS), and advanced CLI operations.

### Validation Checkpoints

Run these checks at each stage:

**After extraction:**
```python
text = page.extract_text()
if not text or len(text.strip()) < 10:
    # PDF may be scanned -- fall back to OCR
    print(f"Page {i+1}: no text found, switching to OCR")
```

**After merge/split:**
```python
result = PdfReader("output.pdf")
print(f"Output has {len(result.pages)} pages")
# Verify page count matches expectation
```

**After form fill:**
Run the validation scripts described in `references/forms.md` before delivering the output.

**After markdown-to-PDF:**
```python
import os
output_size = os.path.getsize("output.pdf")
print(f"Generated PDF: {output_size} bytes")
if output_size < 500:
    print("Warning: PDF seems too small, check for conversion errors")
```

## Step 4: Deliver Results

- Report what was done: page count, text length, file size.
- If OCR was used, warn the user about potential accuracy issues.
- For form fills, note which fields were populated and which were skipped.

</instructions>

<examples>

<example>
**User:** "Extract all the tables from this PDF and save as Excel"

**Steps:**
1. Install pdfplumber and pandas.
2. Extract tables from each page.
3. Validate each table has rows before saving.
4. Combine and export to Excel.

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for table in tables:
            if table and len(table) > 1:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)
                print(f"Page {i+1}: extracted table with {len(df)} rows")
    if all_tables:
        combined = pd.concat(all_tables, ignore_index=True)
        combined.to_excel("tables.xlsx", index=False)
        print(f"Saved {len(combined)} total rows to tables.xlsx")
    else:
        print("No tables found in this PDF")
```
</example>

<example>
**User:** "Merge these three PDFs into one"

```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)
    print(f"Added {len(reader.pages)} pages from {pdf_file}")

with open("merged.pdf", "wb") as output:
    writer.write(output)

# Verify
result = PdfReader("merged.pdf")
print(f"Merged PDF has {len(result.pages)} pages")
```
</example>

<example>
**User:** "This PDF is scanned, I need the text"

```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path("scanned.pdf", dpi=300)
text = ""
for i, image in enumerate(images):
    page_text = pytesseract.image_to_string(image)
    text += page_text
    print(f"Page {i+1}: extracted {len(page_text)} characters")

with open("extracted.txt", "w") as f:
    f.write(text)
print(f"Total: {len(text)} characters. Review for OCR errors.")
```
</example>

<example>
**User:** "Convert this markdown file to PDF"

```bash
# macOS may need: export DYLD_LIBRARY_PATH=$(brew --prefix)/lib
python scripts/md_to_pdf.py report.md report.pdf
```

Features: A4 pages, proper margins, table/code support, Chinese font fallback.
For batch conversion: `python scripts/batch_convert.py *.md --output-dir ./pdfs/`
</example>

<example>
**User:** "Fill out this PDF form with my details"

Follow the complete workflow in `references/forms.md`. Summary:
1. Check if the PDF has fillable fields: `python scripts/check_fillable_fields.py form.pdf`
2. If fillable: extract field info, create values JSON, run fill script.
3. If not fillable: convert to images, identify fields visually, create bounding boxes, validate, fill with annotations.
</example>

</examples>

## References

| File | Purpose |
|------|---------|
| `references/cookbook.md` | Python and CLI code patterns for all PDF operations |
| `references/advanced-features.md` | pypdfium2, pdf-lib (JS), advanced CLI, performance tips |
| `references/forms.md` | Complete form-filling workflow (fillable and non-fillable PDFs) |

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/md_to_pdf.py` | Markdown to PDF with Chinese font support | `python scripts/md_to_pdf.py input.md [output.pdf]` |
| `scripts/batch_convert.py` | Batch markdown to PDF | `python scripts/batch_convert.py *.md [--output-dir dir]` |
| `scripts/check_fillable_fields.py` | Check if PDF has fillable form fields | `python scripts/check_fillable_fields.py input.pdf` |
| `scripts/extract_form_field_info.py` | Extract form field metadata to JSON | `python scripts/extract_form_field_info.py input.pdf output.json` |
| `scripts/fill_fillable_fields.py` | Fill fillable PDF form fields | `python scripts/fill_fillable_fields.py input.pdf values.json output.pdf` |
| `scripts/fill_pdf_form_with_annotations.py` | Fill non-fillable PDFs with text annotations | `python scripts/fill_pdf_form_with_annotations.py input.pdf fields.json output.pdf` |
| `scripts/convert_pdf_to_images.py` | Convert PDF pages to PNG images | `python scripts/convert_pdf_to_images.py input.pdf output_dir` |
| `scripts/create_validation_image.py` | Create bounding box validation images | `python scripts/create_validation_image.py page_num fields.json input.png output.png` |
| `scripts/check_bounding_boxes.py` | Validate bounding boxes do not overlap | `python scripts/check_bounding_boxes.py fields.json` |
