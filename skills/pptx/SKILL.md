---
name: pptx
description: "Creates, edits, and analyses PowerPoint presentations with layouts, speaker notes, and design elements. Use when working with .pptx files, creating presentations from topics, modifying slides, or extracting content. Triggers: 'create presentation from topic', 'slide deck from document', 'powerpoint from scratch'."
license: MIT
---

# PPTX creation, editing, and analysis

<context>
A .pptx file is a ZIP archive containing XML files and other resources. This skill provides different workflows for creating, editing, and analysing presentations.
</context>

## Creating from Topic (Content-First)

For generating complete decks from a topic, document, or brief, use the content-first workflow built on the **Pyramid Principle** (conclusion, reasons, evidence):

1. **Intake**: Use questionnaire at `references/content-workflow/INTAKE.md`
2. **Follow 9-stage workflow**: `references/content-workflow/WORKFLOW.md`
3. **Score with rubric** (must reach 75+): `references/content-workflow/RUBRIC.md`

### Content-First Reference Files

| File | Purpose |
|------|---------|
| `INTAKE.md` | Questionnaire to gather requirements |
| `WORKFLOW.md` | 9-stage content generation process |
| `TEMPLATES.md` | Slide layout templates |
| `VIS-GUIDE.md` | Chart and visualisation selection |
| `STYLE-GUIDE.md` | WCAG 2.1 AA compliance, typography |
| `RUBRIC.md` | Quality scoring (10 dimensions, 75+ to pass) |
| `CHECKLIST.md` | Pre-delivery verification |
| `ORCHESTRATION_OVERVIEW.md` | High-level orchestration map across the 9 stages |
| `ORCHESTRATION_PPTX.md` | Slide-build orchestration (HTML, layout, packaging) |
| `ORCHESTRATION_DATA_CHARTS.md` | Chart and data-visual orchestration (chartkit) |
| `EXAMPLES.md` | Sample presentations |

### Chart Generation

For data-driven charts, use chartkit:

<example>
```bash
python scripts/chartkit.py \
  --data data.csv \
  --type line \
  --x date \
  --y sales profit \
  --out output/assets \
  --filename kpi_trend.png \
  --title "Monthly KPIs"
```
Creates: `kpi_trend.png` line chart in output/assets
</example>

Supported chart types: `line`, `area`, `bar`, `barh`, `scatter`, `hist`, `waterfall`

## Reading and analysing content

### Text extraction

To read text contents, convert the document to markdown:

<example>
```bash
python -m markitdown path-to-file.pptx
```
Outputs: Markdown text content from all slides
</example>

### Raw XML access

Raw XML access is needed for: comments, speaker notes, slide layouts, animations, design elements, and complex formatting. Unpack the presentation and read its raw XML contents.

<example>
```bash
python ooxml/scripts/unpack.py presentation.pptx unpacked/
```
Creates: Directory with extracted XML files and media
</example>

**Note**: The unpack.py script is at `skills/pptx/ooxml/scripts/unpack.py` relative to the project root. If the script is not at this path, use `find . -name "unpack.py"` to locate it.

<context>
#### Key file structures
* `ppt/presentation.xml` - Main presentation metadata and slide references
* `ppt/slides/slide{N}.xml` - Individual slide contents (slide1.xml, slide2.xml, etc.)
* `ppt/notesSlides/notesSlide{N}.xml` - Speaker notes for each slide
* `ppt/comments/modernComment_*.xml` - Comments for specific slides
* `ppt/slideLayouts/` - Layout templates for slides
* `ppt/slideMasters/` - Master slide templates
* `ppt/theme/` - Theme and styling information
* `ppt/media/` - Images and other media files
</context>

#### Typography and colour extraction

**When given an example design to emulate**: Analyse the presentation's typography and colours first:

1. **Read theme file**: Check `ppt/theme/theme1.xml` for colours (`<a:clrScheme>`) and fonts (`<a:fontScheme>`)
2. **Sample slide content**: Examine `ppt/slides/slide1.xml` for actual font usage (`<a:rPr>`) and colours
3. **Search for patterns**: Use grep to find colour (`<a:solidFill>`, `<a:srgbClr>`) and font references across all XML files

## Creating a new presentation without a template

<instructions>

Use the **html2pptx** workflow to convert HTML slides to PowerPoint with accurate positioning.

### Design Approach

Before creating any presentation, analyse the content and choose appropriate design elements:

1. **Identify the subject matter**: What is this presentation about? What tone, industry, or mood does it suggest?
2. **Check for branding**: If the user mentions a company or organisation, use their brand colours and identity
3. **Match palette to content**: Select colours that reflect the subject
4. **State your approach**: Explain your design choices before writing code

**Requirements**:
- State your content-informed design approach before writing code
- Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
- Create clear visual hierarchy through size, weight, and colour
- Check readability: WCAG 2.1 AA contrast (>= 4.5:1 for body, >= 3:1 for large text), body text >= 18pt, headings >= 28pt, clean alignment
- Repeat patterns, spacing, and visual language across slides

#### Design Resources

For colour palettes and visual design elements, read:
- `references/color-palettes.md` - 18 curated colour schemes
- `references/design-elements.md` - Geometric patterns, typography, layouts

### Layout Tips

**When creating slides with charts or tables:**
- **Two-column layout (preferred)**: Use a header spanning the full width, then two columns below -- text/bullets in one column and the featured content in the other. Use flexbox with unequal column widths (e.g., 40%/60% split)
- **Full-slide layout**: Let the featured content take up the entire slide for maximum readability
- **Do not vertically stack**: Do not place charts/tables below text in a single column -- this causes poor readability and layout issues

### Workflow

1. Read [`references/html2pptx-guide.md`](references/html2pptx-guide.md) completely from start to finish before proceeding
2. Create an HTML file for each slide with proper dimensions (e.g., 720pt x 405pt for 16:9)
   - Use `<p>`, `<h1>`-`<h6>`, `<ul>`, `<ol>` for all text content
   - Use `class="placeholder"` for areas where charts/tables will be added (render with grey background for visibility)
   - Rasterise gradients and icons as PNG images first using Sharp, then reference in HTML
   - For slides with charts/tables/images, use either full-slide layout or two-column layout
3. Create and run a JavaScript file using the [`html2pptx.js`](scripts/html2pptx.js) library to convert HTML slides to PowerPoint and save the presentation
   - Use the `html2pptx()` function to process each HTML file
   - Add charts and tables to placeholder areas using PptxGenJS API
   - Save the presentation using `pptx.writeFile()`
4. **Visual validation**: Generate thumbnails and inspect for layout issues
   <example>
   ```bash
   python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4
   ```
   Creates: `workspace/thumbnails.jpg` grid for visual validation
   </example>
   - Read and examine the thumbnail image for:
     - **Text cutoff**: Text being cut off by header bars, shapes, or slide edges
     - **Text overlap**: Text overlapping with other text or shapes
     - **Positioning issues**: Content too close to slide boundaries or other elements
     - **Contrast issues**: Insufficient contrast between text and backgrounds
   - If issues found, adjust HTML margins/spacing/colours and regenerate the presentation
   - Repeat until all slides are visually correct

</instructions>

## Editing an existing presentation

<instructions>

Work with the raw Office Open XML (OOXML) format: unpack the .pptx file, edit the XML content, and repack it.

### Workflow

1. Read [`references/ooxml-reference.md`](references/ooxml-reference.md) (~500 lines) completely from start to finish before any editing
2. Unpack the presentation:
   <example>
   ```bash
   python ooxml/scripts/unpack.py presentation.pptx unpacked/
   ```
   </example>
3. Edit the XML files (primarily `ppt/slides/slide{N}.xml` and related files)
4. Validate immediately after each edit:
   <example>
   ```bash
   python ooxml/scripts/validate.py unpacked/ --original presentation.pptx
   ```
   </example>
5. Pack the final presentation:
   <example>
   ```bash
   python ooxml/scripts/pack.py unpacked/ output.pptx
   ```
   </example>

</instructions>

## Creating a presentation using a template

<instructions>

Read [`references/template-workflow.md`](references/template-workflow.md) completely from start to finish. It covers the full 7-step process:

1. Extract template text and create visual thumbnail grid
2. Analyse template and save inventory to a file
3. Create presentation outline based on template inventory
4. Duplicate, reorder, and delete slides using `rearrange.py`
5. Extract all text using `inventory.py`
6. Generate replacement text and save to JSON
7. Apply replacements using `replace.py`

</instructions>

## Creating Thumbnail Grids

<example>
```bash
python scripts/thumbnail.py template.pptx [output_prefix]
```
Creates: `thumbnails.jpg` (or `output_prefix.jpg` if specified)
</example>

**Features**:
- Creates: `thumbnails.jpg` (or `thumbnails-1.jpg`, `thumbnails-2.jpg`, etc. for large decks)
- Default: 5 columns, max 30 slides per grid (5x6)
- Custom prefix: `python scripts/thumbnail.py template.pptx my-grid`
  - Note: The output prefix should include the path if you want output in a specific directory (e.g., `workspace/my-grid`)
- Adjust columns: `--cols 4` (range: 3-6, affects slides per grid)
- Grid limits: 3 cols = 12 slides/grid, 4 cols = 20, 5 cols = 30, 6 cols = 42
- Slides are zero-indexed (Slide 0, Slide 1, etc.)

**Use cases**:
- Template analysis: Quickly understand slide layouts and design patterns
- Content review: Visual overview of entire presentation
- Navigation reference: Find specific slides by their visual appearance
- Quality check: Verify all slides are properly formatted

<example>
```bash
# Basic usage
python scripts/thumbnail.py presentation.pptx

# Combine options: custom name, columns
python scripts/thumbnail.py template.pptx analysis --cols 4
```
</example>

## Converting Slides to Individual Images

For cases where you need individual slide images rather than a grid:

<example>
```bash
# Step 1: Convert PPTX to PDF
soffice --headless --convert-to pdf template.pptx

# Step 2: Convert PDF pages to JPEG images
pdftoppm -jpeg -r 150 template.pdf slide
```
Creates: `slide-1.jpg`, `slide-2.jpg`, etc.
</example>

Options: `-r 150` (DPI), `-jpeg` or `-png` (format), `-f N -l N` (page range)

## Code Style Guidelines

When generating code for PPTX operations, write concise code. Avoid verbose variable names, redundant operations, and unnecessary print statements.

## Dependencies

Required dependencies (should already be installed):

| Package | Install (pip) | Install (npm) | Purpose |
|---------|--------------|---------------|---------|
| markitdown | `pip install "markitdown[pptx]"` | -- | Text extraction from presentations |
| pptxgenjs | -- | `npm install -g pptxgenjs` | Creating presentations via html2pptx |
| playwright | -- | `npm install -g playwright` | HTML rendering in html2pptx |
| react-icons | -- | `npm install -g react-icons react react-dom` | Icons |
| sharp | -- | `npm install -g sharp` | SVG rasterisation and image processing |
| defusedxml | `pip install defusedxml` | -- | Secure XML parsing |
| LibreOffice | System package: `brew install libreoffice` (macOS) or `apt-get install libreoffice` (Linux) | -- | PDF conversion |
| Poppler | System package: `brew install poppler` (macOS) or `apt-get install poppler-utils` (Linux) | -- | PDF to image conversion via pdftoppm |
