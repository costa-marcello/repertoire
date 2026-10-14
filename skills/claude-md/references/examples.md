<!-- v2.0 | 2026-01-30 -->

# Before/After Examples

## Contents

1. [Example 1: Bloated → Well-Organized (Standard Refactor)](#example-1-bloated--well-organized-standard-refactor)
2. [Example 2: Already Well-Organized (Skip Refactor)](#example-2-already-well-organized-skip-refactor)
3. [Example 3: What to Keep vs What to Remove](#example-3-what-to-keep-vs-what-to-remove)
4. [Example 4: Compaction That Preserves Meaning](#example-4-compaction-that-preserves-meaning)
5. [Example 5: Instruction Placement (Research-Backed)](#example-5-instruction-placement-research-backed)
6. [Key Takeaways](#key-takeaways)

Research-backed transformations showing how to refactor while preserving meaning.

**Key principle:** Optimize for relevance, not brevity. A 150-line file with reasoning beats a 50-line file that lost meaning.

---

## Example 1: Bloated → Well-Organized (Standard Refactor)

### Before (Problematic)

```markdown
# CLAUDE.md

This is a React project.

## Code Style
- Use 2 spaces
- Use semicolons
- Prefer const over let
- Use arrow functions
- Always use explicit return types
- Never use any
... (200 more lines of rules without reasoning)

## Testing
- Use Jest
- Coverage > 80%
... (100 more lines)

## Don't do bad things
- Write clean code
- Be careful
- Don't break stuff
```

**Problems:**
- 400+ lines, mostly without reasoning ("why")
- Vague instructions ("write clean code") mixed with specific ones
- No priority hierarchy
- No structure for progressive disclosure

### After (Research-Backed)

**Root CLAUDE.md (~80 lines):**

```markdown
# React Analytics Dashboard

Real-time analytics visualization with TypeScript and React.

## Commands

| Command | Purpose |
|---------|---------|
| `pnpm dev` | Start dev server |
| `pnpm test` | Run tests with coverage |
| `pnpm build` | Production build |

## Hard Rules (Critical)

| Rule | Why |
|------|-----|
| Never commit secrets | In git history forever; rotation is expensive |
| Never force-push main | Rewrites shared history; breaks teammates |
| PRs < 400 lines | Reviewable diffs get better reviews |

## Core Principles

- **Type safety first** — Strict TS, no `any`, Zod at boundaries. Catches bugs before runtime.
- **Test behavior, not implementation** — Tests survive refactoring when they verify outcomes.
- **Conventional commits** — `feat:`, `fix:`, `chore:`. Enables automated changelogs.

## Rules (Detailed)

@rules/coding.md
@rules/testing.md
@rules/workflow.md

## Rule Conflicts

When rules conflict: Hard Rules > Core Principles > Style preferences

## Critical Reminders

These rules are repeated here because research shows end-position improves recall:
- **Never commit secrets** — check before every commit
- **PRs < 400 lines** — split if larger
```

**`.claude/rules/coding.md` (~60 lines):**

```markdown
# Coding Guidelines

## TypeScript

| Rule | Why |
|------|-----|
| Enable `noUncheckedIndexedAccess` | Catches undefined access at compile time |
| No `any` — use `unknown` + narrowing | Preserves type safety through the codebase |
| Zod at API boundaries | Runtime validation where types can't help |

## Style

2 spaces, semicolons, `const` over `let`, arrow functions, explicit return types.

## Async Patterns

- **Cancellation:** AbortController for fetch/timers
- **Concurrency:** Batch >10 parallel ops to avoid overwhelming resources
- **Cleanup:** Always in `finally` block

## Error Handling

| Pattern | When |
|---------|------|
| Bubble up | When you can't meaningfully handle it |
| Catch at boundaries | API routes, event handlers, async entry points |
| Custom error classes | When domain context matters for handling |
```

**Improvements:**
- Root has high-value content with reasoning ("why")
- Critical rules appear at BOTH start AND end (research-backed)
- Detailed rules extracted to `.claude/rules/` but still include reasoning
- Priority hierarchy is explicit
- No vague instructions ("write clean code" removed entirely)

---

## Example 2: Already Well-Organized (Skip Refactor)

### Triage Assessment

```markdown
## Triage Assessment

**Score:** 5/6
**Recommendation:** Skip refactoring

**Strengths:**
- Already uses `.claude/rules/` structure (+2)
- Clear hierarchy with headers and tables (+1)
- Rules include "why" reasoning (+1)
- Actionable, specific instructions (+1)
- ~100 lines, dense content (+1)

**Issues found:**
- None significant

**Proceed with Phase 1?** No — file is already well-organized.

**Alternative offers:**
- Minor cleanup of any verbose sections?
- Add critical rules at end for recall improvement?
- Review for any contradictions?
```

---

## Example 3: What to Keep vs What to Remove

### Keep (Research-Backed Reasons)

| Instruction | Why Keep |
|-------------|----------|
| "Never commit secrets" | Safety reinforcement — repetition improves compliance 76% |
| "Never force-push main — rewrites shared history" | Has reasoning; context improves generalization |
| "Hard Rules > Core Principles > Style" | Explicit priority — models struggle with implicit hierarchy |
| "PRs < 400 lines" (even if "obvious") | Override reinforcement for training patterns |

### Remove (Actually Vague)

| Instruction | Why Remove |
|-------------|------------|
| "Write clean code" | Not actionable — what does "clean" mean specifically? |
| "Be careful" | No specific guidance |
| "Follow best practices" | Which practices? Be specific. |
| "Don't introduce bugs" | Obviously not actionable |

### Transform (Vague → Specific)

| Before (Vague) | After (Specific) |
|----------------|------------------|
| "Write good tests" | "Test behavior, not implementation — tests should survive refactoring" |
| "Handle errors properly" | "Catch at boundaries (API routes, event handlers); bubble up otherwise" |
| "Use TypeScript correctly" | "Enable strict mode, no `any`, Zod at boundaries" |

---

## Example 4: Compaction That Preserves Meaning

### Bad Compaction (Loses Meaning)

Before:
```markdown
- Never commit .env files because they contain secrets that will be in git history forever
- Never force-push to main because it rewrites shared history and breaks other developers
- Keep PRs under 400 lines because large PRs get rubber-stamped instead of reviewed
```

Bad compaction:
```markdown
| Rule |
|------|
| No .env commits |
| No force-push main |
| PRs < 400 lines |
```

**Problem:** Lost the "why" — Claude won't generalize to similar situations.

### Good Compaction (Preserves Meaning)

```markdown
| Rule | Why |
|------|-----|
| Never commit secrets (.env, keys) | In git history forever; rotation expensive |
| Never force-push main | Rewrites shared history; breaks teammates |
| PRs < 400 lines | Large PRs get rubber-stamped |
```

**Better:** Same line reduction, but reasoning preserved.

---

## Example 5: Instruction Placement (Research-Backed)

### Why Position Matters

Research finding: "Lost in the middle" — models process beginning and end better than middle.

### Pattern

```markdown
# Project Name

## Hard Rules (at START for visibility)
[Critical safety rules with reasoning]

## ... (middle content) ...

## Critical Reminders (at END for recall)
[Repeat 2-3 most critical rules]
```

### Example

```markdown
# My Project

## Hard Rules

| Rule | Why |
|------|-----|
| Never commit secrets | History forever |
| Never force-push main | Breaks teammates |

## Core Principles
[...]

## Detailed Rules
@rules/coding.md
@rules/workflow.md

## Critical Reminders

For emphasis (research shows end-position aids recall):
- Check for secrets before every commit
- Never force-push to main
```

---

## Key Takeaways

1. **Keep the "why"** — Reasoning enables generalization
2. **Repeat critical rules** — At both start AND end
3. **Delete vague, keep specific** — "Write clean code" goes; "no `any`" stays
4. **Safety rules are NOT redundant** — Repetition improves compliance
5. **Explicit priority** — "X > Y > Z" beats implicit hierarchy
6. **Triage first** — Well-organized files don't need refactoring
