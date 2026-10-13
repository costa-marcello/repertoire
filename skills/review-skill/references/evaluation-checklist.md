# Skill Evaluation Checklist

Complete checklist based on [official Anthropic best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

## YAML Frontmatter

### Required Fields

- [ ] `name` field present and valid
  - Max 64 characters
  - Lowercase letters, numbers, hyphens only
  - No reserved words (anthropic, claude)
  - Noun or short-phrase form preferred (pdf, changelog, frontend-design)

- [ ] `description` field present and valid
  - Non-empty
  - Max 1024 characters
  - **Third-person voice** (required -- most common failure)
  - Includes trigger conditions ("Use when...")

- [ ] `context: fork` correctly applied (canonical taxonomy — single source of truth)

  Four skill classes. Only Class A gets `context: fork`.

  **Class A — Autonomous (add `context: fork`):** runs self-contained work end-to-end (file I/O, script execution, analysis). No sub-agent dispatch. No pause for the user. No persistent reasoning mode.
  *Signals:* scripts in `scripts/`, linear numbered steps, `allowed-tools` limited to read / single-process tools, needs subagent isolation.

  **Class B — Orchestrator (no fork):** dispatches sub-agents.
  *Signals:* `allowed-tools` includes `Task`, `TeamCreate`, `TaskCreate`, or `SendMessage`; body mentions "spawn agents", "dispatch agents", "parallel agents/sub-agents", agent allocation tables, or `TaskOutput` collection.
  *Why no fork:* a forked subagent cannot spawn further subagents; fork breaks the dispatch chain.

  **Class C — Interactive (no fork):** presents a report, plan, or prompt to the user AND resumes on the user's response.
  *Signals:* a numbered step or mode that shows output to the user, followed by a later step or mode gated on the user's reply ("after the user confirms", "if the user approves", "then apply"). Writing a report file to disk does NOT qualify — the pause must be directed at the human reader.
  *Why no fork:* a forked subagent returns only a final summary, collapsing the two-stage flow into one opaque result.

  **Class D — Mode-style reasoning (no fork):** persistent thinking modes that span turns or accumulate tokens in the lead context (e.g. `ultrathink`).
  *Signals (the skill is Class D when the value comes from Claude's reasoning in the lead context, not from tool use or file output):*
  - `allowed-tools` is empty, absent, or restricted to passive/read-only analysis.
  - No `scripts/` directory; body has no `Bash`, `Write`, `Edit`, or external I/O steps.
  - Description uses stance / perspective verbs ("thinks", "analyses", "reasons", "considers") rather than manipulation verbs ("extracts", "generates", "runs").
  - Skill is invoked as a reasoning modifier on an existing task (often with a case-sensitive trigger keyword) rather than as a self-contained task.
  - Body describes a lens, framework, or mental model to apply — not a workflow that produces a file or state change.
  *Why no fork:* a fork spawns a fresh subagent context, losing the lead's thinking tokens, conversation state, and cross-turn persistence that give the mode its value.

  **Definitive conflicts (fork must be removed):**
  (a) `context: fork` set AND `allowed-tools` contains any of `Task`, `TeamCreate`, `TaskCreate`, `SendMessage` — orchestrator violation.
  (b) `context: fork` set AND the skill body defines a user-visible pause AND a later step or mode gated on the user's response — interactive violation.
  (c) `context: fork` set AND the skill is invoked as a persistent reasoning mode rather than a discrete task — mode-style violation.

  **Pairing rule:** `agent` is always paired with `context: fork`. Add or remove both together.

### Description Quality

**Third-Person Voice Check:**

```
BAD:  "Browse YouTube videos..."          (imperative)
BAD:  "You can use this to..."            (second person)
BAD:  "I can help you..."                 (first person)
BAD:  "Complete toolkit for..."           (noun phrase)
GOOD: "Browses YouTube videos..."         (third-person verb)
GOOD: "Extracts text from PDFs..."        (third-person verb)
GOOD: "Processes Excel files and..."      (third-person verb)
```

**Trigger Conditions Check:**

```
BAD:  "Processes PDFs"
GOOD: "Extracts text from PDFs. Use when working with PDF files or when the user mentions document extraction."
```

## File Structure

### Core Requirements

- [ ] **SKILL.md body under 500 lines** (required)
- [ ] **Only SKILL.md in root** (no loose .md files)
- [ ] Reference files in `references/` folder
- [ ] One level deep references (no nested references)

### Recommended Structure

```
skill-name/
├── SKILL.md              (under 500 lines)
└── references/
    ├── configuration.md  (if needed)
    ├── examples.md       (if needed)
    └── advanced.md       (if needed)
```

### File Naming

- [ ] Descriptive filenames (not doc1.md, file2.md)
- [ ] Use forward slashes (Unix-style paths)
- [ ] No Windows-style paths (backslashes)

## Content Quality

### Conciseness

- [ ] No obvious explanations Claude already knows
- [ ] Challenge each paragraph: "Does Claude need this?"
- [ ] Default assumption: Claude is already smart

**Good (concise):**
```markdown
Use pdfplumber for text extraction:
\`\`\`python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
\`\`\`
```

**Bad (verbose):**
```markdown
PDF (Portable Document Format) files are a common file format...
To extract text from a PDF, you'll need to use a library...
There are many libraries available for PDF processing...
```

### Workflow Patterns

- [ ] Clear sequential steps for complex tasks
- [ ] Copy-paste checklist provided
- [ ] Validation/verification steps included
- [ ] Feedback loops for quality-critical operations

### Progressive Disclosure

- [ ] Main instructions in SKILL.md
- [ ] Detailed content in `references/`
- [ ] Large files include table of contents
- [ ] No duplication between files

## Scripts (if present)

Check using `content-quality-checklist.md` Section 5 and `script-quality.md` for detailed patterns.

Quick pass/fail:
- [ ] No bare `except:` clauses
- [ ] No hardcoded secrets or user-specific paths
- [ ] All constants documented with rationale

## Unified Grading Rubric

This is the single grading rubric for the entire skill. Combine findings from all three evaluation layers into one grade.

### Three Evaluation Layers

| Layer | Source | Items |
|-------|--------|-------|
| **Structural** | This checklist (above) | Frontmatter, file structure, file naming |
| **Content Quality** | `content-quality-checklist.md` | 8 dimensions: degrees of freedom, conciseness, actionability, options overload, script quality, feedback loops, consistency, time-sensitive content |
| **Deep Review** | `research-backed-criteria.md` | 6 criteria: XML tags, example quality, defect taxonomy, anti-patterns, formatting, HELM metrics |

### Grade Definitions

**Grade A** -- All of these must be true:

| Requirement | How to verify |
|-------------|---------------|
| SKILL.md under 400 lines | `wc -l SKILL.md` |
| Frontmatter: `name` valid, `description` third-person with "Use when..." triggers | Checklist items 1-2 above |
| `context: fork` correctly applied (present for Class A autonomous; absent for Class B orchestrator, Class C interactive, Class D mode-style) | Checklist item 3 above |
| Only SKILL.md in skill root; references in `references/` | File structure checks above |
| 0 major issues, 0 minor issues | See issue classification below |
| 3-5 diverse examples in `<example>` tags | Deep review criterion 2 |
| `<instructions>` tags wrap core directives | Deep review criterion 1 |
| Every multi-step workflow has a verification step | Content quality dimension 6 |
| 0 contradictions within or across files | Content quality dimension 7 |
| All 6 deep review criteria pass | `research-backed-criteria.md` |

**Grade B** -- All of these must be true:

| Requirement | How to verify |
|-------------|---------------|
| SKILL.md under 500 lines | `wc -l SKILL.md` |
| Frontmatter passes all required field checks | Checklist items 1-3 above |
| 0 major issues | See issue classification below |
| 1-2 minor issues maximum | See issue classification below |
| At least 4 of 6 deep review criteria pass | `research-backed-criteria.md` |
| At least 6 of 8 content quality dimensions pass | `content-quality-checklist.md` |

**Grade C** -- Exactly 1 major issue:

| Requirement | How to verify |
|-------------|---------------|
| Exactly 1 major issue | See issue classification below |
| No more than 3 minor issues alongside | Count from all layers |
| Core instructions are executable (not entirely vague) | Content quality dimension 3 |

**Grade D** -- 2 or more major issues:

| Requirement | How to verify |
|-------------|---------------|
| 2-3 major issues from any categories | See issue classification below |
| OR 1 major issue + 4 or more minor issues | Combined count from all layers |
| Skill is still structurally parseable (valid YAML, SKILL.md exists) | Basic file checks |

**Grade F** -- Any of these is true:

| Trigger | Example |
|---------|---------|
| `description` field missing or empty | No frontmatter description at all |
| SKILL.md missing or unparseable YAML | Broken `---` delimiters, invalid syntax |
| 4+ major issues | Failures across most evaluation layers |
| Core instructions are fundamentally unactionable | Every directive uses "consider", "ensure", "as needed" with no defaults |
| Skill body is empty or contains only frontmatter | No instructions for Claude to follow |

### Issue Classification

**Major issues** (each drops grade by one full letter from A):

| # | Issue | Layer | Detection |
|---|-------|-------|-----------|
| M1 | SKILL.md over 500 lines | Structural | `wc -l SKILL.md` exceeds 500 |
| M2 | `context: fork` incorrectly applied | Structural | Class A missing `context: fork`, OR Class B/C/D has it when it should not. See the four-class taxonomy in frontmatter checklist item 3 above. |
| M3 | Wrong degrees of freedom for task type | Content | Fragile operation with vague instructions, or flexible task over-constrained (dimension 1) |
| M4 | No feedback loop for destructive or multi-step operations | Content | Workflows with 5+ steps or destructive actions lack verification checkpoints (dimension 6) |
| M5 | Contradictions between SKILL.md and references | Content | Same topic, different guidance across files (dimension 7) |
| M6 | Scripts with bare `except:` or no error recovery | Content | Script catches all exceptions without specific handling (dimension 5) |
| M7 | Core instructions unactionable | Content | 3+ directives in `<instructions>` use only weak verbs: "consider", "ensure", "handle appropriately" (dimension 3) |
| M8 | Description not third-person or missing triggers | Structural | Imperative, second-person, or noun-phrase description; no "Use when..." clause |

**Minor issues** (each noted but only affects grade at thresholds above):

| # | Issue | Layer | Detection |
|---|-------|-------|-----------|
| m1 | Verbose explanations of concepts Claude knows | Content | Section explains common knowledge: what JSON is, what APIs are (dimension 2) |
| m2 | One decision point missing a default | Content | List of 3+ options without recommendation or "Default to X" (dimension 4) |
| m3 | One piece of time-sensitive content | Content | Specific dates in conditional logic, "currently", pinned version without note (dimension 8) |
| m4 | Inconsistent terminology | Content | Same concept called different names across files (dimension 7) |
| m5 | Missing `<example>` tags on examples | Deep | Examples present but not wrapped in XML tags (criterion 1) |
| m6 | Fewer than 3 examples or more than 10 | Deep | Count of `<example>` blocks outside 3-5 range (criterion 2) |
| m7 | SKILL.md between 400-500 lines | Structural | Line count in warning zone |
| m8 | Loose files in skill root beside SKILL.md | Structural | `.md` or other files not inside `references/`, `scripts/`, or `assets/` |

### Scoring Summary

| Grade | Major Issues | Minor Issues | Line Count |
|-------|-------------|--------------|------------|
| **A** | 0 | 0 | Under 400 |
| **B** | 0 | 1-2 | Under 500 |
| **C** | 1 | 0-3 | Any |
| **D** | 2-3, or 1 major + 4+ minor | Any | Any |
| **F** | 4+, or missing description, or broken structure | Any | Any |
