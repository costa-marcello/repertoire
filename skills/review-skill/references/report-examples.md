# Report Examples

The report format, one full sample report, and three before/after Auto-Fix runs. Every grade below follows the bands in `rules.md`: count each Major and Minor ID once, ignore Style, and take the first band that matches from the top.

## Contents

1. [Report format](#report-format)
2. [Sample report: Review Only, Grade C](#sample-report-review-only-grade-c)
3. [Fix summary format](#fix-summary-format)
4. [Auto-Fix 1: bloated skill, D to A in one pass](#auto-fix-1-bloated-skill-d-to-a-in-one-pass)
5. [Auto-Fix 2: forked interactive skill, F to A in two passes](#auto-fix-2-forked-interactive-skill-f-to-a-in-two-passes)
6. [Auto-Fix 3: a finding that stays open, D to C](#auto-fix-3-a-finding-that-stays-open-d-to-c)

## Report format

```markdown
# Skill review: <skill-name>

| Field | Value |
|-------|-------|
| Target | <path> |
| Mode | <Review Only, Review + Auto-Fix, or Auto-Fix>, plus "with regression" when `regression` was given |
| Graded for | <claude-code (Claude Code and Cowork) or portable (single-skill uploads to claude.ai and the API)> |
| quick_validate | <ran, exit N (meaning)> or <not run (reason)> |
| security_scan | <ran with --no-marker, exit N (RESULT secrets=<n> leads=<n>)> or <secret scan not run (reason)> |
| Regression | <only when a regression run was requested or triggered: ran, with case counts, or not run (reason)> |

## Grade: <letter>

<n> Major (<IDs>), <n> Minor (<IDs>). Band: <the band row that matched>.

## Major findings

### <ID> <rule title>
- Where: <file:line>, <file:line>
- Evidence: "<quoted text>"
- Confidence: <definitive (validator)> or <heuristic, confirmed>
- Fix: <the exact edit or command>

## Minor findings

<same shape, or "None.">

## Style notes (not graded)

<same shape, or "None.">

## Advisory notes

- Discarded checks: <[ID] file:line, and the reason>
- Trigger review: should trigger <3 prompts>; near-misses <3 prompts>; overlaps <skills>
- Other: <lens observations that map to no rule, fork nesting notes>
```

Rules for filling it in:

- One heading per rule ID, with every location under it. Never one heading per location.
- Quote the evidence exactly, with its line number. A heuristic finding without a quote is not a finding.
- Write each fix as an edit or a command the reader can apply without guessing.
- Write "None." in an empty section instead of dropping it, so the reader can see the check ran.
- The Regression row and the M12 finding follow the format in `mode-regression.md`.

## Sample report: Review Only, Grade C

quick_validate printed two definitive m9 lines, three Style lines (S2, and S5 once for each missing evals file), and one `check` line (M7). security_scan --verbose printed one `[M10] major check` line and ended with `RESULT secrets=0 leads=1`. The reviewer confirmed one heuristic Major and one heuristic Minor by reading, and discarded both leads.

```markdown
# Skill review: invoice-extract

| Field | Value |
|-------|-------|
| Target | ./skills/invoice-extract |
| Mode | Review Only |
| Graded for | claude-code (Claude Code and Cowork) |
| quick_validate | ran, exit 4 (definitive Minor only) |
| security_scan | ran with --no-marker, exit 0 (RESULT secrets=0 leads=1) |

## Grade: C

1 Major (M4), 2 Minor (m2, m9). Band: C, "1 Major".

## Major findings

### M4 No verification step for destructive or long workflows
- Where: SKILL.md:58
- Evidence: "Write the converted totals back into the input workbook and save it."
- Confidence: heuristic, confirmed. The step overwrites the user's file and nothing checks the totals first.
- Fix: replace line 58 with "Write the totals to `<input>-totals.xlsx`. Run `python scripts/check_totals.py <input>-totals.xlsx`; it exits 0 when every invoice total matches its line items. Fix and re-run until it passes. Replace the input only if the user asks."

## Minor findings

### m2 Three or more options with no default
- Where: SKILL.md:31
- Evidence: "Use pdfplumber, camelot, or tabula-py to read the tables."
- Confidence: heuristic, confirmed.
- Fix: "Default to pdfplumber. Use camelot for ruled tables when pdfplumber merges cells."

### m9 Long reference file without a table of contents
- Where: references/field-map.md:1 (142 lines), references/vendors.md:1 (118 lines)
- Evidence: neither file has a Contents heading in its first 30 lines.
- Confidence: definitive (validator).
- Fix: add a "## Contents" link list under the title of each file.

## Style notes (not graded)

### S2 Fewer than 3 or more than 5 example blocks
- Where: SKILL.md (1 example block)
- Fix: add two short example blocks: a multi-page invoice and a credit note.

### S5 No evals
- Where: evals/evals.json and evals/trigger_queries.json (evals/ is missing)
- Fix: add evals/evals.json with 3 cases and evals/trigger_queries.json.

## Advisory notes

- Discarded checks:
  - [M7] SKILL.md:47 "Retry as needed (default 3 attempts, 2 seconds apart)." The directive gives a default, so it is actionable.
  - [M10] scripts/fx.py:12 (security_scan) `urllib.request.urlopen(` call. SKILL.md:12 discloses it: "Fetches daily exchange rates from the ECB (network)."
- Trigger review: should trigger "pull the line items out of these supplier invoices", "turn invoice PDFs into a spreadsheet of totals", "extract VAT amounts from this invoice". Near-misses: "create an invoice for my client", "summarize this PDF contract", "extract text from a scanned letter". Overlaps the kit's pdf skill; naming invoices and totals in the first clause of the description keeps them apart.
- Other: no gotchas section. The vendor-specific date formats in vendors.md are the likeliest failure point and deserve a short list near the top of SKILL.md.
```

Why C: the bands are checked from the top. F needs 4+ Major; D needs 2-3 Major, or 1 Major with 4+ Minor. C matches on "1 Major". m9 has two locations but counts once.

## Fix summary format

Review + Auto-Fix appends this after the report; Auto-Fix prints the findings list and then this.

```markdown
## Fix summary

| Field | Value |
|-------|-------|
| Passes | <n> of 3 |
| Backup | <the printed path, or "not needed: tracked and clean in your own repository"> |
| Files changed | <file (before -> after lines)>, <added files> |
| Fixed | <IDs> |
| Still open | <ID: reason>, or "none" |
| Grade | <before> -> <after> |
| Regression | <ran: <n> cases, <p> passed, <f> passed on the re-run, <m> failed twice>, or <not run (reason)> |
| Style notes left as is | <IDs> (Style fixes were not requested) |
```

## Auto-Fix 1: bloated skill, D to A in one pass

Before, SKILL.md is 580 lines:

```yaml
---
name: data-export
description: "Export data from databases"
license: MIT
---
```

| ID | Where | Evidence |
|----|-------|----------|
| M1 | SKILL.md | 580 lines (definitive) |
| M7 | SKILL.md:44, :97, :130 | "Ensure the export format is correct", "Handle large tables appropriately", "Retry as needed" (no defaults) |
| M8 | SKILL.md:3 | No trigger clause, and the capability is vague |
| m1 | SKILL.md:12-30 | Explains what CSV and Parquet are |
| S3 | SKILL.md | 580 lines, over the 400-line house limit (Style) |
| S4 | root | `formats.md` and `tips.md` beside SKILL.md (Style) |
| S6 | SKILL.md:3 | Opens with "Export" (Style) |

Before grade: 3 Major (M1, M7, M8) and 1 Minor (m1), so D ("2-3 Major").

Pass 1 applied the rules.md fixes:

- M1: moved the SQL syntax section (lines 310-520) into a new reference, `sql-syntax.md`. It is 214 lines, so it got a `## Contents` list. SKILL.md links it with "Read when writing a custom export query."
- M8: rewrote the description, which also cleared S6:

  ```yaml
  description: "Exports tables from PostgreSQL and MySQL to CSV, JSON, or Parquet. Use when the user asks to export, dump, or snapshot database tables, or to schedule a recurring export."
  ```

- M7: "Run `python scripts/validate_export.py <file>`; it exits 0 when the columns match the source schema." / "Export tables over 1,000,000 rows with `--chunk-size 100000`." / "Retry a failed connection 3 times, 5 seconds apart, then stop and report the error." The flag and its default came from reading the script's argparse block; the script was not run.
- m1: deleted lines 12-30.

Re-check: quick_validate exit 0, and the rules walk found no Major or Minor. S4 stays as a Style note because Style fixes were not requested. No `context: fork` was added.

The skill is tracked in the user's own repository and the loop changed it, so a regression run followed without asking. All 3 eval cases passed on the first run.

```markdown
## Fix summary

| Field | Value |
|-------|-------|
| Passes | 1 of 3 |
| Backup | not needed: tracked and clean in your own repository |
| Files changed | SKILL.md (580 -> 352 lines), added sql-syntax.md |
| Fixed | M1, M7, M8, m1 (S3 and S6 cleared as side effects of the M1 move and the M8 rewrite) |
| Still open | none |
| Grade | D -> A |
| Regression | ran: 3 cases, 3 passed, 0 passed on the re-run, 0 failed twice |
| Style notes left as is | S4 |
```

## Auto-Fix 2: forked interactive skill, F to A in two passes

Before, SKILL.md is 720 lines:

```yaml
---
name: api-tester
description: "Test your APIs"
license: MIT
context: fork
agent: general-purpose
---
```

| ID | Where | Evidence |
|----|-------|----------|
| M1 | SKILL.md | 720 lines (definitive) |
| M2 | SKILL.md:18 | "Ask the user which environment to test against." with `context: fork` (definitive) |
| M7 | SKILL.md:66, :102, :140, :188 | Four directives built on "ensure" and "handle appropriately" with no defaults |
| M8 | SKILL.md:3 | "your" is second person, and there is no trigger clause |
| m1 | SKILL.md:50-80 | Explains what a REST API is |
| S3 | SKILL.md | 720 lines, over the 400-line house limit (Style) |
| S5 | evals/ | No evals folder (Style) |
| S6 | SKILL.md:3 | Opens with "Test", not a third-person verb (Style) |

Before grade: 4 Major (M1, M2, M7, M8), so F ("4 or more Major"), whatever the Minor count.

Pass 1:

- M2: removed `context: fork` and `agent`. The question on line 18 now reaches the user, because the skill runs inline.
- M8: `description: "Tests REST and GraphQL endpoints against a response schema and reports failing assertions. Use when the user asks to test an API, check a response schema, or run API regression checks."`
- M1: moved 410 lines into two new references, `api-patterns.md` (262 lines) and `schema-validation.md` (148 lines).
- M7: replaced each directive with a command or a default, for example "Run `python scripts/validate_response.py --schema <schema.json> <response.json>`; exit 1 lists the failing fields."
- m1: deleted lines 50-80.

Re-check after pass 1: quick_validate exit 4 with two m9 lines, one for each new reference, because neither has a Contents heading. That is 0 Major and 1 Minor (m9), so B.

Pass 2: added a `## Contents` list to both new references. Re-check: exit 0, no Major or Minor.

No regression run: the folder is not in the user's own repository, and the skill has no evals.

```markdown
## Fix summary

| Field | Value |
|-------|-------|
| Passes | 2 of 3 |
| Backup | /tmp/tmp.k3J9qA/api-tester-backup (the folder was not in a git repository) |
| Files changed | SKILL.md (720 -> 298 lines), added api-patterns.md and schema-validation.md |
| Fixed | M1, M2, M7, M8, m1, and m9 (introduced in pass 1, fixed in pass 2); S3 and S6 cleared as side effects of the M1 move and the M8 rewrite |
| Still open | none |
| Grade | F -> A |
| Regression | not run (not in your own repository) |
| Style notes left as is | S5 |
```

## Auto-Fix 3: a finding that stays open, D to C

`release-notes` has a 7-step release workflow. Before:

| ID | Where | Evidence |
|----|-------|----------|
| M3 | SKILL.md:40 | "Publish the package to the registry carefully." A fragile, irreversible step with no command |
| M4 | SKILL.md:34-41 | Seven steps ending in a publish, with no check before it |
| m15 | SKILL.md:12, :20, :33, :41 | "NEVER skip the changelog", "ALWAYS use semver", "You MUST tag", "CRITICAL: bump the version", all without reasons |
| m4 | SKILL.md:8, :15, :27 | "release notes", "changelog", and "CHANGES file" name the same file |

Before grade: 2 Major (M3, M4) and 2 Minor (m15, m4), so D ("2-3 Major").

Pass 1:

- M4: added a check before the publish step: "Show the user the version, the tag, and the new changelog entry, and publish only after a yes. After publishing, run `git ls-remote --tags origin v<version>` and confirm the tag exists."
- m15: rewrote the four directives in plain words with reasons, for example "Tag every release, because the deploy job builds from tags."
- m4: used "changelog" everywhere.
- M3: not applied. The exact publish command depends on the registry, and the skill does not say whether it is npm or PyPI. Inventing one would mislead Claude, so the reviewer asked the user: "Which command publishes the package: `npm publish`, `twine upload dist/*`, or another?"

Re-check: 1 Major (M3) and 0 Minor, so C ("1 Major"). The loop stops here rather than spending passes 2 and 3 on a fix that needs the author's answer. When the user replies, the next pass applies it and counts toward the 3-pass limit.

The loop changed a skill in the user's own repository, so a regression run followed. Case 2 failed its first run and passed the re-run, so it is listed as flaky under advisory notes, not as M12. Its publish command went to `would_run.txt`, as the isolation rules require.

```markdown
## Fix summary

| Field | Value |
|-------|-------|
| Passes | 1 of 3 |
| Backup | not needed: tracked and clean in your own repository |
| Files changed | SKILL.md |
| Fixed | M4, m15, m4 |
| Still open | M3: needs the publish command; question sent to the user |
| Grade | D -> C |
| Regression | ran: 3 cases, 2 passed, 1 passed on the re-run, 0 failed twice |
| Style notes left as is | none |
```
