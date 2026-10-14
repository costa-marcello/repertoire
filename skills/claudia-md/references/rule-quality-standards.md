# Rule Quality Standards

## What Makes a High-Quality Rule

| Dimension | Bad | Good |
|-----------|-----|------|
| **Clarity** | "Be careful with auth" | "Auth errors fail immediately -- retrying won't fix and wastes quota" |
| **Reasoning** | "Never use any" | "Use `unknown` + narrowing -- preserves type safety through the codebase" |
| **Positive framing** | "Don't hardcode URLs" | "Read URLs from config -- avoids hitting wrong environment" |
| **Specificity** | "Write good tests" | "Test behavior, not implementation -- tests should survive refactoring" |
| **Examples** | (abstract) | Include Bad/Good columns in tables |

## The Hybrid Format

Anthropic research shows this format is most effective:

```
Directive + Brief Reasoning (1-2 sentences)
```

**Patterns that work:**

| Pattern | Example | Best For |
|---------|---------|----------|
| **Table with Why** | `\| Rule \| Why \|` | Hard rules, reference docs |
| **Inline dash** | "Prefer X -- it provides Y benefit" | Principles, guidelines |
| **Because clause** | "Do X because Y" | Prose instructions |
| **Bad/Good/Why table** | Full 4-column table | Complex patterns with anti-patterns |

## Transformation Examples

| Before (Rule-only) | After (Hybrid) |
|--------------------|----------------|
| "Never commit secrets" | "Never commit secrets -- in git history forever; rotation expensive" |
| "Use TypeScript" | "Use TypeScript -- static types catch errors at compile time" |
| "Don't use any" | "Use `unknown` + narrowing -- preserves type safety" |
| "Write tests" | "Test behavior, not implementation -- tests should survive refactoring" |
| "Handle errors" | "Catch at boundaries (API routes, handlers) -- bubble up otherwise" |

## Positive Reframing

| Negative (Less Effective) | Positive (More Effective) |
|---------------------------|---------------------------|
| "Don't hardcode URLs" | "Read URLs from config -- avoids wrong environment" |
| "Never use console.log" | "Use structured logger -- enables filtering and persistence" |
| "Avoid magic numbers" | "Extract constants with descriptive names -- self-documenting" |
| "Don't skip tests" | "Run quality gate after changes -- format, lint, typecheck, test" |

## Preservation Rules

Never delete these from a CLAUDE.md during refactoring:

| Keep | Why (Research-backed) |
|------|----------------------|
| Safety reminders ("never commit secrets") | Repetition improves compliance (industry research, as of v1.0) |
| Rules with reasoning ("X -- because Y") | Context improves generalization (Anthropic documentation) |
| Priority hierarchies | Models struggle with implicit priority (LLM prompting research) |
| Critical rules even if "obvious" | Training patterns need override reinforcement |
