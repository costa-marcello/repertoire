# Anti-Patterns

<!-- v1.0.0 | 2026-01-30 -->

Common mistakes to avoid when writing CLAUDE.md files.

| Avoid | Why | Instead |
|-------|-----|---------|
| Rules without reasoning | Models can't generalize; follow letter not spirit | "Rule — because reason" format |
| Negative-only framing | Less effective than positive | "Do X" instead of "Don't do Y" |
| Vague instructions | Not actionable; inconsistent behavior | Concrete, specific guidance |
| Deleting "obvious" safety rules | Repetition improves compliance 76% | Keep safety reminders |
| Over 200 instructions | Models reliably follow ~150-200 | Focus on most important |
| Bare rule tables | Missing Why column loses generalization | Always include reasoning |
| Refactoring well-organized files | Wastes effort, risks meaning loss | Triage first |
| Generic advice | Not project-specific, wastes tokens | Document actual patterns |
| One-off fixes | Won't recur, clutters file | Only recurring patterns |
| Verbose explanations | Wastes context window | One line per concept |
