# Deep-Review Lenses

Six lenses drawn from Anthropic's prompting guidance and published research. Like the content lenses, they only find issues: each issue maps to a rule ID in `rules.md` or goes under "Advisory notes" in the report. No lens produces a grade, a score, or a pass count. Full citations are in `sources.md`.

## Contents

1. [XML tags (S1)](#1-xml-tags-s1)
2. [Examples (S2, M5, m12)](#2-examples-s2-m5-m12)
3. [Prompt defect taxonomy](#3-prompt-defect-taxonomy)
4. [Anti-patterns](#4-anti-patterns)
5. [Formatting (advisory)](#5-formatting-advisory)
6. [HELM-inspired questions (thinking aids)](#6-helm-inspired-questions-thinking-aids)
7. [Quick checklist](#quick-checklist)

## 1. XML tags (S1)

Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags) recommend XML tags when a prompt mixes instructions, context, examples, and inputs, so Claude can tell them apart. Anthropic's skill guidance does not require tags, and Anthropic's own skills use plain Markdown. Repertoire uses `<instructions>` and `<example>` as house style, so a gap here is Style.

| Check | Rule |
|-------|------|
| The workflow sits inside `<instructions>` | S1 (definitive) |
| Worked examples sit inside `<example>` | S1 (heuristic; the validator checks only `<instructions>`) |
| The same tag names are used throughout | advisory |
| Inputs or fetched content are separated from instructions | advisory; M10 when the skill tells Claude to obey them |

## 2. Examples (S2, M5, m12)

The [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#use-examples-effectively) call examples one of the most reliable ways to steer format and tone. Make them relevant, diverse, and structured; 3-5 work best for prompts. The skill guidance prescribes no number, which is why the count is Style.

| Check | Rule |
|-------|------|
| Fewer than 3 or more than 5 `<example>` blocks in SKILL.md | S2 |
| An example contradicts the instructions | M5 |
| An example in SKILL.md contains a literal `$ARGUMENTS` or `$N` | m12 |
| All examples cover the same case | advisory |
| Long examples crowd SKILL.md | advisory; move them to a reference |

Research context: example order changes results (Lu et al., ACL 2022); format matters more than label correctness (Min et al., EMNLP 2022); too many examples can lower performance (arXiv:2509.13196), although some tasks gain from hundreds (arXiv:2404.11018).

## 3. Prompt defect taxonomy

Tian et al. (arXiv:2509.14404) sort prompt defects into six dimensions. In a skill, each points to rules:

| Dimension | What it looks like in a skill | Rule |
|-----------|-------------------------------|------|
| Specification and intent | Vague description, unclear task, directives Claude cannot act on | M8, M7 |
| Input and content | The skill treats file or web content as instructions; inputs are never defined | M10; advisory |
| Structure and formatting | Bloated SKILL.md, long references without a table of contents, reference chains | M1, m9, m10, S3 |
| Context and memory | Fork on a skill that needs the conversation; facts that disagree across files; key rules buried after the first 5,000 tokens | M2, M5, advisory |
| Performance and efficiency | Explaining concepts Claude knows; repeated content | m1, S3 |
| Maintainability and engineering | User-specific paths, the skill's own files reached through an install location, dated logic, drifting terms, unexplained constants | m11, M11, m3, m4, advisory |

## 4. Anti-patterns

From the [OWASP Top 10 for LLM applications (2025)](https://genai.owasp.org/llm-top-10/):

| Risk | What it looks like in a skill | Rule |
|------|-------------------------------|------|
| LLM01 Prompt injection | The skill tells Claude to follow instructions found in fetched pages or user files | M10 |
| LLM02 Sensitive information disclosure | Hardcoded secrets; file contents sent to an undisclosed host | M10 |
| LLM03 Supply chain | A script downloads and runs remote code that SKILL.md does not disclose | M10 |
| LLM06 Excessive agency | Deletes, publishes, or overwrites with no check or confirmation | M4; M10 when it acts against the user |

From Anthropic's skill and prompting guidance:

| Anti-pattern | Rule |
|--------------|------|
| Shouted directives (`MUST`, `NEVER`, `CRITICAL`) with no reason | m15 |
| Conflicting instructions with no precedence | M5 |
| Vague tool rules ("use tools when helpful") | M7 |
| A menu of options with no default | m2 |
| Instructions to reveal hidden reasoning | M10 |
| MCP tools named without their server | m14 |
| Dynamic context injection in SKILL.md, or the skill's own files reached through an install location such as `~/.claude/skills/<own-name>/` | M11 |
| A step that needs a display or browser, a local stdio MCP server or `localhost` service with no fallback, a `claude -p` call, or secrets only in a home-directory dotfile | M11 (heuristic) |
| Rigid steps where judgment is needed (newer models need less prescription) | M3 when an open task is forced into fixed steps; otherwise advisory |

From research: elaborate prompting techniques that help one model can hurt a stronger one (arXiv:2510.22251). Treat it as support for simplifying, not as a finding.

## 5. Formatting (advisory)

He et al. (arXiv:2411.10541) found that GPT-3.5-turbo's results on a code translation task varied by up to 40% across prompt templates, while GPT-4 was much less sensitive. Use this as a reason to look at structure, not as a rule:

- Headers for sections, tables for comparisons, one delimiter style throughout.
- Direct instructions over elaborate framing.

Formatting observations are advisory; tag usage is covered by S1.

## 6. HELM-inspired questions (thinking aids)

These questions, adapted from Stanford HELM's multi-metric view, help a reviewer notice problems. They carry no score. When one fails, look for the rule in the right column.

| Question | Where to look |
|----------|---------------|
| Clarity: can a person follow SKILL.md in one read? | M7, m4 |
| Actionability: can each instruction be carried out as written? | M7, m2 |
| Robustness: would a reworded request still trigger the skill? | trigger review (advisory), M8 |
| Maintainability: can one fact change without breaking another file? | M5, m3, m11 |
| Safety: are destructive steps checked, and are boundaries stated? | M4, M10 |
| Portability: does it run in Cowork as well as in Claude Code? | M11; M9 for the portable target |

## Quick checklist

```text
Deep-review lenses:
- [ ] XML tags: S1 gaps noted as Style
- [ ] Examples: count (S2), contradictions (M5), literal arguments (m12)
- [ ] Defect taxonomy: each dimension checked, issues mapped to IDs
- [ ] Anti-patterns: OWASP and Anthropic lists checked, including the Cowork rows (M11), issues mapped to IDs
- [ ] Formatting and HELM questions: observations recorded as advisory
```
