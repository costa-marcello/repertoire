---
name: xlsx
description: "Creates, edits, and analyses spreadsheets with formulas, formatting, and data visualisation. Use when working with .xlsx, .xlsm, .csv, or .tsv files, creating spreadsheets from scratch, reading or analysing tabular data, modifying files while preserving formulas, building financial models, or recalculating formula values."
license: MIT
---

# Output Rules

## Zero Formula Errors

Deliver every Excel file with zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?).

## Preserve Existing Templates

When updating a file with established patterns, match its format, style, and conventions exactly. Existing template conventions override these guidelines.

## Financial Models

For financial model colour coding, number formatting, assumptions placement, and hardcode documentation standards, read `references/financial-model-standards.md`.

---

<instructions>

# Workflow

## Tool Selection

| Task | Library | Reason |
|------|---------|--------|
| Data analysis, bulk operations, simple export | **pandas** | Fast column operations, statistics |
| Formulas, formatting, Excel-specific features | **openpyxl** | Preserves formulas and styles |

Default to openpyxl. Use pandas when the task is purely data analysis with no formula or formatting needs.

## Step-by-Step Process

```
Workflow Progress:
- [ ] Step 1: Choose library (pandas or openpyxl)
- [ ] Step 2: Create or load the workbook
- [ ] Step 3: Add data, formulas, and formatting
- [ ] Step 4: Save the file
- [ ] Step 5: Recalculate formulas (run scripts/recalc.py)
- [ ] Step 6: Check recalc output for errors -- fix and re-run until clean
- [ ] Step 7: Return a summary with file path, formula count, and any unresolved errors
```

## Formulas Over Hardcodes

Use Excel formulas for all calculations. Do not compute values in Python and write the result.

<example>
**Bad -- hardcoding a computed value:**
```python
total = df['Sales'].sum()
sheet['B10'] = total  # writes 5000, not a formula
```

**Good -- letting Excel compute:**
```python
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```
</example>

## Reading Data with pandas

```python
import pandas as pd

df = pd.read_excel('file.xlsx')                          # first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # all sheets as dict
df = pd.read_excel('file.xlsx', dtype={'id': str}, usecols=['A', 'C'], parse_dates=['date'])
```

## Creating a New Workbook

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
ws = wb.active
ws['A1'] = 'Header'
ws['A1'].font = Font(bold=True, color='FF0000')
ws['A1'].fill = PatternFill('solid', start_color='FFFF00')
ws['A1'].alignment = Alignment(horizontal='center')
ws.column_dimensions['A'].width = 20
ws['B2'] = '=SUM(A1:A10)'
wb.save('output.xlsx')
```

## Editing an Existing Workbook

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
ws = wb.active  # or wb['SheetName']
ws['A1'] = 'Updated'
ws.insert_rows(2)
wb.save('modified.xlsx')
```

### Key openpyxl Details

- Cell indices are 1-based (row=1, column=1 = A1).
- `load_workbook('file.xlsx', data_only=True)` reads calculated values. Do not save after loading with `data_only=True` -- formulas will be permanently lost.
- For large files use `read_only=True` (reading) or `write_only=True` (writing).

## Recalculating Formulas

openpyxl writes formulas as strings without computed values. Run the recalc script after every save that contains formulas:

```bash
python scripts/recalc.py output.xlsx 30
```

The script uses LibreOffice (assumed installed) to recalculate, then scans all cells for errors. It returns JSON:

```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42
}
```

If `status` is `errors_found`, check `error_summary` for types and locations:

| Error | Cause | Fix |
|-------|-------|-----|
| `#REF!` | Invalid cell reference | Verify referenced cells exist |
| `#DIV/0!` | Division by zero | Add `=IF(B2=0, 0, A2/B2)` guard |
| `#VALUE!` | Wrong data type in formula | Check input types |
| `#NAME?` | Unrecognised formula name | Check spelling |
| `#N/A` | Value not found in lookup | Verify lookup values exist |

Fix the errors, save, and run `scripts/recalc.py` again. Repeat until `status` is `success`.

For the full verification checklist, read `references/formula-verification.md`.

</instructions>

---

<examples>

<example>
**Example 1: Sales Report from CSV**

User asks: "Create a formatted sales report from this CSV."

```python
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, numbers

df = pd.read_csv('sales.csv')
wb = Workbook()
ws = wb.active
ws.title = 'Sales Report'

# Headers
headers = list(df.columns)
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, color='FFFFFF')
    cell.fill = PatternFill('solid', start_color='4472C4')
    cell.alignment = Alignment(horizontal='center')

# Data rows
for r_idx, row in enumerate(df.itertuples(index=False), 2):
    for c_idx, value in enumerate(row, 1):
        ws.cell(row=r_idx, column=c_idx, value=value)

# Summary formulas
last_row = len(df) + 1
ws.cell(row=last_row + 1, column=1, value='Total')
ws.cell(row=last_row + 1, column=2).value = f'=SUM(B2:B{last_row})'

wb.save('sales_report.xlsx')
```
Then run: `python scripts/recalc.py sales_report.xlsx`
</example>

<example>
**Example 2: Editing Existing File, Preserving Formulas**

User asks: "Add a new column to my budget spreadsheet."

```python
from openpyxl import load_workbook

wb = load_workbook('budget.xlsx')
ws = wb.active
new_col = ws.max_column + 1
ws.cell(row=1, column=new_col, value='Variance')

for row in range(2, ws.max_row + 1):
    budget_cell = ws.cell(row=row, column=2).coordinate
    actual_cell = ws.cell(row=row, column=3).coordinate
    ws.cell(row=row, column=new_col).value = f'={actual_cell}-{budget_cell}'

wb.save('budget.xlsx')
```
Then run: `python scripts/recalc.py budget.xlsx`
</example>

<example>
**Example 3: Data Analysis Only (No Formulas)**

User asks: "Which products had the highest sales last quarter?"

```python
import pandas as pd

df = pd.read_excel('inventory.xlsx')
q4 = df[df['Quarter'] == 'Q4']
top = q4.nlargest(10, 'Sales')[['Product', 'Sales', 'Region']]
print(top.to_string(index=False))
```

No recalc needed -- pure analysis with no file output.
</example>

<example>
**Example 4: Multi-Sheet Financial Model**

User asks: "Build a 3-statement model with assumptions tab."

Read `references/financial-model-standards.md` for colour coding and number formats, then:

```python
from openpyxl import Workbook
from openpyxl.styles import Font

wb = Workbook()
assumptions = wb.active
assumptions.title = 'Assumptions'
assumptions['A1'] = 'Revenue Growth'
assumptions['B1'] = 0.05
assumptions['B1'].font = Font(color='0000FF')  # blue = hardcoded input

income = wb.create_sheet('Income Statement')
income['A1'] = 'Revenue'
income['B1'] = 1000000
income['B1'].font = Font(color='0000FF')
income['C1'] = "=B1*(1+Assumptions!B1)"
income['C1'].font = Font(color='000000')  # black = formula

wb.save('model.xlsx')
```
Then run: `python scripts/recalc.py model.xlsx`
</example>

<example>
**Example 5: Bulk CSV-to-Excel Conversion**

User asks: "Convert all CSVs in this folder to one Excel file with tabs."

```python
import pandas as pd
from pathlib import Path

writer = pd.ExcelWriter('combined.xlsx', engine='openpyxl')
for csv_file in sorted(Path('.').glob('*.csv')):
    df = pd.read_csv(csv_file)
    df.to_excel(writer, sheet_name=csv_file.stem[:31], index=False)
writer.close()
```
</example>

</examples>

---

## Code Style

Write minimal Python. No unnecessary comments, verbose variable names, or redundant print statements. For Excel files, add cell comments for complex formulas and data sources.

## References

| File | Purpose |
|------|---------|
| `references/formula-verification.md` | Verification checklist and error debugging |
| `references/financial-model-standards.md` | Colour coding, number formats, assumptions, hardcode docs |
| `scripts/recalc.py` | LibreOffice formula recalculation with error scanning |
