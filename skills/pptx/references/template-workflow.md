# Template-Based Presentation Workflow

## Contents

1. [Workflow](#workflow)

Create presentations that follow an existing template's design by duplicating, rearranging, and replacing placeholder content.

## Workflow

### Step 1: Extract template text and create visual thumbnail grid

* Extract text: `python -m markitdown template.pptx > template-content.md`
* Read `template-content.md` in full to understand the template contents
* Create thumbnail grids: `python scripts/thumbnail.py template.pptx`
* See the [Creating Thumbnail Grids](#creating-thumbnail-grids) section in SKILL.md for details

### Step 2: Analyse template and save inventory to a file

* **Visual analysis**: Review thumbnail grid(s) to understand slide layouts, design patterns, and visual structure
* Create and save a template inventory file at `template-inventory.md` containing:
  ```markdown
  # Template Inventory Analysis
  **Total Slides: [count]**
  **Slides are 0-indexed (first slide = 0, last slide = count-1)**

  ## [Category Name]
  - Slide 0: [Layout code if available] - Description/purpose
  - Slide 1: [Layout code] - Description/purpose
  - Slide 2: [Layout code] - Description/purpose
  [... EVERY slide must be listed individually with its index ...]
  ```
* **Using the thumbnail grid**: Reference the visual thumbnails to identify:
  - Layout patterns (title slides, content layouts, section dividers)
  - Image placeholder locations and counts
  - Design consistency across slide groups
  - Visual hierarchy and structure
* This inventory file is required for selecting appropriate templates in the next step

### Step 3: Create presentation outline based on template inventory

* Review available templates from step 2
* Choose an intro or title template for the first slide (one of the first templates)
* Choose safe, text-based layouts for the other slides
* **Match layout structure to actual content**:
  - Single-column layouts: Use for unified narrative or single topic
  - Two-column layouts: Use only when you have exactly 2 distinct items/concepts
  - Three-column layouts: Use only when you have exactly 3 distinct items/concepts
  - Image + text layouts: Use only when you have actual images to insert
  - Quote layouts: Use only for actual quotes from people (with attribution), not for emphasis
  - Do not use layouts with more placeholders than you have content
  - If you have 2 items, do not force them into a 3-column layout
  - If you have 4+ items, break into multiple slides or use a list format
* Count your actual content pieces before selecting the layout
* Verify each placeholder in the chosen layout will be filled with meaningful content
* Select one option representing the best layout for each content section
* Save `outline.md` with content and template mapping that leverages available designs

<example>
Template mapping:
```
# Template slides to use (0-based indexing)
# WARNING: Verify indices are within range! Template with 73 slides has indices 0-72
# Mapping: slide numbers from outline -> template slide indices
template_mapping = [
    0,   # Use slide 0 (Title/Cover)
    34,  # Use slide 34 (B1: Title and body)
    34,  # Use slide 34 again (duplicate for second B1)
    50,  # Use slide 50 (E1: Quote)
    54,  # Use slide 54 (F2: Closing + Text)
]
```
</example>

### Step 4: Duplicate, reorder, and delete slides using `rearrange.py`

<example>
```bash
python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52
```
Creates: `working.pptx` with slides 0, 34, 34 (duplicated), 50, 52 from template
</example>

* The script handles duplicating repeated slides, deleting unused slides, and reordering automatically
* Slide indices are 0-based (first slide is 0, second is 1, etc.)
* The same slide index can appear multiple times to duplicate that slide

### Step 5: Extract all text using the `inventory.py` script

<example>
```bash
python scripts/inventory.py working.pptx text-inventory.json
```
Creates: `text-inventory.json` with all text shapes, positions, and formatting
</example>

* Read text-inventory.json in full to understand all shapes and their properties

* The inventory JSON structure:
   ```json
     {
       "slide-0": {
         "shape-0": {
           "placeholder_type": "TITLE",  // or null for non-placeholders
           "left": 1.5,                  // position in inches
           "top": 2.0,
           "width": 7.5,
           "height": 1.2,
           "paragraphs": [
             {
               "text": "Paragraph text",
               // Optional properties (only included when non-default):
               "bullet": true,           // explicit bullet detected
               "level": 0,               // only included when bullet is true
               "alignment": "CENTER",    // CENTER, RIGHT (not LEFT)
               "space_before": 10.0,     // space before paragraph in points
               "space_after": 6.0,       // space after paragraph in points
               "line_spacing": 22.4,     // line spacing in points
               "font_name": "Arial",     // from first run
               "font_size": 14.0,        // in points
               "bold": true,
               "italic": false,
               "underline": false,
               "color": "FF0000"         // RGB color
             }
           ]
         }
       }
     }
   ```

* Key features:
  - **Slides**: Named as "slide-0", "slide-1", etc.
  - **Shapes**: Ordered by visual position (top-to-bottom, left-to-right) as "shape-0", "shape-1", etc.
  - **Placeholder types**: TITLE, CENTER_TITLE, SUBTITLE, BODY, OBJECT, or null
  - **Default font size**: `default_font_size` in points extracted from layout placeholders (when available)
  - **Slide numbers are filtered**: Shapes with SLIDE_NUMBER placeholder type are automatically excluded from inventory
  - **Bullets**: When `bullet: true`, `level` is always included (even if 0)
  - **Spacing**: `space_before`, `space_after`, and `line_spacing` in points (only included when set)
  - **Colors**: `color` for RGB (e.g., "FF0000"), `theme_color` for theme colors (e.g., "DARK_1")
  - **Properties**: Only non-default values are included in the output

### Step 6: Generate replacement text and save the data to a JSON file

Based on the text inventory from step 5:

- First verify which shapes exist in the inventory -- only reference shapes that are actually present
- The replace.py script validates that all shapes in your replacement JSON exist in the inventory
  - If you reference a non-existent shape, you get an error showing available shapes
  - If you reference a non-existent slide, you get an error indicating the slide does not exist
  - All validation errors are shown at once before the script exits
- The replace.py script uses inventory.py internally to identify all text shapes
- All text shapes from the inventory will be cleared unless you provide "paragraphs" for them
- Add a "paragraphs" field to shapes that need content (not "replacement_paragraphs")
- Shapes without "paragraphs" in the replacement JSON will have their text cleared automatically
- Paragraphs with bullets will be automatically left aligned. Do not set the `alignment` property when `"bullet": true`
- Generate appropriate replacement content for placeholder text
- Use shape size to determine appropriate content length
- Include paragraph properties from the original inventory -- do not just provide text
- When bullet: true, do not include bullet symbols in text -- they are added automatically
- **Formatting rules**:
  - Headers/titles: use `"bold": true`
  - List items: use `"bullet": true, "level": 0` (level is required when bullet is true)
  - Preserve any alignment properties (e.g., `"alignment": "CENTER"` for centred text)
  - Include font properties when different from default (e.g., `"font_size": 14.0`, `"font_name": "Lora"`)
  - Colors: Use `"color": "FF0000"` for RGB or `"theme_color": "DARK_1"` for theme colours
  - The replacement script expects properly formatted paragraphs, not just text strings
  - Overlapping shapes: prefer shapes with larger default_font_size or more appropriate placeholder_type
- Save the updated inventory with replacements to `replacement-text.json`
- Different template layouts have different shape counts -- always check the actual inventory before creating replacements

<example>
Paragraphs field showing proper formatting:
```json
"paragraphs": [
  {
    "text": "New presentation title text",
    "alignment": "CENTER",
    "bold": true
  },
  {
    "text": "Section Header",
    "bold": true
  },
  {
    "text": "First bullet point without bullet symbol",
    "bullet": true,
    "level": 0
  },
  {
    "text": "Red coloured text",
    "color": "FF0000"
  },
  {
    "text": "Theme coloured text",
    "theme_color": "DARK_1"
  },
  {
    "text": "Regular paragraph text without special formatting"
  }
]
```
</example>

<example>
Shapes not listed in the replacement JSON are automatically cleared:
```json
{
  "slide-0": {
    "shape-0": {
      "paragraphs": [...] // This shape gets new text
    }
    // shape-1 and shape-2 from inventory will be cleared automatically
  }
}
```
</example>

**Common formatting patterns for presentations**:
- Title slides: Bold text, sometimes centred
- Section headers within slides: Bold text
- Bullet lists: Each item needs `"bullet": true, "level": 0`
- Body text: Usually no special properties needed
- Quotes: May have special alignment or font properties

### Step 7: Apply replacements using the `replace.py` script

<example>
```bash
python scripts/replace.py working.pptx replacement-text.json output.pptx
```
Creates: `output.pptx` with replaced text, preserving formatting
</example>

The script will:
- Extract the inventory of all text shapes using functions from inventory.py
- Validate that all shapes in the replacement JSON exist in the inventory
- Clear text from all shapes identified in the inventory
- Apply new text only to shapes with "paragraphs" defined in the replacement JSON
- Preserve formatting by applying paragraph properties from the JSON
- Handle bullets, alignment, font properties, and colours automatically
- Save the updated presentation

<example>
Validation errors:
```
ERROR: Invalid shapes in replacement JSON:
  - Shape 'shape-99' not found on 'slide-0'. Available shapes: shape-0, shape-1, shape-4
  - Slide 'slide-999' not found in inventory
```
</example>

<example>
Overflow errors:
```
ERROR: Replacement text made overflow worse in these shapes:
  - slide-0/shape-2: overflow worsened by 1.25" (was 0.00", now 1.25")
```
</example>
