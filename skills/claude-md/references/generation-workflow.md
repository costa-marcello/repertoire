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

<!-- v1.0 | 2026-02-02 -->

Detailed workflow for Generate mode — creating CLAUDE.md files in subdirectories that benefit from instant context.

---

## Overview

Generate mode analyzes codebase structure, scores directories by "needs context" heuristics, and creates minimal CLAUDE.md files for high-value directories. User approval required before any file creation.

**Token Budgets (Critical):**

| Location | Budget | Purpose |
|----------|--------|---------|
| Root CLAUDE.md | 500-1000 tokens | Project-wide context |
| Subdirectory CLAUDE.md | 150-300 tokens | Directory-specific context |
| Total static context | <3000 tokens | Avoid context bloat |

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

### Command

```bash
find . -type d -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/dist/*' -not -path '*/__pycache__/*' -not -path '*/build/*' -not -path '*/coverage/*' -not -path '*/.next/*' -not -path '*/.nuxt/*' -not -path '*/vendor/*' | head -100
```

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
| **File count >15** | +3 | `ls -1 | wc -l` |
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

**Minimal vs Full:**
- **Minimal (score 4-5):** ~100 tokens. Context sentence + 2-3 key files. Skip Patterns unless non-obvious.
- **Full (score >=6):** ~200-300 tokens. Context + Key Files + Patterns with reasoning + Gotchas if applicable.

### Example Scoring

```
src/api/           Score: 8 (23 files +3, has index.ts +2, is API domain +2, config +1)
packages/shared/   Score: 6 (monorepo +3, 18 files +3)
src/utils/         Score: 2 (12 files, obvious naming) — SKIP
tests/             Score: 3 (obvious directory, no special patterns) — SKIP
src/services/auth/ Score: 5 (domain jargon +2, deep nesting +1, entry point +2)
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

Identify entry points and important files:

```bash
# Entry points
ls -la index.* main.* mod.* 2>/dev/null

# Config files
ls -la *.config.* tsconfig.json package.json Cargo.toml 2>/dev/null

# By file size (larger = likely more important)
ls -lS *.{ts,js,py,go,rs} 2>/dev/null | head -5
```

### 3. Patterns

Look for:
- Naming conventions (file suffixes, prefixes)
- Co-location patterns (tests with code, styles with components)
- Framework conventions (routes structure, component hierarchy)

### 4. Internal Dependencies

```bash
# Find imports to other project directories
grep -r "from '\.\./\|from \"\.\./\|import \.\./\|require('\.\./\|require(\"\.\." --include="*.{ts,js,py}" | head -10
```

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

@../CLAUDE.md

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
- [ ] Each file is 150-300 tokens
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
1. src/api/CLAUDE.md (Score: 8) — API routes context
2. packages/shared/CLAUDE.md (Score: 6) — Shared utilities
3. src/services/auth/CLAUDE.md (Score: 5) — Auth domain

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
- [ ] Content starts with @../CLAUDE.md
- [ ] Under 500 tokens
- [ ] Has Context section
- [ ] Has Key Files section
- [ ] Patterns include reasoning (if Patterns section exists)
- [ ] No root CLAUDE.md duplication
```

### Post-Creation Verification

```markdown
## Generation Complete

**Created {N} files:**
- [x] src/api/CLAUDE.md (287 tokens)
- [x] packages/shared/CLAUDE.md (203 tokens)
- [x] src/services/auth/CLAUDE.md (156 tokens)

**Total added context:** 646 tokens

**Next steps:**
- Review generated files and customize as needed
- Run `/claude-md review` to check quality
- Consider removing generic patterns, keep only project-specific
```

---

## Good vs Bad Generated Content

### Good (Directory-Specific, Patterns Have Reasoning)

```markdown
# Auth Service

@../CLAUDE.md

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

@../CLAUDE.md

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
| `tests/` | Maybe | Only if non-obvious fixtures/patterns |
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
| Copy root CLAUDE.md content | Duplication | Reference with `@../CLAUDE.md` |
| List all files | Noisy, outdated quickly | 2-5 key files only |
| Generic advice | Wastes tokens | Directory-specific only |
| Patterns without reasoning | Review mode flags as issue | Add brief "— why" |
| No user approval | Unwanted files | Always ask first |
| Verbose descriptions | Context bloat | One sentence per section |
