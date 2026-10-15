# Content Quality Lenses

Nine lenses for judging whether a skill works, not only whether it is well formed, plus four newer points from Anthropic's guidance. A lens finds issues; it does not grade. Each issue maps to the rule ID named in the lens heading and is graded by `rules.md`. An issue that fits no rule goes under "Advisory notes" in the report.

Based on [Anthropic's skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

## Contents

1. [Degrees of freedom (M3)](#1-degrees-of-freedom-m3)
2. [Conciseness (m1)](#2-conciseness-m1)
3. [Actionability (M7)](#3-actionability-m7)
4. [Options and defaults (m2)](#4-options-and-defaults-m2)
5. [Script quality (M6, m13)](#5-script-quality-m6-m13)
6. [Feedback loops (M4)](#6-feedback-loops-m4)
7. [Consistency (M5, m4)](#7-consistency-m5-m4)
8. [Time-sensitive content (m3)](#8-time-sensitive-content-m3)
9. [Runs in Cowork (M11)](#9-runs-in-cowork-m11)
10. [Newer guidance (advisory unless a rule applies)](#10-newer-guidance-advisory-unless-a-rule-applies)
11. [Quick reference](#quick-reference)

## 1. Degrees of freedom (M3)

Match how specific the instructions are to how fragile the task is.

| Task type | Freedom | Form | Example |
|-----------|---------|------|---------|
| Reviews, troubleshooting, analysis | High | Heuristics with a default | "Check structure first, then edge cases" |
| API integration, data processing | Medium | Parameters or pseudocode | `process(data, format="json")` |
| Migrations, releases, OOXML edits | Low | Exact commands or a script | `python scripts/migrate.py --verify` |

Anthropic's analogy: a narrow bridge with cliffs on both sides needs exact guardrails; an open field needs only a direction.

Look for:

- **Too loose** for a fragile step: "Modify the schema, being careful about data integrity." That is M3.
- **Too rigid** for an open-ended task: "Check lines 1-10 for imports, then lines 11-20 for the class, then exactly 5 edge cases." That is M3.

## 2. Conciseness (m1)

Every token in SKILL.md competes with the conversation. Ask of each paragraph: would Claude get this wrong without it?

Look for:

- Explanations of general concepts: what JSON, REST, git, or a PDF is. That is m1.
- Filler such as "It's important to note that..." or "As you may know...". It is an advisory note unless it introduces a general explanation, which is m1.
- Full implementations where a short pattern would do.

Fails:

```markdown
PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need a library.
```

Passes:

```markdown
Extract text with pdfplumber: `pdfplumber.open(path).pages[0].extract_text()`.
```

Keep gotchas and project-specific facts; those are what Claude cannot know.

## 3. Actionability (M7)

Abstract instructions make Claude guess. M7 counts directives built only on the weak verbs listed under M7 in `rules.md`, with no default, command, or check. Three or more is M7.

Can Claude carry out each instruction without guessing the author's intent, asking a clarifying question, or assuming the scope? If not, it is a lead for M7.

| Unactionable | Actionable |
|--------------|------------|
| "Review the code structure appropriately" | "Check for unused imports, functions over 50 lines, and missing type hints" |
| "Handle errors as needed" | "On HTTP 429, wait 2^n seconds (max 60) and retry 3 times" |
| "Adjust the output format" | "Output JSON with the fields status, message, data" |

A weak verb next to a concrete default is fine: "Retry as needed (default 3 attempts)" is actionable.

## 4. Options and defaults (m2)

Three or more tools or approaches with no default and no decision criteria is m2. Give a default and an escape hatch, not a menu.

Passes:

```markdown
Use pdfplumber for text extraction. For scanned PDFs, use pdf2image with pytesseract instead.
```

Fails:

```markdown
You can use pypdf, pdfplumber, PyMuPDF, or pdf2image.
```

Look for lists of 3+ tools without a recommendation, "you could do A, B, or C", and workflow branches with no criteria.

## 5. Script quality (M6, m13)

Scripts should solve the problem, not hand it back to Claude.

- Bare `except:`, `except Exception: pass`, `input()`, or `getpass.getpass()` in a bundled script: M6.
- SKILL.md does not say whether to run or read a script, or does not name the packages it needs: m13.
- Network calls not disclosed in SKILL.md: M10.
- A script that reaches its own skill's files through an install location, opens a browser, or shells out to `claude -p`: M11 (lens 9).

Full detection and pass/fail patterns: `script-quality.md`.

## 6. Feedback loops (M4)

A workflow that deletes, overwrites, publishes, or migrates, or that has 5 or more steps, needs a check before the irreversible step and at the end. Missing checks are M4.

Look for "make all changes, then verify at the end", a plan executed without validating it, and multi-file edits with no intermediate check.

Full patterns: `feedback-loops.md`.

## 7. Consistency (M5, m4)

Contradictions make Claude spend effort reconciling instead of executing.

| Type | Example | Rule |
|------|---------|------|
| Conflicting defaults | "default: 3" in one section, "default: 5" in another | M5 |
| Conflicting rules | "Always output JSON" and "output YAML for configs" with no precedence | M5 |
| Example contradicts the instructions | the example uses a flag the text forbids | M5 |
| Stale cross-reference | "see section X" after X was renamed | M5 |
| Missing bundled file | SKILL.md links a file that does not exist | M5 (definitive) |
| Mixed terminology | "subagent" and "sub-agent", or "field" and "property" | m4 |

Process: list the rules and defaults in SKILL.md, list them in each reference, compare by topic, then check that every cross-reference resolves.

## 8. Time-sensitive content (m3)

Content that expires turns into misinformation.

Fails:

```markdown
If you're doing this before August 2025, use the old API.
```

Passes:

```markdown
## Current method
Use the v2 endpoint: `api.example.com/v2/messages`.

## Old patterns
<details><summary>Legacy v1 API (deprecated)</summary>
The v1 endpoint was `api.example.com/v1/messages`.
</details>
```

Look for date-conditional logic, "currently" or "at the time of writing", and pinned versions with no "verify against official docs" note.

## 9. Runs in Cowork (M11)

The default platform target, `claude-code`, covers Claude Code and Cowork, and the portable platform target shares the same limits, so this lens applies to every review. Cowork runs the Claude Code engine with the plugin's skills, inside a desktop VM or a cloud container. It has no display, never reads `~/.claude/skills`, and does not run dynamic context injection; a cloud session with no linked computer also cannot reach local stdio MCP servers or `localhost`.

Check SKILL.md, every Markdown file under `references/`, and every bundled script. Skip `<example>` blocks for the path check.

| Check | What to look for | Confidence |
|-------|------------------|------------|
| Context injection | In SKILL.md, a `!` at the start of a line or after whitespace followed by a backtick command, or a fenced block whose opening three backticks are followed by `!`. Code fences count | definitive |
| Own files through an install location | A path to the skill's own files through `~/.claude/skills/<own-name>/`, the `$HOME` or `%USERPROFILE%` form of it, the same under `.agents/skills/`, or a project-relative `.claude/skills/<own-name>/` or `.agents/skills/<own-name>/` | definitive |
| Display or browser | A step that opens a GUI window, calls `webbrowser.open`, drives a headed browser, or shows a preview the user must look at, with no file output or headless path | heuristic |
| Local services | A step that depends on a local stdio MCP server or a `localhost` service and states no fallback | heuristic |
| `claude -p` | A step or script that shells out to `claude -p` | heuristic |
| Dotfile-only secrets | Secrets read only from a home-directory dotfile (such as `~/.config/<tool>/.env`), with no environment variable route | heuristic |
| Skill-folder fallback | SKILL.md runs, reads, or copies bundled files with no skill-folder block (`${CLAUDE_SKILL_DIR}`, then the base directory, then a Glob for the skill's own file), so a session that hands over a missing folder fails | advisory, not graded |

quick_validate prints the definitive checks as `[M11] major definitive` lines, and a script that imports `webbrowser` as an `[M11] major check` line; confirm each by reading the cited line. Paths to other skills' files under `~/.claude/skills/` are not M11; they fall under m11's exemption. Neither is the skill-folder search, a Glob or `find` for `**/<own-name>/<file>` in `~/.claude` or `/mnt/skills`.

Fails, in a skill named `report`:

```markdown
Run `python ~/.claude/skills/report/scripts/report.py <input>`.
```

Passes:

```markdown
Run `python ${CLAUDE_SKILL_DIR}/scripts/report.py <input>`, and write the result to `report.md` (in Cowork, the outputs folder).
```

The fixes: reach bundled files through `${CLAUDE_SKILL_DIR}` in Markdown, behind the skill-folder block, and through `Path(__file__).resolve().parent` in scripts; turn injection into an explicit step ("Run `git status`"); write results to files instead of opening them; state the fallback for each local service; read secrets from environment variables.

## 10. Newer guidance (advisory unless a rule applies)

Anthropic's skill and prompting guidance adds four points. Report a gap as an advisory note unless a rule named below applies.

- **Gotchas.** The most valuable content in a skill is often the list of places where Claude goes wrong without it: an API quirk, a file format edge case, a command that fails on Windows. A skill with no gotchas section gets an advisory note naming the likeliest failure point.
- **Defaults, not menus.** Prefer one recommended path with an escape hatch over a list of equal choices. Three or more choices with no default is m2; two equal choices is advisory.
- **Key instructions near the top.** After compaction, Claude Code re-attaches only the first 5,000 tokens of a recently invoked skill (verify the figure against the [Claude Code skills docs](https://code.claude.com/docs/en/skills), since it can change). Safety rules, the main workflow, and the arguments belong near the top; background and long tables go later or in references. A safety rule buried after a long section gets an advisory note.
- **Reasons over emphasis.** Newer models over-apply shouted rules. Three or more all-caps directives without a reason is m15; fewer is advisory.

## Quick reference

| Lens | Core question | Maps to |
|------|---------------|---------|
| Degrees of freedom | Is specificity matched to fragility? | M3 |
| Conciseness | Does each paragraph earn its tokens? | m1 |
| Actionability | Can Claude act without guessing? | M7 |
| Options and defaults | Is there a clear default? | m2 |
| Script quality | Do scripts solve or punt? | M6, m13, M10 |
| Feedback loops | Is there a check before the irreversible step? | M4 |
| Consistency | Do all files agree? | M5, m4 |
| Time-sensitive content | Will this be wrong in six months? | m3 |
| Runs in Cowork | Does it run without a display, injection, install paths, or local-only services? | M11 |
| Newer guidance | Gotchas, defaults, key instructions first, reasons | advisory, m2, m15 |
