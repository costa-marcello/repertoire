# PDF Form Filling Workflow

## Contents

1. [Fillable fields](#fillable-fields)
2. [Non-fillable fields](#non-fillable-fields)

Complete these steps in order. Do not skip ahead to writing code.

First, check whether the PDF has fillable form fields. Run this script from this file's directory:
`python scripts/check_fillable_fields.py <file.pdf>`

Depending on the result, follow either "Fillable fields" or "Non-fillable fields".

## Fillable fields

If the PDF has fillable form fields:

- Run from this file's directory: `python scripts/extract_form_field_info.py <input.pdf> <field_info.json>`. This creates a JSON file listing fields in this format:

```
[
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "rect": ([left, bottom, right, top] bounding box in PDF coordinates, y=0 is the bottom of the page),
    "type": ("text", "checkbox", "radio_group", or "choice"),
  },
  // Checkboxes have "checked_value" and "unchecked_value" properties:
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "type": "checkbox",
    "checked_value": (Set the field to this value to check the checkbox),
    "unchecked_value": (Set the field to this value to uncheck the checkbox),
  },
  // Radio groups have a "radio_options" list with the possible choices.
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "type": "radio_group",
    "radio_options": [
      {
        "value": (set the field to this value to select this radio option),
        "rect": (bounding box for the radio button for this option)
      },
      // Other radio options
    ]
  },
  // Multiple choice fields have a "choice_options" list with the possible choices:
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "type": "choice",
    "choice_options": [
      {
        "value": (set the field to this value to select this option),
        "text": (display text of the option)
      },
      // Other choice options
    ],
  }
]
```

- Convert the PDF to PNGs (one image per page) with:
  `python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>`
  Then analyse the images to determine each field's purpose. Convert the bounding box PDF coordinates to image coordinates when you compare.

- Create a `field_values.json` file in this format with the values to enter for each field:

```
[
  {
    "field_id": "last_name", // Must match the field_id from `extract_form_field_info.py`
    "description": "The user's last name",
    "page": 1, // Must match the "page" value in field_info.json
    "value": "Simpson"
  },
  {
    "field_id": "Checkbox12",
    "description": "Checkbox to be checked if the user is 18 or over",
    "page": 1,
    "value": "/On" // If this is a checkbox, use its "checked_value" value to check it. If it's a radio button group, use one of the "value" values in "radio_options".
  },
  // more fields
]
```

- Run the fill script from this file's directory to create the filled PDF:
  `python scripts/fill_fillable_fields.py <input pdf> <field_values.json> <output pdf>`
  The script verifies that the field IDs and values are valid. If it prints errors, correct the relevant fields and try again.

## Non-fillable fields

If the PDF lacks fillable form fields, visually determine where the data should be added and create text annotations. Complete every step below in order so the form is accurately filled.

- Convert the PDF to PNG images and determine field bounding boxes.
- Create a JSON file with field information and validation images showing the bounding boxes.
- Validate the bounding boxes.
- Use the bounding boxes to fill in the form.

### Step 1: Visual analysis

- Convert the PDF to PNG images. Run from this file's directory:
  `python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>`
  The script creates one PNG per page.
- Examine each PNG and identify all form fields and data-entry areas. For each text field, determine separate bounding boxes for the label and for the entry area. The label and entry bounding boxes must not intersect; the entry box should cover only the area where data is entered. Entry boxes usually sit immediately to the side, above, or below the label, and must be tall and wide enough for the text.

Common form structures:

*Label inside box*
```
┌────────────────────────┐
│ Name:                  │
└────────────────────────┘
```
The input area sits to the right of the "Name" label and extends to the edge of the box.

*Label before line*
```
Email: _______________________
```
The input area sits above the line and covers its full width.

*Label under line*
```
_________________________
Name
```
The input area sits above the line and covers its full width. Common for signature and date fields.

*Label above line*
```
Please enter any special requests:
________________________________________________
```
The input area extends from the bottom of the label to the line and covers the line's full width.

*Checkboxes*
```
Are you a US citizen? Yes □  No □
```
For checkboxes:
- Target the small square (□), not the text label. The square may sit to the left or right of its label.
- Distinguish label text ("Yes", "No") from the clickable checkbox squares.
- The entry bounding box should cover only the square.

### Step 2: Create fields.json and validation images

- Create a `fields.json` file with this structure:

```
{
  "pages": [
    {
      "page_number": 1,
      "image_width": (first page image width in pixels),
      "image_height": (first page image height in pixels),
    },
    {
      "page_number": 2,
      "image_width": (second page image width in pixels),
      "image_height": (second page image height in pixels),
    }
    // additional pages
  ],
  "form_fields": [
    // Example for a text field.
    {
      "page_number": 1,
      "description": "The user's last name should be entered here",
      // Bounding boxes are [left, top, right, bottom]. The label and entry boxes must not overlap.
      "field_label": "Last name",
      "label_bounding_box": [30, 125, 95, 142],
      "entry_bounding_box": [100, 125, 280, 142],
      "entry_text": {
        "text": "Johnson", // This text will be added as an annotation at the entry_bounding_box location
        "font_size": 14, // optional, defaults to 14
        "font_color": "000000", // optional, RRGGBB format, defaults to 000000 (black)
      }
    },
    // Example for a checkbox. Target the square for the entry bounding box, not the text.
    {
      "page_number": 2,
      "description": "Checkbox that should be checked if the user is over 18",
      "entry_bounding_box": [140, 525, 155, 540],  // Small box over checkbox square
      "field_label": "Yes",
      "label_bounding_box": [100, 525, 132, 540],  // Box containing "Yes" text
      // Use "X" to check a checkbox.
      "entry_text": {
        "text": "X",
      }
    }
    // additional form field entries
  ]
}
```

- Create validation images by running this script from this file's directory for each page:
  `python scripts/create_validation_image.py <page_number> <path_to_fields.json> <input_image_path> <output_image_path>`

  The validation images show red rectangles where text will be entered and blue rectangles over label text.

### Step 3: Validate bounding boxes

#### Automated intersection check

- Check the fields.json file for overlapping boxes and entry boxes that are too short:
  `python scripts/check_bounding_boxes.py <JSON file>`

  If there are errors, re-analyse the relevant fields, adjust the bounding boxes, and iterate until there are no remaining errors. Label (blue) boxes should contain text labels; entry (red) boxes should not.

#### Manual image inspection

Inspect the validation images before proceeding. Verify:
- Red rectangles cover only input areas.
- Red rectangles contain no text.
- Blue rectangles contain label text.
- For checkboxes: the red rectangle is centred on the checkbox square, and the blue rectangle covers the checkbox's text label.

If any rectangles look wrong, fix fields.json, regenerate the validation images, and verify again. Repeat until the bounding boxes are accurate.

### Step 4: Add annotations to the PDF

Run from this file's directory to create a filled PDF using the information in fields.json:
`python scripts/fill_pdf_form_with_annotations.py <input_pdf_path> <path_to_fields.json> <output_pdf_path>`
