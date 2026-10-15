---
name: claudia-md
description: Manages CLAUDE.md files. Audits, reviews, improves, refactors, updates, and generates subdirectory context. Discovers all CLAUDE.md files, evaluates quality against research-backed criteria, generates improvement reports, applies targeted updates, syncs CLAUDE.md with current codebase state, restructures using progressive disclosure, and creates contextual CLAUDE.md files for directories that benefit from instant context. Use when the user says "audit CLAUDE.md", "review my CLAUDE.md rules", "improve instructions", "organize Claude config", "update CLAUDE.md", "sync my CLAUDE.md rules", "init CLAUDE.md", "generate subdirectory context", or "CLAUDE.md maintenance".
allowed-tools: Read, Glob, Grep, Edit, Write
license: MIT
---

<!-- v1.5.0 | 2026-10-14 -->

# Claude MD

**Complete CLAUDE.md management:** Audit, Review, Improve, Refactor, Update, and Generate. Core insight: rules with reasoning outperform bare rules. Models generalize from "why" explanations.

## Quick Reference

| Mode | When to Use | Output |
|------|-------------|--------|
| **Audit** | "Audit CLAUDE.md", "Check all my rule files" | Discovery + quality scores for all files |
| **Review** | "Review my CLAUDE.md", "Check instruction quality" | Detailed quality report + improvement suggestions |
| **Improve** | "Improve my CLAUDE.md rules", "Fix my CLAUDE.md" | Targeted updates with diffs |
| **Refactor** | "Organize Claude config", "Split CLAUDE.md" | Restructured files with progressive disclosure |
| **Update** | "Update CLAUDE.md", "Sync my CLAUDE.md rules", "Init CLAUDE.md" | CLAUDE.md synced with current codebase state |
| **Generate** | "Generate subdirectory context", "Create package CLAUDE.md files" | New CLAUDE.md files for directories that need context |

### Mode Sequencing

| Sequence | When to Use |
|----------|-------------|
| Audit → Review → Improve | Full assessment → quality check → targeted fixes |
| Audit → Generate | Gaps found in subdirectory coverage → create missing files |
| Update → Review or Improve | Sync with codebase → then grade or fix quality |
| Improve → Refactor | Fix content issues → restructure if still bloated |

### Where It Works

Every mode works on files in a folder, so it runs the same in Claude Code and Cowork.

- **Skill folder:** Use `${CLAUDE_SKILL_DIR}` unless it is blank, unexpanded, or a bundled file proves missing there. Then use the "Base directory for this skill" if it holds `references/quality-criteria.md`, else the folder two levels above the last match Glob lists for `**/claudia-md/references/quality-criteria.md` in `~/.claude`. That folder replaces `CLAUDE_SKILL_DIR` and anchors every relative bundled path. If nothing matches, work from this file and say the reference files were not read.
- **Project folder:** the current working directory in Claude Code; the connected folder in Cowork. If a Cowork session has no connected folder, ask the user to connect the folder that holds the CLAUDE.md. If they attach a single CLAUDE.md instead, work on it and save the result in the outputs folder.
- **No git or terminal needed:** find and read files with Glob, Grep, and Read. A plain folder that is not a git repository is fine.
- **User-wide file:** `~/.claude/CLAUDE.md` exists only in Claude Code. Cowork cannot read your computer's home-folder Claude config, so skip that file there, say so in the report, and offer to review it if the user pastes it or copies it into the connected folder.
- **Say where files went:** after writing, list every file created or changed with its path from the project folder root, and in Cowork say that it is in the connected folder (or the outputs folder).

---

## Workflow Overview

<instructions>

Track progress with the mode's checklist in [references/execution-checklists.md](references/execution-checklists.md).

### Phase 1: Discovery

Find all CLAUDE.md files in the project folder with Glob, using the patterns `**/CLAUDE.md`, `**/CLAUDE.local.md`, `.claude/CLAUDE.md`, and `.claude/rules/**/*.md`, and note any `**/AGENTS.md`. Drop matches under `node_modules`, `dist`, `build`, `vendor`, and `.git`. Stop at 50 files and say so when there are more. When Audit already ran in the session, Generate reuses this list for its "Already has CLAUDE.md" signal.

**File Types & Locations:**

| Type | Location | Purpose |
|------|----------|---------|
| Project root | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Primary project context |
| Local overrides | `./CLAUDE.local.md` | Personal project notes (usually gitignored) |
| Global defaults | `~/.claude/CLAUDE.md` | User-wide defaults across all projects (Claude Code only; see Where It Works) |
| Package-specific | `./packages/*/CLAUDE.md` | Module-level context in monorepos |
| Subdirectory | Any nested location | Feature/domain-specific context |
| Rules directory | `./.claude/rules/**/*.md` | Topic rules, loaded without any import |
| Reference docs | `./.claude/reference/*.md` | Large docs (a convention; NOT auto-loaded) |
| AGENTS.md | `./AGENTS.md` | By default, read by Claude Code only while no CLAUDE.md exists |

**How Claude Code loads these files** (source: the Claude Code memory docs at https://code.claude.com/docs/en/memory; recheck them when Claude Code changes, since this behavior varies between releases):
- Every CLAUDE.md from the working directory up loads at launch. A subdirectory's CLAUDE.md loads when Claude first touches a file there, so it never imports its parent.
- An `@path` import resolves relative to the file that contains it and loads at launch: it organizes a file but saves no context. So `@rules/x.md` in the root points to `./rules/`, not `.claude/rules/`.
- `.claude/rules/` files load on their own, so CLAUDE.md never imports them. A rule with `paths:` frontmatter loads only when Claude touches a matching file.
- The docs target under 200 lines per CLAUDE.md: longer files cost context in every session and reduce adherence.

### Phase 2: Quality Assessment

For each CLAUDE.md file, evaluate against the 100-point rubric.

**Six Categories (100 points total):**

| Category | Points | Core Check |
|----------|--------|------------|
| Commands/workflows | 12 | Build/test/deploy commands present |
| Architecture clarity | 12 | Codebase structure clear |
| Non-obvious patterns | 10 | Gotchas and quirks documented |
| Conciseness | 8 | No verbose or obvious info |
| Currency | 8 | Reflects current codebase |
| Content Quality | 50 | Reasoning, actionability, format (5 sub-criteria) |

**Quality Grades:** A (90-100), B (70-89), C (50-69), D (30-49), F (0-29).

See [references/quality-criteria.md](references/quality-criteria.md) for the full rubric, sub-criteria point breakdown, and bad/good examples.

<example>
**Audit mode summary output:**

```markdown
## CLAUDE.md Audit Summary

- Files found: 4
- Average score: 72/100 (Grade B)
- Files needing update: 2

| File | Score | Grade | Key Issue |
|------|-------|-------|-----------|
| ./CLAUDE.md | 88/100 | B | Missing gotchas section |
| .claude/rules/coding.md | 91/100 | A | No issues |
| packages/api/CLAUDE.md | 54/100 | C | No commands, vague patterns |
| packages/shared/CLAUDE.md | 56/100 | C | Rules lack reasoning |
```
</example>

**Rule Quality Dimensions (for Review mode):** 6 dimensions, total /13: Reasoning, Specificity, and Positive framing (0-3 each), Examples and Structure (0-2 each), and Conflicts (-1 per conflict, down to -3). Only rules/patterns/conventions get scored; factual sections (Context, Key Files, Architecture, Commands) are excluded.

### Phase 3: Quality Report Output

Output the quality report before making any updates. In Review mode, run Phase 4 first so the report lists its issues.

**Report Format:**

```markdown
## CLAUDE.md Quality Report

### Summary
- Files found: X | Average score: X/100 | Files needing update: X

### File-by-File Assessment

#### 1. ./CLAUDE.md (Project Root) — Score: XX/100 (Grade: X)

| Criterion | Score |
|-----------|-------|
| Commands/workflows | X/12 |
| Architecture clarity | X/12 |
| Non-obvious patterns | X/10 |
| Conciseness | X/8 |
| Currency | X/8 |
| Content Quality (5 sub-criteria) | X/50 |

**Issues:** [list specific problems]
**Recommended additions:** [list what should be added]
```

### Phase 4: Issue Detection (Review Mode)

**Check rules and patterns for:** (not factual context sections)

| Issue Type | Detection | Example Problem | Applies To |
|------------|-----------|-----------------|------------|
| **Missing reasoning** | No "why", "because", explanation | "Never use any" (why?) | Rules, Patterns |
| **Vague instruction** | Not actionable, no concrete guidance | "Write clean code" | Rules, Patterns |
| **Negative-only framing** | "Don't", "Never", "Avoid" without positive alternative | "Don't hardcode URLs" | Rules only |
| **No examples** | Abstract rule without concrete illustration | Complex patterns need examples | Complex rules |
| **Conflicts** | Two rules that contradict | "Use Jest" + "Use Vitest" | All |
| **Redundant** | Duplicates another rule | Same instruction in two places | All |
| **Obvious** | Model does this without instruction | "Use correct syntax" | Rules |
| **Stale commands** | Build commands that no longer work | Outdated paths or scripts | Commands |
| **Missing dependencies** | Required tools not mentioned | Setup requirements omitted | Environment |
| **Wrong import** | `@path` that does not resolve from the importing file, or imports a file that loads anyway | `@rules/x.md` in the root, `@../CLAUDE.md` | Imports |

Also check each file against [references/anti-patterns.md](references/anti-patterns.md).

**Do NOT flag as issues:**
- Context sections without "why" (factual descriptions don't need reasoning)
- Key Files without explanations (file path + purpose is sufficient)
- Architecture sections without justification (structure is factual)

### Phase 5: Targeted Updates (Improve Mode)

After outputting the quality report, ask user for confirmation before updating.

**Update Guidelines:**

| Do | Skip |
|----|------|
| Propose discovered commands, gotchas, package relationships, working test approaches, config quirks | Restate what's obvious from code, generic best practices, one-off fixes, verbose explanations |

For each change, show: target file, the diff or quoted block, and a brief "why". See [references/update-guidelines.md](references/update-guidelines.md) for the full add-vs-skip heuristics, and rewrite rules in the hybrid format from [references/rule-quality-standards.md](references/rule-quality-standards.md).

**Diff Format:**

<example>
````markdown
### Update: ./CLAUDE.md

**Why:** Build command was missing, causing confusion about how to run the project.

```diff
+ ## Quick Start
+
+ ```bash
+ npm install
+ npm run dev  # Start development server on port 3000
+ ```
```
````
</example>

### Phase 6: Refactoring (Refactor Mode)

For bloated files, restructure using progressive disclosure.

**Triage Assessment:**

| Signal | Score |
|--------|-------|
| Already uses `.claude/rules/` structure | +2 |
| Has clear hierarchy (headers, tables) | +1 |
| Contains reasoning ("why" explanations) | +1 |
| Rules are actionable and specific | +1 |
| Under 200 lines with dense content | +1 |
| Over 300 lines | -1 |
| Wall-of-text without structure | -2 |
| Contains contradictions | -2 |
| Mix of vague and specific rules | -1 |

| Score | Action |
|-------|--------|
| 4+ | **Skip** — already well-organized |
| 2-3 | **Light** — extract verbose sections |
| 0-1 | **Standard** — full refactoring |
| Negative | **Deep** — significant restructuring |

<example>
**Refactor triage output:**

```markdown
## Triage: ./CLAUDE.md (380 lines)

| Signal | Score |
|--------|-------|
| Uses `.claude/rules/` | 0 |
| Clear hierarchy | +1 |
| Has reasoning | 0 |
| Actionable rules | +1 |
| Length | -1 (>300) |
| Mix of vague and specific | -1 |

**Total: 0 → Decision: Standard refactoring**

Plan: Extract coding rules to `.claude/rules/coding.md`, add reasoning to bare directives, move testing patterns to `.claude/rules/testing.md` with `paths: ["**/*.test.ts"]`.
```
</example>

**Keep in root (high-value, frequently referenced):**

| Category | Example | Why Keep |
|----------|---------|----------|
| Project description | "React dashboard for analytics" | Sets context for all tasks |
| Commands | `pnpm build`, `pnpm test` | Used every session |
| Hard rules with reasoning | "Never commit secrets — in git history forever" | Safety reinforcement |
| Core principles (3-5) | "Type safety first", "Test behavior not implementation" | Philosophy that guides decisions |
| Priority hierarchy | "Safety > Core Principles > Style" | Conflict resolution |
| Pointers to reference docs | "API details: `.claude/reference/api.md`" | Reference docs never load on their own |

**Extract to `.claude/rules/` (detailed, topic-specific):**
- Detailed language conventions with examples
- Extensive testing patterns
- Framework-specific guidance
- Comprehensive workflow documentation
- Reference tables and checklists

A rule without `paths:` frontmatter loads every session, so splitting alone saves no context. Give a rule that matters for only part of the codebase a `paths:` glob (for example `"src/api/**/*.ts"`) so it loads only when Claude works on matching files.

**Output structure:**
```
project-root/
├── CLAUDE.md                     # High-value content, no imports of rules
└── .claude/
    ├── rules/                    # Loaded by Claude Code; paths: rules on demand
    │   ├── coding.md
    │   ├── testing.md
    │   ├── workflow.md
    │   └── safety.md
    └── reference/                # NOT auto-loaded; CLAUDE.md points to it
        └── patterns.md
```

### Phase 7: Apply Updates

After user approval, apply changes with the Edit tool (Write for new files). Preserve existing content structure. Then re-read each changed file to confirm the edits landed, and list the files with their paths (see Where It Works).

### Mode: Update (Sync CLAUDE.md with Codebase)

**Triggers:** "Update CLAUDE.md", "Sync my CLAUDE.md rules", "Init CLAUDE.md", "Refresh project context"

Scans the codebase and updates CLAUDE.md to reflect the current project state. Creates a CLAUDE.md from scratch if none exists. Unlike Improve (which fixes quality issues), Update detects drift between the documented state and the actual codebase. Unlike the built-in `/init`, it previews every change, keeps user-authored rules, and imports an existing AGENTS.md.

| Phase | Action | Detail |
|-------|--------|--------|
| U1 | Codebase Scan | Detect package manager, scripts/commands, directory structure, frameworks, config files, environment vars. |
| U2 | Existing CLAUDE.md Read | Read current CLAUDE.md (if any). If none exists, treat all discovered info as new, and when an `AGENTS.md` exists, start the new file with `@AGENTS.md`: Claude Code stops reading AGENTS.md once a CLAUDE.md exists. |
| U3 | Drift Detection | Compare documented state against discovered state. Flag stale commands, missing sections, outdated structure, removed files. |
| U4 | Change Preview | Show additions, updates, and removals as a diff. Never auto-apply. |
| U5 | User Approval | Present changes for approval. Support approve all, select specific, or cancel. |
| U6 | Apply Updates | Write approved changes, then re-read each file. Preserve existing reasoning, rules, and user-authored content. A new file goes to `CLAUDE.md` at the project folder root; say where it went. |

**Key principle:** Update adds and corrects factual content (commands, structure, files). It never removes or rewrites user-authored rules, reasoning, or principles unless they reference things that no longer exist.

See [references/update-workflow.md](references/update-workflow.md) for the full scanning algorithm, detection heuristics, and framework-specific patterns.

<example>
**Update mode preview output:**

```markdown
## CLAUDE.md Update Preview

**Codebase scan results:** Node.js project, pnpm, Next.js 15, TypeScript

### Additions (new sections)
+ ## Commands
+ | `pnpm dev` | Start dev server |
+ | `pnpm build` | Production build |
+ | `pnpm test` | Run vitest |
+ | `pnpm lint` | ESLint check |

+ ## Architecture
+ src/app/        # Next.js app router pages
+ src/lib/        # Shared utilities
+ src/components/ # React components

### Updates (changed content)
~ ## Key Files
~ - `src/lib/db.ts` → renamed to `src/lib/database.ts`
~ - Removed reference to deleted `src/utils/legacy.ts`

### No changes
= ## Hard Rules (unchanged, user-authored)
= ## Core Principles (unchanged, user-authored)

Apply these changes? [All / Select / Cancel]
```
</example>

### Mode: Generate (Create Subdirectory Context)

**Triggers:** "Generate subdirectory context", "Create CLAUDE.md for packages", "Add directory context files"

**Workflow:** Scan directories, score by "needs context" heuristics, generate minimal CLAUDE.md files for high-value directories, get user approval before creating any files.

| Phase | Action | Detail |
|-------|--------|--------|
| G1 | Directory Discovery | Scan structure, skip `node_modules`, `dist`, `.git`, etc. Reuse Audit's file list, if any, to spot directories that already have a CLAUDE.md. |
| G2 | Directory Scoring | Score each directory (file count, entry points, naming clarity, monorepo signals). Threshold: >=6 full, 4-5 minimal, <4 skip. |
| G3 | Content Extraction | Extract purpose, key files, patterns, dependencies, gotchas from each candidate. |
| G4 | Preview Generation | Show proposed files with scores and content. |
| G5 | User Approval | Present options: approve all, select specific, modify, or cancel. Never auto-create. |
| G6 | File Creation | Write approved files, then re-read each one. Verify: no `@` import of a parent CLAUDE.md (it loads already), under 500 tokens, no root duplication. List each created path. |

See [references/generation-workflow.md](references/generation-workflow.md) for the full scoring algorithm, extraction heuristics, and framework-specific guidance.

<example>
**Generate mode preview output:**

```markdown
## Proposed Subdirectory CLAUDE.md Files

### 1. src/api/CLAUDE.md (Score: 7)
**Reason:** 23 files (+3), index.ts entry point (+2), config file (+1), README (+1)

**Content:**
# API Layer

## Context
Express routes with Zod validation. All routes require auth middleware.

## Key Files
- `index.ts` - Route registration
- `middleware/auth.ts` - JWT validation

## Patterns
- One route file per resource — keeps routing predictable
- Validation schemas co-located with routes — easier to maintain

## Gotchas
- Rate limiting applies per-user, not per-IP
```
</example>

</instructions>

---

## References

| File | Read when |
|------|-----------|
| `references/quality-criteria.md` | Phase 2: scoring a file on the 100-point rubric and the rule quality dimensions |
| `references/anti-patterns.md` | Phase 4: checking a file against common mistakes |
| `references/update-guidelines.md` | Phase 5: deciding what to add and what to skip |
| `references/rule-quality-standards.md` | Phase 5 and Refactor: rewriting a rule (hybrid format, positive reframing, what to preserve) |
| `references/templates.md` | Writing a root, subdirectory, monorepo, or rule file, or the triage and completion reports |
| `references/examples.md` | Refactor: before/after transformations |
| `references/execution-checklists.md` | Any mode: tracking progress phase by phase |
| `references/update-workflow.md` | Update mode: scanning, drift detection, and framework signals |
| `references/generation-workflow.md` | Generate mode: directory scoring and content extraction |
| `references/subdirectory-examples.md` | Generate mode or a hand-crafted subdirectory file: real examples |
