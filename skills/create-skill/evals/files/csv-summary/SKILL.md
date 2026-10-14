---
name: csv-summary
description: "Summarises a CSV file as a Markdown table of row and column counts. Use when the user asks how many rows or columns a CSV has."
---

# CSV Summary

<instructions>

1. Read the CSV file the user names.
2. Split each line on commas to get the fields.
3. Count the rows (excluding the header) and the columns in the header.
4. Reply with a two-row Markdown table: `rows | columns`.
5. Verify: the row count equals the number of non-empty lines minus one.

</instructions>
