# CLAUDE.md Templates

## Contents

1. [Key Principles](#key-principles)
2. [Recommended Sections](#recommended-sections)
3. [Template: Root CLAUDE.md (Research-Backed)](#template-root-claudemd-research-backed)
4. [Template: Project Root (Minimal)](#template-project-root-minimal)
5. [Template: Project Root (Comprehensive)](#template-project-root-comprehensive)
6. [Template: Rule File (.claude/rules/*.md)](#template-rule-file-clauderulesmd)
7. [Template: Hand-Crafted Subdirectory CLAUDE.md](#template-hand-crafted-subdirectory-claudemd)
8. [Template: Generated Subdirectory (Minimal)](#template-generated-subdirectory-minimal)
9. [Template: Package/Module (Monorepo)](#template-packagemodule-monorepo)
10. [Template: Monorepo Root](#template-monorepo-root)
11. [Template: Triage Assessment](#template-triage-assessment)
12. [Template: Refactoring Complete](#template-refactoring-complete)
13. [Update Principles](#update-principles)

Templates for CLAUDE.md structure. These are **examples**, not mandates — adapt to your project's needs.

**Key principle:** Include reasoning ("why") with rules, and keep each CLAUDE.md under about 200 lines, the target in the Claude Code docs: every line loads in every session, and longer files reduce adherence.

**Which root template:** default to [Project Root (Minimal)](#template-project-root-minimal); Update mode uses it for every new CLAUDE.md. Use [Project Root (Comprehensive)](#template-project-root-comprehensive) when the scan finds environment variables, a test setup, or code-style config worth recording. Use [Root CLAUDE.md (Research-Backed)](#template-root-claudemd-research-backed) when the user supplies hard rules and principles, or when Refactor rebuilds a root that already has them.

---

## Key Principles

- **Concise**: Dense, human-readable content; one line per concept when possible
- **Actionable**: Commands should be copy-paste ready
- **Project-specific**: Document patterns unique to this project, not generic advice
- **Current**: All info should reflect actual codebase state
- **Reasoned**: Rules include "why" to enable generalization

---

## Recommended Sections

Use only the sections relevant to the project. Not all sections are needed.

### Commands

Document the essential commands for working with the project.

```markdown
## Commands

| Command | Description |
|---------|-------------|
| `<install command>` | Install dependencies |
| `<dev command>` | Start development server |
| `<build command>` | Production build |
| `<test command>` | Run tests |
| `<lint command>` | Lint/format code |
```

### Hard Rules

Document non-negotiable constraints with reasoning.

```markdown
## Hard Rules

| Rule | Why |
|------|-----|
| Never commit secrets | In git history forever; rotation expensive |
| Never force-push main | Rewrites shared history; breaks teammates |
| Never retry auth errors | Won't fix; wastes quota; may trigger lockouts |
```

### Core Principles

Document guiding philosophy with reasoning.

```markdown
## Core Principles

- **Principle 1** — Brief explanation of why this matters
- **Principle 2** — Brief explanation of why this matters
- **Principle 3** — Brief explanation of why this matters
```

### Architecture

Describe the project structure so Claude understands where things live.

```markdown
## Architecture

```
<root>/
  <dir>/    # <purpose>
  <dir>/    # <purpose>
  <dir>/    # <purpose>
```
```

### Key Files

List important files that Claude should know about.

```markdown
## Key Files

- `<path>` - <purpose>
- `<path>` - <purpose>
```

### Code Style

Document project-specific coding conventions.

```markdown
## Code Style

- <convention>
- <convention>
- <preference over alternative>
```

### Environment

Document required environment variables and setup.

```markdown
## Environment

Required:
- `<VAR_NAME>` - <purpose>
- `<VAR_NAME>` - <purpose>

Setup:
- <setup step>
```

### Testing

Document testing approach and commands.

```markdown
## Testing

- `<test command>` - <what it tests>
- <testing convention or pattern>
```

### Gotchas

Document non-obvious patterns, quirks, and warnings.

```markdown
## Gotchas

- <non-obvious thing that causes issues>
- <ordering dependency or prerequisite>
- <common mistake to avoid>
```

### Workflow

Document development workflow patterns.

```markdown
## Workflow

- <when to do X>
- <preferred approach for Y>
```

---

## Template: Root CLAUDE.md (Research-Backed)

**Use when:** the user supplies hard rules and principles, or Refactor rebuilds a root that already has them.

```markdown
# Project Name

One-sentence description of the project.

## Commands

| Command | Purpose |
|---------|---------|
| `pnpm build` | Production build |
| `pnpm test` | Run tests |
| `pnpm typecheck` | Type checking |

## Hard Rules (Critical)

These rules have no exceptions. Placed early for visibility.

| Rule | Why |
|------|-----|
| Never commit secrets | In git history forever; rotation is expensive |
| Never force-push main | Rewrites shared history; breaks teammates |
| Never retry auth errors | Won't fix; wastes quota; may trigger lockouts |

## Core Principles

- **Principle 1** — Brief explanation of why this matters
- **Principle 2** — Brief explanation of why this matters
- **Principle 3** — Brief explanation of why this matters

## Quick Reference

{Compact summary of frequently-needed info — patterns, conventions, etc.}

## Rule Conflicts

When rules conflict, use this priority:
1. Hard Rules (safety, security) — never override
2. Core Principles — guide decisions
3. Style preferences — yield to above

## Critical Reminders

- **Check for secrets before every commit**
- **Never force-push to main**
```

**Template notes:**
- Critical rules at BOTH start (visibility) AND end (recall: models attend least to the middle of a long context, the "Lost in the Middle" finding by Liu et al., 2023)
- All rules include "why" column for generalization
- Priority hierarchy is explicit
- Under 200 lines; move topic detail into `.claude/rules/` files
- No imports of rule files: Claude Code loads `.claude/rules/` on its own, and an import resolves relative to the importing file, so `@rules/coding.md` in the root would point to `./rules/`, not `.claude/rules/`

---

## Template: Project Root (Minimal)

**Use when:** creating a new CLAUDE.md (the default, and what Update mode writes when none exists).

```markdown
# <Project Name>

<One-line description>

## Commands

| Command | Description |
|---------|-------------|
| `<command>` | <description> |

## Architecture

```
<structure>
```

## Key Files

- `<path>` - <purpose>

## Hard Rules

<!-- Add project-specific rules here, each with its reason -->

## Gotchas

<!-- Add project-specific gotchas here -->
```

Claude Code strips block-level HTML comments before loading a CLAUDE.md, so the placeholders cost no context.

---

## Template: Project Root (Comprehensive)

**Use when:** the scan finds environment variables, a test setup, or code-style config worth recording. Keep the Hard Rules and Gotchas placeholders from the Minimal template.

```markdown
# <Project Name>

<One-line description>

## Commands

| Command | Description |
|---------|-------------|
| `<command>` | <description> |

## Architecture

```
<structure with descriptions>
```

## Key Files

- `<path>` - <purpose>

## Code Style

- <convention>

## Environment

- `<VAR>` - <purpose>

## Testing

- `<command>` - <scope>

## Gotchas

- <gotcha>
```

---

## Template: Rule File (.claude/rules/*.md)

```markdown
---
paths:
  - "{glob, for example src/api/**/*.ts}"
---

# {Topic} Guidelines

## Overview

Brief context: when these guidelines apply and why they exist.

## Rules

### Category 1

| Rule | Why |
|------|-----|
| Specific, actionable instruction | Reason this matters |
| Another specific instruction | Reason this matters |

### Category 2

| Rule | Why |
|------|-----|
| Specific, actionable instruction | Reason this matters |

## Patterns

### Good Pattern

```{language}
// Example of correct approach with explanation
```

### Avoid

```{language}
// Example of what not to do
// Explanation of why this is problematic
```

## Edge Cases

{Any special cases or exceptions to the rules above}
```

**Rule file notes:**
- `paths:` frontmatter is optional. With it, the rule loads only when Claude reads or edits a matching file; without it, the rule loads every session, like CLAUDE.md. Leave it out for rules that apply everywhere (safety, workflow)
- Self-contained — works without needing root context
- Includes reasoning for every rule
- Examples show both good and bad patterns with explanations

---

## Template: Hand-Crafted Subdirectory CLAUDE.md

```markdown
# {Directory} Guidelines

## Context

This directory contains {description}. Key priorities:
- {Priority 1 — what matters most here}
- {Priority 2 — secondary focus}

## Conventions

### {Category 1}

| Pattern | Why |
|---------|-----|
| Directory-specific instruction | Reason for this directory |

### {Category 2}

| Pattern | Why |
|---------|-----|
| Another instruction | Reason |

## Examples

### Pattern to Follow

```{language}
// Good example specific to this directory
// Brief explanation of why
```
```

**Subdirectory file notes:**
1. **No parent import:** Claude Code already loads every CLAUDE.md from the working directory up, and loads this file when Claude touches a file in the directory. `@../CLAUDE.md` would load the parent a second time, and in a nested directory such as `src/api/` it points to `src/CLAUDE.md`, not the root
2. **Keep focused:** Only include directory-specific guidance
3. **Don't duplicate:** If rule is in root CLAUDE.md, don't repeat it
4. **Target ~30 lines:** Subdirectory files supplement, not replace, root rules

---

## Template: Generated Subdirectory (Minimal)

For auto-generated files. Budget: about 100 tokens for a minimal file (score 4-5), 150-300 for a full one (score 6+), never over 500.

```markdown
# {Directory Name}

## Context
{One sentence: what this directory contains and its role}

## Key Files
- `{file}` - {purpose}
- `{file}` - {purpose}

## Patterns
- {Pattern} — {brief why}

## Gotchas
- {Non-obvious thing, if any — omit section if none}
```

**Generated file notes:**
1. **Minimal by design:** Start small, expand manually as needed
2. **One-sentence Context:** Avoid paragraphs — captures purpose, not background
3. **2-5 Key Files:** Entry points and configs only, not exhaustive
4. **Patterns with reasoning:** Brief "why" for each pattern (research-backed)
5. **Gotchas:** Include only if discovered during analysis — omit if none
6. **Budget:** about 100 tokens (minimal) or 150-300 (full), never over 500; lean toward brevity

**Example (good):**
```markdown
# Payments Service

## Context
Stripe integration for subscriptions and one-time payments.

## Key Files
- `stripe.ts` - Stripe client setup
- `webhooks.ts` - Webhook handlers

## Patterns
- Idempotency keys on all mutations — prevents duplicate charges
- Webhook verification before processing — security requirement

## Gotchas
- Webhooks require `STRIPE_WEBHOOK_SECRET` env var
```

**Example (too verbose — avoid):**
```markdown
# Payments Service

## Context
This directory contains the payments service which handles all payment-related functionality including Stripe integration, subscription management, and one-time payment processing.

## Key Files
- `stripe.ts` - The main Stripe client configuration and setup
- `webhooks.ts` - Handlers for Stripe webhook events
- `subscriptions.ts` - Subscription lifecycle management
- `types.ts` - TypeScript type definitions
- `utils.ts` - Payment utility functions
- `errors.ts` - Custom error classes

## Patterns
- Use TypeScript for type safety
- Handle errors appropriately
- Follow clean code principles
```

---

## Template: Package/Module (Monorepo)

For packages within a monorepo or distinct modules.

```markdown
# <Package Name>

<Purpose of this package>

## Usage

```
<import/usage example>
```

## Key Exports

- `<export>` - <purpose>

## Dependencies

- `<dependency>` - <why needed>

## Notes

- <important note>
```

---

## Template: Monorepo Root

```markdown
# <Monorepo Name>

<Description>

## Packages

| Package | Description | Path |
|---------|-------------|------|
| `<name>` | <purpose> | `<path>` |

## Commands

| Command | Description |
|---------|-------------|
| `<command>` | <description> |

## Cross-Package Patterns

- <shared pattern>
- <generation/sync pattern>
```

---

## Template: Triage Assessment

Use this for the Refactor triage (Phase 6 in SKILL.md). The signals and points are the ones in the SKILL.md triage table, so the highest possible score is 6:

```markdown
## Triage Assessment

**Current file:** {path}
**Lines:** {count}

### Scoring

| Signal | Score | Notes |
|--------|-------|-------|
| Already uses `.claude/rules/` structure | +2 / 0 | {yes/no} |
| Has clear hierarchy (headers, tables) | +1 / 0 | {yes/no} |
| Contains reasoning ("why" explanations) | +1 / 0 | {yes/no} |
| Rules are actionable and specific | +1 / 0 | {yes/no} |
| Under 200 lines with dense content | +1 / 0 | {yes/no} |
| Over 300 lines | -1 / 0 | {yes/no} |
| Wall-of-text without structure | -2 / 0 | {yes/no} |
| Contains contradictions | -2 / 0 | {none found / list them} |
| Mix of vague and specific rules | -1 / 0 | {all specific / mixed} |

**Total Score:** {X}

### Decision

| Score | Action |
|-------|--------|
| 4+ | Skip — already well-organized |
| 2-3 | Light refactoring |
| 0-1 | Standard refactoring |
| Negative | Deep refactoring |

**Recommendation:** {Skip / Light / Standard / Deep}

### Strengths
- {What's already good}

### Issues Found
- {What needs work}

### Next Steps
{If Skip: offer minor tweaks. Otherwise: propose the keep-vs-extract plan}
```

---

## Template: Refactoring Complete

Use this for final confirmation:

```markdown
## Refactoring Complete

### Summary

| Metric | Before | After |
|--------|--------|-------|
| Root CLAUDE.md lines | {X} | {Y} |
| Rule files | {X} | {Y} |
| Subdirectory files | {X} | {Y} |

### Preserved (in root)
- {High-value content kept in root}
- {Core principles}
- {Hard rules with reasoning}

### Extracted to .claude/rules/
- {Topic 1} → `.claude/rules/{file}.md` (paths: {glob, or "loads every session"})
- {Topic 2} → `.claude/rules/{file}.md` (paths: {glob, or "loads every session"})

### NOT Deleted (intentionally kept)
These were kept despite seeming "obvious", because a one-line safety reminder costs little and guards against an expensive mistake:
- {Safety reminder 1}
- {Safety reminder 2}

### Removed (actually vague)
- "{Vague instruction}" — not actionable
- "{Another vague one}" — no specific guidance

### Validation Checklist

- [ ] Reasoning ("why") preserved in all rules
- [ ] Safety rules NOT deleted
- [ ] Critical rules at BOTH start AND end
- [ ] Priority hierarchy explicit
- [ ] Every `@` import resolves from the file that contains it, and nothing imports a `.claude/rules/` file or a parent CLAUDE.md
- [ ] No meaning lost

**Does this look correct?**
```

---

## Update Principles

When updating any CLAUDE.md:

1. **Be specific**: Use actual file paths, real commands from this project
2. **Be current**: Verify info against the actual codebase
3. **Be brief**: One line per concept when possible
4. **Be useful**: Would this help a new Claude session understand the project?
5. **Include reasoning**: "X — because Y" format for rules
