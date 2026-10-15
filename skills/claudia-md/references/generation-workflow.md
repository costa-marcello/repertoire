# Generation Workflow

## Contents

1. [Overview](#overview)
2. [Phase G1: Directory Discovery](#phase-g1-directory-discovery)
3. [Phase G2: Directory Scoring](#phase-g2-directory-scoring)
4. [Phase G3: Content Extraction](#phase-g3-content-extraction)
5. [Phase G4: Preview Generation](#phase-g4-preview-generation)
6. [Phase G5: User Approval](#phase-g5-user-approval)
7. [Phase G6: File Creation](#phase-g6-file-creation)
8. [Good vs Bad Generated Content](#good-vs-bad-generated-content)
9. [Framework-Specific Heuristics](#framework-specific-heuristics)
10. [Common Mistakes to Avoid](#common-mistakes-to-avoid)

<!-- v1.1 | 2026-10-14 -->

Detailed workflow for Generate mode — creating CLAUDE.md files in subdirectories that benefit from instant context.

---

## Overview

Generate mode analyzes codebase structure, scores directories by "needs context" heuristics, and creates minimal CLAUDE.md files for high-value directories. User approval required before any file creation.

**How a subdirectory file loads:** Claude Code loads every CLAUDE.md from the working directory up at launch, and loads a subdirectory's CLAUDE.md when Claude first reads or edits a file in that directory. A generated file therefore never imports its parent: `@../CLAUDE.md` would load the parent twice, and an import resolves relative to the importing file, so in `src/api/` it would point to `src/CLAUDE.md`, not the root. Source: the Claude Code memory docs (https://code.claude.com/docs/en/memory); recheck them when Claude Code changes.

**Size Budgets:** this table is the single source for generated-file sizes.

| Location | Budget | Purpose |
|----------|--------|---------|
| Root CLAUDE.md | Under 200 lines (the Claude Code docs' target) | Project-wide context |
| Subdirectory CLAUDE.md, minimal (score 4-5) | About 100 tokens | Context + Key Files |
| Subdirectory CLAUDE.md, full (score 6+) | 150-300 tokens | Adds Patterns and Gotchas |
| Any generated file | Never over 500 tokens | Hard cap |

**Token Estimation (Rule of Thumb):**

| Tokens | Approx. Words | Approx. Lines |
|--------|---------------|---------------|
| 100 | ~75 words | ~8-10 lines |
| 150 | ~110 words | ~12-15 lines |
| 300 | ~225 words | ~25-30 lines |
| 500 | ~375 words | ~40-50 lines |

**Quick check:** 1 token ≈ 0.75 words. Count words, multiply by 1.33 for tokens.

Example: Auth Service file with ~100 words ≈ ~130 tokens ✓

---

## Phase G1: Directory Discovery

### Method

Glob returns files, not directories. Glob `**/*`, take the parent directory of each file path, and drop the skip list below. When the result is truncated, Glob each top-level directory in turn (`<dir>/**/*`). This works in Claude Code and Cowork, with or without a shell. Stop at 100 directories and say so when there are more.

### Skip List

Always skip these directories:

| Pattern | Reason |
|---------|--------|
| `.git`, `.svn` | Version control |
| `node_modules`, `vendor` | Dependencies |
| `dist`, `build`, `out` | Build output |
| `coverage`, `.nyc_output` | Test coverage |
| `.next`, `.nuxt`, `.svelte-kit` | Framework cache |
| `__pycache__`, `.pytest_cache` | Python cache |
| `.venv`, `venv`, `env` | Virtual environments |

---

## Phase G2: Directory Scoring

### Scoring Algorithm

Calculate "needs context" score for each directory:

| Signal | Score | Detection Method |
|--------|-------|------------------|
| **File count >15** | +3 | Glob `<dir>/*` and count the files |
| **Has entry point** | +2 | `index.{ts,js,py}`, `main.{py,go,rs}`, `mod.rs` |
| **Non-obvious naming** | +2 | Abbreviations (`src/svc`), jargon (`src/dal`), single letters |
| **Deep nesting (>3 levels)** | +1 | Path depth from project root |
| **Has config file** | +1 | `tsconfig.json`, `package.json`, `.env.example`, `Cargo.toml` |
| **Is monorepo package** | +3 | Under `packages/`, `apps/`, `services/`, `libs/` |
| **Has README** | +1 | Existing documentation to extract from |
| **Already has CLAUDE.md** | -10 | Skip — already documented |
| **Framework standard dir** | -5 | `public/`, `static/`, `assets/` — structure is obvious |
| **Shallow with few files** | -2 | <5 files, no nesting — not complex enough |

### Threshold Decision

| Score | Action | Content |
|-------|--------|---------|
| >= 6 | **High priority** | Full: Context + Key Files + Patterns (with reasoning) + Gotchas |
| 4-5 | **Medium priority** | Minimal: Context + Key Files only; skip Patterns if obvious |
| < 4 | **Skip** | No generation — directory is self-explanatory |

**Minimal vs Full** (sizes from the Size Budgets table):
- **Minimal (score 4-5):** Context sentence + 2-3 key files. Skip Patterns unless non-obvious.
- **Full (score >=6):** Context + Key Files + Patterns with reasoning + Gotchas if applicable.

### Example Scoring

Every point comes from a signal in the table above:

```
src/api/            Score: 7 (23 files +3, index.ts +2, config file +1, README +1)
packages/shared/    Score: 6 (monorepo package +3, 18 files +3)
src/svc/authz/      Score: 5 (abbreviated names +2, index.ts +2, .env.example +1)
tests/              Score: 3 (18 files +3) — SKIP
src/utils/          Score: 2 (index.ts +2; 12 files, obvious name) — SKIP
```

---

## Phase G3: Content Extraction

For each candidate directory, gather:

### 1. Purpose

| Source | Priority | Method |
|--------|----------|--------|
| README.md | High | Read first paragraph |
| package.json `description` | High | Parse JSON |
| Top-level docstring | Medium | Read first file's header comment |
| Directory name + structure | Low | Infer from naming |

### 2. Key Files

Identify entry points and important files with Glob, inside the candidate directory:

| Look for | Glob pattern |
|----------|--------------|
| Entry points | `index.*`, `main.*`, `mod.*` |
| Config files | `*.config.*`, `tsconfig.json`, `package.json`, `Cargo.toml` |
| Source files | `*.{ts,js,py,go,rs}`; prefer the ones other directories import (step 4) |

### 3. Patterns

Look for:
- Naming conventions (file suffixes, prefixes)
- Co-location patterns (tests with code, styles with components)
- Framework conventions (routes structure, component hierarchy)

### 4. Internal Dependencies

Find imports that reach other project directories with Grep, using the pattern `from ['"]\.\./|require\(['"]\.\./|from \.\.` and the glob `*.{ts,js,py}`. Read the first 10 matches.

### 5. Gotchas

Non-obvious things to document:
- Unusual file organization
- Required environment setup
- Ordering dependencies
- Framework-specific quirks

### Extraction Fallback Guidance

When a directory lacks clear metadata:

| Missing | Fallback Action |
|---------|-----------------|
| No README | Use directory name + first file's header comment/docstring |
| No package.json | Not a package — check if directory still merits context |
| No clear purpose | Reduce score by 1; if still >=4, use directory name as Context |
| No entry point | List largest files by size as Key Files |
| Empty directory | Skip entirely — nothing to document |
| Only config files | Skip — configuration is self-documenting |
| Generated code only | Skip — generated files shouldn't need manual context |

**Edge case handling:**
- If extraction yields <50 tokens of useful content: skip generation for this directory
- If all key files are symlinks: note symlink target in Key Files
- If directory contains only tests: skip (covered by testing conventions in root)

---

## Phase G4: Preview Generation

### Template for Preview

```markdown
## Proposed Subdirectory CLAUDE.md Files

### 1. {path}/CLAUDE.md (Score: {score})
**Reason:** {scoring_explanation}

**Content:**
# {Directory Name}

## Context
{one_sentence_purpose}

## Key Files
- `{file}` - {purpose}
- `{file}` - {purpose}

## Patterns
- {pattern} — {brief_why}

## Gotchas
- {non_obvious_thing} (if any)

---

### 2. {next_directory}...
```

### Preview Quality Checklist

Before showing preview:
- [ ] Each file fits the Size Budgets table: about 100 tokens (minimal) or 150-300 (full), never over 500
- [ ] No `@` import of a parent CLAUDE.md
- [ ] Context is one sentence, not a paragraph
- [ ] Key Files lists 2-5 files (not exhaustive)
- [ ] Patterns are directory-specific, not project-wide
- [ ] Patterns include brief reasoning ("— why")
- [ ] No duplicate info from root CLAUDE.md
- [ ] No generic advice ("write clean code")

---

## Phase G5: User Approval

Present clear options:

```markdown
## Ready to Generate {N} Files

**Proposed files:**
1. src/api/CLAUDE.md (Score: 7) — API routes context
2. packages/shared/CLAUDE.md (Score: 6) — Shared utilities
3. src/svc/authz/CLAUDE.md (Score: 5) — Authorization domain

**Options:**
- [A] Approve all — create all {N} files
- [S] Select — choose specific files to create
- [M] Modify — request changes before creation
- [C] Cancel — abort generation
```

**Never auto-create.** User must explicitly approve.

---

## Phase G6: File Creation

### Creation Checklist

For each approved file:

```
- [ ] Parent directory exists
- [ ] No existing CLAUDE.md (double-check)
- [ ] No `@../CLAUDE.md` or other import of a parent CLAUDE.md
- [ ] Under 500 tokens
- [ ] Has Context section
- [ ] Has Key Files section
- [ ] Patterns include reasoning (if Patterns section exists)
- [ ] No root CLAUDE.md duplication
```

### Post-Creation Verification

Re-read each created file and check it against the list above, then report:

```markdown
## Generation Complete

**Created {N} files:**
- [x] src/api/CLAUDE.md (287 tokens)
- [x] packages/shared/CLAUDE.md (203 tokens)
- [x] src/svc/authz/CLAUDE.md (96 tokens)

**Total added context:** 586 tokens, each loaded only when Claude works in that directory

**Next steps:**
- Review generated files and customize as needed
- Run `/repertoire:claudia-md review` (or `/claudia-md review` when the skill is installed on its own) to check quality
- Consider removing generic patterns, keep only project-specific
```

---

## Good vs Bad Generated Content

### Good (Directory-Specific, Patterns Have Reasoning)

```markdown
# Auth Service

## Context
JWT-based authentication with Redis session storage. Handles login, logout, token refresh.

## Key Files
- `index.ts` - Service exports
- `jwt.ts` - Token generation/validation
- `middleware.ts` - Express auth middleware

## Patterns
- All tokens expire in 1 hour — balances security with UX
- Refresh tokens stored in Redis with 7-day TTL — survives server restarts

## Gotchas
- Redis must be running locally for tests
```

### Bad (Generic, No Reasoning on Patterns)

```markdown
# Auth Service

## Context
This directory contains the authentication service for the application. It is responsible for handling user authentication, including login, logout, and session management. The service uses modern security practices and follows industry standards for authentication.

## Key Files
- `index.ts` - The main entry point for the auth service module
- `jwt.ts` - Handles JWT token operations
- `middleware.ts` - Middleware functions
- `types.ts` - TypeScript types
- `utils.ts` - Utility functions
- `constants.ts` - Constants
- `errors.ts` - Error classes
- `validators.ts` - Validation logic

## Patterns
- Use TypeScript for type safety
- Follow clean code principles
- Write tests for all functions
- Use meaningful variable names

## Gotchas
- Make sure to handle errors properly
- Don't forget to validate inputs
```

**Problems with bad example:**
- Verbose Context (should be one sentence)
- Lists every file instead of key files only
- Generic patterns that apply everywhere
- Patterns lack reasoning (no "why")
- Gotchas are obvious advice, not directory-specific

---

## Framework-Specific Heuristics

### React/Next.js

| Directory | Generate? | Focus On |
|-----------|-----------|----------|
| `src/components/` | Yes if >10 components | Component patterns, props conventions |
| `src/hooks/` | Yes if custom hooks | Hook naming, dependency patterns |
| `src/pages/` or `app/` | No | Structure is Next.js standard |
| `src/lib/` | Yes if non-obvious | What utilities exist, when to use |

### Python

| Directory | Generate? | Focus On |
|-----------|-----------|----------|
| `src/{domain}/` | Yes for domains | Business logic, models |
| `tests/` | No | Covered by the root's testing conventions (see Extraction Fallback Guidance) |
| `scripts/` | Yes if many | What each script does |
| `migrations/` | No | Structure is framework standard |

### Go

| Directory | Generate? | Focus On |
|-----------|-----------|----------|
| `internal/` | Yes per package | Package responsibilities |
| `cmd/` | Yes if multiple binaries | What each binary does |
| `pkg/` | Yes for public packages | API, usage examples |

### Monorepo

| Directory | Generate? | Focus On |
|-----------|-----------|----------|
| `packages/*/` | Yes for each | Package purpose, exports |
| `apps/*/` | Yes for each | App-specific config, env vars |
| `services/*/` | Yes for each | Service responsibilities, API |
| `libs/*/` | Yes for shared libs | What's exported, who uses it |

---

## Common Mistakes to Avoid

| Mistake | Why It's Bad | Instead |
|---------|--------------|---------|
| Generate for every directory | Context bloat | Only score >= 4 |
| Copy root CLAUDE.md content | Duplication | Leave it out: Claude Code loads the root file already |
| Import the parent with `@../CLAUDE.md` | Loads the parent twice, or the wrong file in a nested directory | No import; ancestors load on their own |
| List all files | Noisy, outdated quickly | 2-5 key files only |
| Generic advice | Wastes tokens | Directory-specific only |
| Patterns without reasoning | Review mode flags as issue | Add brief "— why" |
| No user approval | Unwanted files | Always ask first |
| Verbose descriptions | Context bloat | One sentence per section |
