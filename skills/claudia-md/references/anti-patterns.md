# Anti-Patterns

<!-- v1.1.0 | 2026-10-14 -->

Common mistakes to avoid when writing CLAUDE.md files.

| Avoid | Why | Instead |
|-------|-----|---------|
| Rules without reasoning | Models can't generalize; follow letter not spirit | "Rule — because reason" format |
| Negative-only framing | Less effective than positive | "Do X" instead of "Don't do Y" |
| Vague instructions | Not actionable; inconsistent behavior | Concrete, specific guidance |
| Deleting "obvious" safety rules | A one-line reminder costs little and guards against an expensive mistake | Keep safety reminders |
| Files over 200 lines | The Claude Code docs target under 200 lines; longer files cost context every session and reduce adherence | Move topic detail into `.claude/rules/` files with `paths:` frontmatter |
| `@`-importing a `.claude/rules/` file or the parent CLAUDE.md | Both load anyway, and an import resolves from the importing file, so the path is often wrong | Let Claude Code load them |
| Bare rule tables | Missing Why column loses generalization | Always include reasoning |
| Refactoring well-organized files | Wastes effort, risks meaning loss | Triage first |
| Generic advice | Not project-specific, wastes tokens | Document actual patterns |
| One-off fixes | Won't recur, clutters file | Only recurring patterns |
| Verbose explanations | Wastes context window | One line per concept |
