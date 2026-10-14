---
name: docx
description: "Creates, edits, and analyzes Word documents with tracked changes, comments, and formatting preservation. Use when working with .docx files for document creation, modification, redlining, or text extraction."
license: MIT
---

# DOCX Creation, Editing, and Analysis

Read the relevant reference file completely before starting work:
- **Creating** a new document: read `references/docx-js.md`
- **Editing** an existing document: read `references/ooxml.md`

## Workflow Decision Tree

| Task | Workflow | Reference |
|------|----------|-----------|
| Read/analyse content | Text extraction (pandoc) or Raw XML | None needed |
| Create new document | docx-js (JavaScript) | `references/docx-js.md` |
| Edit your own doc (simple) | OOXML editing | `references/ooxml.md` |
| Edit someone else's doc | Redlining workflow (recommended) | `references/ooxml.md` |
| Legal/business/government | Redlining workflow (required) | `references/ooxml.md` |

**If unsure who owns the document, default to Redlining.** OOXML editing writes changes directly and is only safe on your own drafts where tracked changes are unwanted.

---

<instructions>

## Reading and Analysing Content

**Default to text extraction.** Use raw XML only when you need comments, complex formatting, document structure, embedded media, or metadata.

### Text Extraction (Default)

Convert the document to markdown with pandoc:

```bash
pandoc --track-changes=all path-to-file.docx -o output.md
# Options: --track-changes=accept (default) / reject / all
```

Default to `--track-changes=all` to preserve revision history. Use `accept` only when the user wants clean text without markup.

### Raw XML Access

Use raw XML when you need: comments, complex formatting, document structure, embedded media, or metadata.

```bash
python ooxml/scripts/unpack.py <office_file> <output_directory>
```

Key files after unpacking:
- `word/document.xml` -- main document body
- `word/comments.xml` -- comments referenced in document.xml
- `word/media/` -- embedded images and media
- Tracked changes use `<w:ins>` (insertions) and `<w:del>` (deletions) tags

</instructions>

---

<instructions>

## Creating a New Word Document

Use **docx-js** (JavaScript/TypeScript) for new documents.

1. Read `references/docx-js.md` completely
2. Write a script using Document, Paragraph, TextRun components
3. Export with `Packer.toBuffer()`
4. Verify the output opens in Word/LibreOffice without errors

<example>
**Task:** User says "Create a one-page memo with a title and two bullet points"

**Action:**
1. Read `references/docx-js.md`
2. Create script with Document, Paragraph, TextRun, numbering config for bullets
3. Run: `node memo.js`
4. Verify: `soffice --headless --convert-to pdf memo.docx && pdftoppm -jpeg -r 150 memo.pdf preview`
</example>

</instructions>

---

<instructions>

## Editing an Existing Word Document

Use the **Document library** (Python) from `scripts/document.py`. It handles infrastructure setup automatically (people.xml, RSIDs, settings.xml, comments, relationships, content types).

### Standard Editing Workflow

1. Read `references/ooxml.md` completely (focus on "Document Library" section)
2. Unpack: `python ooxml/scripts/unpack.py <file.docx> <output_dir>`
3. Edit using Document library methods
4. Pack: `python ooxml/scripts/pack.py <output_dir> <result.docx>`
5. Verify: convert to markdown and check output

<example>
**Task:** User says "Change '30 days' to '60 days' in this contract"

**Action:**
```python
from scripts.document import Document
doc = Document('unpacked', track_revisions=True)
node = doc["word/document.xml"].get_node(tag="w:r", contains="30 days")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = (
    f'<w:r w:rsidR="ORIGINAL">{rpr}<w:t>within </w:t></w:r>'
    f'<w:del><w:r>{rpr}<w:delText>30</w:delText></w:r></w:del>'
    f'<w:ins><w:r>{rpr}<w:t>60</w:t></w:r></w:ins>'
    f'<w:r w:rsidR="ORIGINAL">{rpr}<w:t> days</w:t></w:r>'
)
doc["word/document.xml"].replace_node(node, replacement)
doc.save()
```
</example>

</instructions>

---

<instructions>

## Redlining Workflow (Document Review with Tracked Changes)

Plan tracked changes in markdown before implementing in OOXML. Group related changes into batches of 3-10 for manageable debugging.

**Principle: Minimal, Precise Edits.** Only mark text that actually changes. Repeating unchanged text makes edits harder to review. Break replacements into: [unchanged text] + [deletion] + [insertion] + [unchanged text]. Preserve the original run's RSID for unchanged text.

### Step-by-Step

1. **Get markdown representation:**
   ```bash
   pandoc --track-changes=all path-to-file.docx -o current.md
   ```

2. **Identify and group changes.** Organise into batches by section, type, or proximity. Use these location methods for finding text in XML:
   - Section/heading numbers (e.g., "Section 3.2")
   - Grep patterns with unique surrounding text
   - Document structure (e.g., "first paragraph after Heading 2")
   - Do NOT use markdown line numbers -- they do not map to XML structure

3. **Read documentation and unpack:**
   - Read `references/ooxml.md` -- focus on "Document Library" and "Tracked Change Patterns"
   - Unpack: `python ooxml/scripts/unpack.py <file.docx> <dir>`
   - Note the suggested RSID from unpack script

4. **Implement changes in batches.** For each batch:
   - Grep `word/document.xml` to verify current text and line numbers (they shift after each script)
   - Write a script using `get_node` to find nodes, then `replace_node`, `suggest_deletion`, or `insert_after`
   - Run the script and verify with `doc.save()`

5. **Pack the document:**
   ```bash
   python ooxml/scripts/pack.py unpacked reviewed-document.docx
   ```

6. **Final verification:**
   ```bash
   pandoc --track-changes=all reviewed-document.docx -o verification.md
   grep "original phrase" verification.md   # Should NOT match
   grep "replacement phrase" verification.md # Should match
   ```

<example>
**Task:** User says "Review this NDA and suggest changing the non-compete period from 2 years to 1 year, and update the jurisdiction from New York to Delaware"

**Batch plan:**
- Batch 1 (Term changes): "2 years" to "1 year" in Section 5
- Batch 2 (Jurisdiction): "New York" to "Delaware" in Section 8

**Per batch:** grep for text, write script, run, verify. After all batches, pack and do final verification.
</example>

### Method Selection Guide

| Scenario | Method |
|----------|--------|
| Change part of regular text | `replace_node()` with `<w:del>`/`<w:ins>` |
| Delete entire run or paragraph | `suggest_deletion()` |
| Reject another author's insertion | `revert_insertion()` (NOT `suggest_deletion()`) |
| Restore another author's deletion | `revert_deletion()` |
| Partially modify another author's change | `replace_node()` with nested `<w:ins>`/`<w:del>` |

</instructions>

---

<instructions>

## Converting Documents to Images

Two-step process for visual analysis:

```bash
# Step 1: DOCX to PDF
soffice --headless --convert-to pdf document.docx

# Step 2: PDF pages to JPEG
pdftoppm -jpeg -r 150 document.pdf page
# Creates page-1.jpg, page-2.jpg, etc.

# For specific pages only:
pdftoppm -jpeg -r 150 -f 2 -l 5 document.pdf page
```

Use `-r 150` for a good quality/size balance. Increase to 300 for print-quality output.

</instructions>

---

## Code Style

Write concise code. Avoid verbose variable names, redundant operations, and unnecessary print statements.

## Dependencies

Install if not available:

| Dependency | Install | Purpose |
|------------|---------|---------|
| pandoc | `brew install pandoc` or `apt-get install pandoc` | Text extraction |
| docx | `npm install -g docx` | Creating new documents |
| LibreOffice | `brew install --cask libreoffice` or `apt-get install libreoffice` | PDF conversion |
| Poppler | `brew install poppler` or `apt-get install poppler-utils` | PDF to images |
| defusedxml | `pip install defusedxml` | Secure XML parsing |

## References

| File | Purpose |
|------|---------|
| `references/docx-js.md` | docx-js API patterns for creating new documents |
| `references/ooxml.md` | OOXML XML patterns, Document library API, tracked changes |
