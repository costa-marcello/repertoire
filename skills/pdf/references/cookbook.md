# PDF Cookbook -- Python and CLI Patterns

## Contents

1. [Text Extraction](#text-extraction)
2. [Table Extraction](#table-extraction)
3. [OCR for Scanned PDFs](#ocr-for-scanned-pdfs)
4. [Merge PDFs](#merge-pdfs)
5. [Split PDF](#split-pdf)
6. [Rotate Pages](#rotate-pages)
7. [Extract Metadata](#extract-metadata)
8. [Add Watermark](#add-watermark)
9. [Password Protection](#password-protection)
10. [Extract Images](#extract-images)
11. [Create PDF with reportlab](#create-pdf-with-reportlab)
12. [CLI Tools Quick Reference](#cli-tools-quick-reference)

Quick-reference code patterns for common PDF operations. Use `advanced-features.md` for pypdfium2, JavaScript, and advanced CLI.

---

## Text Extraction

### pdfplumber (recommended)

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

### pdftotext CLI (fastest for plain text)

```bash
pdftotext input.pdf output.txt
pdftotext -layout input.pdf output.txt       # preserve layout
pdftotext -f 1 -l 5 input.pdf output.txt     # pages 1-5
```

---

## Table Extraction

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table and len(table) > 1:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

if all_tables:
    combined = pd.concat(all_tables, ignore_index=True)
    combined.to_excel("extracted_tables.xlsx", index=False)
```

---

## OCR for Scanned PDFs

```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path("scanned.pdf", dpi=300)
text = ""
for i, image in enumerate(images):
    page_text = pytesseract.image_to_string(image)
    text += f"--- Page {i+1} ---\n{page_text}\n\n"
```

**Requirements:** `pip install pytesseract pdf2image` plus system poppler (`brew install poppler` on macOS).

---

## Merge PDFs

```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

---

## Split PDF

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

---

## Rotate Pages

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
page = reader.pages[0]
page.rotate(90)  # degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

---

## Extract Metadata

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Pages: {len(reader.pages)}")
```

---

## Add Watermark

```python
from pypdf import PdfReader, PdfWriter

watermark = PdfReader("watermark.pdf").pages[0]
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

---

## Password Protection

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)

writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

---

## Extract Images

```bash
# Using pdfimages (poppler-utils) -- fastest method
pdfimages -j input.pdf output_prefix
# Extracts as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

---

## Create PDF with reportlab

### Simple (Canvas)

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter
c.drawString(100, height - 100, "Hello World!")
c.line(100, height - 120, 400, height - 120)
c.save()
```

### Complex (Platypus)

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("Report Title", styles['Title']))
story.append(Spacer(1, 12))
story.append(Paragraph("Body content here. " * 20, styles['Normal']))
story.append(PageBreak())
story.append(Paragraph("Page 2", styles['Heading1']))

doc.build(story)
```

---

## CLI Tools Quick Reference

### qpdf

```bash
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf           # merge
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf                     # split
qpdf input.pdf output.pdf --rotate=+90:1                         # rotate page 1
qpdf --password=secret --decrypt encrypted.pdf decrypted.pdf     # decrypt
qpdf --linearize input.pdf optimized.pdf                         # optimise for web
```

### pdftk

```bash
pdftk file1.pdf file2.pdf cat output merged.pdf     # merge
pdftk input.pdf burst                                # split into pages
pdftk input.pdf rotate 1east output rotated.pdf      # rotate
```
