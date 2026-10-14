---
name: claudia-md
description: Manages CLAUDE.md files. Audits, reviews, improves, refactors, updates, and generates subdirectory context. Discovers all CLAUDE.md files, evaluates quality against research-backed criteria, generates improvement reports, applies targeted updates, syncs CLAUDE.md with current codebase state, restructures using progressive disclosure, and creates contextual CLAUDE.md files for directories that benefit from instant context. Use when the user says "audit CLAUDE.md", "review my rules", "improve instructions", "organize Claude config", "update CLAUDE.md", "sync my rules", "init project", "generate subdirectory context", or "CLAUDE.md maintenance".
allowed-tools: Read, Glob, Grep, Bash, Edit, Write
license: MIT
---

<!-- v1.4.0 | 2026-10-14 -->

# Claude MD

**Complete CLAUDE.md management:** Audit, Review, Improve, Refactor, Update, and Generate. Core insight: rules with reasoning outperform bare rules. Models generalize from "why" explanations.

## Quick Reference

| Mode | When to Use | Output |
|------|-------------|--------|
| **Audit** | "Audit CLAUDE.md", "Check all my rule files" | Discovery + quality scores for all files |
| **Review** | "Review my CLAUDE.md", "Check instruction quality" | Detailed quality report + improvement suggestions |
| **Improve** | "Improve my rules", "Fix my CLAUDE.md" | Targeted updates with diffs |
| **Refactor** | "Organize Claude config", "Split CLAUDE.md" | Restructured files with progressive disclosure |
| **Update** | "Update CLAUDE.md", "Sync my rules", "Init project" | CLAUDE.md synced with current codebase state |
| **Generate** | "Generate subdirectory context", "Create package CLAUDE.md files" | New CLAUDE.md files for directories that need context |

### Mode Sequencing

Common workflow combinations:

| Sequence | When to Use |
|----------|-------------|
| Audit → Review → Improve | Full assessment → quality check → targeted fixes |
| Audit → Generate | Gaps found in subdirectory coverage → create missing files |
| Update → Review or Improve | Sync with codebase → then grade or fix quality |
| Improve → Refactor | Fix content issues → restructure if still bloated |

Generate reuses Phase 1 discovery when Audit already ran in the same session.

### Where It Works

Every mode works on files in a folder, so it runs the same in Claude Code and Cowork.

- **Project folder:** the current working directory in Claude Code; the connected folder in Cowork. If a Cowork session has no connected folder, ask the user to connect the folder that holds the CLAUDE.md. If they attach a single CLAUDE.md instead, work on it and save the result in the outputs folder.
- **No git or terminal needed:** find and read files with Glob, Grep, and Read. A plain folder that is not a git repository is fine.
- **User-wide file:** `~/.claude/CLAUDE.md` exists only in Claude Code. Cowork cannot read the home folder's Claude config, so skip that file there, say so in the report, and offer to review it if the user pastes it or copies it into the connected folder.
- **Say where files went:** after writing, list every file created or changed with its path from the project folder root, and in Cowork say that it is in the connected folder (or the outputs folder).

---

## Workflow Overview

<instructions>

### Phase 1: Discovery

Find all CLAUDE.md files in the project folder with Glob, using the patterns `**/CLAUDE.md`, `**/CLAUDE.local.md`, `.claude/CLAUDE.md`, and `.claude/rules/**/*.md`. Drop matches under `node_modules`, `dist`, `build`, `vendor`, and `.git`. Stop at 50 files and say so when there are more.

**File Types & Locations:**

| Type | Location | Purpose |
|------|----------|---------|
| Project root | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Primary project context |
| Local overrides | `./CLAUDE.local.md` | Personal project notes (usually gitignored) |
| Global defaults | `~/.claude/CLAUDE.md` | User-wide defaults across all projects (Claude Code only; see Where It Works) |
| Package-specific | `./packages/*/CLAUDE.md` | Module-level context in monorepos |
| Subdirectory | Any nested location | Feature/domain-specific context |
| Rules directory | `./.claude/rules/*.md` | Auto-loaded detailed rules |
| Reference docs | `./.claude/reference/*.md` | Large docs (NOT auto-loaded) |

**Note:** Claude auto-discovers CLAUDE.md files in parent directories, making monorepo setups work automatically.

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

**Rule Quality Dimensions (for Review mode):** 6 dimensions scored 0-3 — Reasoning, Specificity, Positive framing, Examples, Structure, Conflicts. Only rules/patterns/conventions get scored; factual sections (Context, Key Files, Architecture, Commands) are excluded. Full scoring table and "what needs reasoning vs what doesn't" examples in [references/quality-criteria.md](references/quality-criteria.md).

### Phase 3: Quality Report Output

Output the quality report before making any updates.

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

For each change, show: target file, the diff or quoted block, and a brief "why". See [references/update-guidelines.md](references/update-guidelines.md) for the full add-vs-skip heuristics.

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
| Wall-of-text | -2 |

**Total: -1 → Decision: Standard refactoring**

Plan: Extract coding rules to `.claude/rules/coding.md`, add reasoning to bare directives, move testing patterns to `.claude/rules/testing.md`.
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
| Critical @rules references | `@rules/safety.md` | Loads detailed content |

**Extract to `.claude/rules/` (detailed, topic-specific):**
- Detailed language conventions with examples
- Extensive testing patterns
- Framework-specific guidance
- Comprehensive workflow documentation
- Reference tables and checklists

**Output structure:**
```
project-root/
├── CLAUDE.md                     # High-value content with @references
└── .claude/
    ├── rules/                    # Auto-loaded by Claude Code
    │   ├── coding.md
    │   ├── testing.md
    │   ├── workflow.md
    │   └── safety.md
    └── reference/                # NOT auto-loaded (search-triggered)
        └── patterns.md
```

### Phase 7: Apply Updates

After user approval, apply changes with the Edit tool (Write for new files). Preserve existing content structure. Then re-read each changed file to confirm the edits landed, and list the files with their paths (see Where It Works).

### Mode: Update (Sync CLAUDE.md with Codebase)

**Triggers:** "Update CLAUDE.md", "Sync my rules", "Init project", "Refresh project context"

Scans the codebase and updates CLAUDE.md to reflect the current project state. Creates a CLAUDE.md from scratch if none exists. Unlike Improve (which fixes quality issues), Update detects drift between the documented state and the actual codebase.

| Phase | Action | Detail |
|-------|--------|--------|
| U1 | Codebase Scan | Detect package manager, scripts/commands, directory structure, frameworks, config files, environment vars. |
| U2 | Existing CLAUDE.md Read | Read current CLAUDE.md (if any). If none exists, treat all discovered info as new. |
| U3 | Drift Detection | Compare documented state against discovered state. Flag stale commands, missing sections, outdated structure, removed files. |
| U4 | Change Preview | Show additions, updates, and removals as a diff. Never auto-apply. |
| U5 | User Approval | Present changes for approval. Support approve all, select specific, or cancel. |
| U6 | Apply Updates | Write approved changes. Preserve existing reasoning, rules, and user-authored content. A new file goes to `CLAUDE.md` at the project folder root; say where it went. |

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
| G1 | Directory Discovery | Scan structure, skip `node_modules`, `dist`, `.git`, etc. Reuse Audit discovery if already run. |
| G2 | Directory Scoring | Score each directory (file count, entry points, naming clarity, monorepo signals). Threshold: >=6 full, 4-5 minimal, <4 skip. |
| G3 | Content Extraction | Extract purpose, key files, patterns, dependencies, gotchas from each candidate. |
| G4 | Preview Generation | Show proposed files with scores and content. |
| G5 | User Approval | Present options: approve all, select specific, modify, or cancel. Never auto-create. |
| G6 | File Creation | Write approved files. Verify: starts with `@../CLAUDE.md`, under 500 tokens, no root duplication. List each created path. |

See [references/generation-workflow.md](references/generation-workflow.md) for the full scoring algorithm, extraction heuristics, and framework-specific guidance.

<example>
**Generate mode preview output:**

```markdown
## Proposed Subdirectory CLAUDE.md Files

### 1. src/api/CLAUDE.md (Score: 7)
**Reason:** 23 files, has index.ts, API domain

**Content:**
# API Layer

@../CLAUDE.md

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

| File | Purpose |
|------|---------|
| `references/rule-quality-standards.md` | Hybrid format, transformation examples, positive reframing, preservation rules |
| `references/quality-criteria.md` | 100-point scoring rubric and rule quality dimensions |
| `references/templates.md` | CLAUDE.md templates for root, subfolder, monorepo, and rule files |
| `references/examples.md` | Before/after refactoring transformations |
| `references/anti-patterns.md` | Common mistakes to avoid when writing CLAUDE.md files |
| `references/execution-checklists.md` | Mode-specific progress checklists (Audit, Review, Improve, Refactor, Update, Generate) |
| `references/update-workflow.md` | Detailed Update mode scanning algorithm, detection heuristics, and framework patterns |
| `references/generation-workflow.md` | Detailed Generate mode scoring algorithm and extraction heuristics |
| `references/subfolder-examples.md` | Real-world subfolder CLAUDE.md examples |
| `references/update-guidelines.md` | What to add vs what to skip when updating CLAUDE.md files |
