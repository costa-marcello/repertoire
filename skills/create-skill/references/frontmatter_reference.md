# YAML Frontmatter Reference

Configure skill behavior using these fields between `---` markers:

```yaml
---
name: my-skill
description: What this skill does and when to use it. Use when...
context: fork
agent: Explore
disable-model-invocation: true
allowed-tools: Read, Grep, Bash(git *)
---
```

## Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name for the skill. If omitted, uses the directory name. Lowercase letters, numbers, and hyphens only (max 64 characters). No reserved words (anthropic, claude). Noun or short-phrase form preferred (pdf, changelog, frontend-design). |
| `description` | Recommended | What the skill does and when to use it. Claude uses this to decide when to apply the skill. If omitted, uses the first paragraph of markdown content. **Max 1024 characters.** |
| `context` | No | Set to `fork` ONLY for autonomous skills that run end-to-end without dispatching sub-agents and without pausing for the user. DO NOT set it on orchestrator skills (those that dispatch sub-agents via `Task`, `TeamCreate`, `TaskCreate`, or `SendMessage`) or interactive skills (those that present a report, plan, or prompt to the user and resume on the user's response). See "When to Use `context: fork`" below. Without fork, skills run inline and cannot be used by subagents. |
| `agent` | No | Which subagent type to use when `context: fork` is set. Options: `Explore`, `Plan`, `general-purpose`, or custom agents from `.claude/agents/`. Default: `general-purpose`. |
| `disable-model-invocation` | No | Set to `true` to prevent Claude from automatically loading this skill. Use for workflows you want to trigger manually with `/name`. Default: `false`. |
| `user-invocable` | No | Set to `false` to hide from the `/` menu. Use for background knowledge users shouldn't invoke directly. Default: `true`. |
| `allowed-tools` | No | Tools Claude can use without asking permission when this skill is active. Supports wildcards: `Read, Grep, Bash(git *)`, `Bash(npm *)`, `Bash(docker compose *)`. |
| `model` | No | Model to use when this skill is active. |
| `argument-hint` | No | Hint shown during autocomplete to indicate expected arguments. Example: `[issue-number]` or `[filename] [format]`. |
| `hooks` | No | Hooks scoped to this skill's lifecycle. Example: `hooks: { pre-invoke: [{ command: "echo Starting" }] }`. See Claude Code Hooks documentation. |

## Special Placeholder

`$ARGUMENTS` in skill content is replaced with text the user provides after the skill name. For example, `/deep-research quantum computing` replaces `$ARGUMENTS` with `quantum computing`.

## When to Use `context: fork`

The review-skill enforces a four-class taxonomy. Decide which class the skill falls into before choosing. Only Class A gets `context: fork`.

### Class A — Autonomous (add `context: fork`)

The skill runs end-to-end on its own: executes scripts, analyses files, writes output, and returns. It does NOT spawn sub-agents and does NOT pause for the user mid-run.

**Signals:**
- Referenced scripts in `scripts/`
- `<instructions>` tags with linear numbered steps that complete without user input
- `allowed-tools` restricts to read or single-process tools (no `Task`, no agent dispatch)
- Needs isolated context for subagent access

### Class B — Orchestrator (do NOT add `context: fork`)

The skill dispatches sub-agents via `Task`, `TeamCreate`, `TaskCreate`, or `SendMessage` and coordinates their output.

**Signals:**
- `allowed-tools` includes any of `Task`, `TeamCreate`, `TaskCreate`, `SendMessage`
- Body mentions "spawn agents", "dispatch agents", "parallel agents", agent allocation tables, or `TaskOutput` collection

**Why no fork:** a forked subagent cannot spawn further subagents, so fork breaks the dispatch chain.

### Class C — Interactive (do NOT add `context: fork`)

The skill presents a report, plan, or prompt to the user and then resumes on the user's response.

**Signals:**
- A numbered step or mode that shows a report, plan, or prompt to the user, followed by a later step or mode gated on the user's response ("after the user confirms", "if the user approves", "then apply")
- Review-then-Fix or Plan-then-Apply mode structure

**Why no fork:** a forked subagent returns only a final summary to the lead, collapsing the two-stage interaction into one opaque result the user never sees mid-flight. Writing a report file to disk does NOT count — the pause must be directed at the human reader.

### Class D — Mode-style reasoning (do NOT add `context: fork`)

The skill is a persistent thinking mode whose value comes from Claude's reasoning in the lead context, not from tool use or external I/O (e.g. `ultrathink`).

**Signals:**
- `allowed-tools` is empty, absent, or restricted to passive/read-only analysis
- No `scripts/` directory; body has no `Bash`, `Write`, `Edit`, or external I/O steps
- Description uses stance / perspective verbs ("thinks", "analyses", "reasons", "considers") rather than manipulation verbs ("extracts", "generates", "runs")
- Skill is invoked as a reasoning modifier on an existing task (often with a case-sensitive trigger keyword) rather than as a self-contained task
- Body describes a lens, framework, or mental model to apply — not a workflow that produces a file or state change

**Why no fork:** a fork spawns a fresh subagent context, losing the lead's thinking tokens, conversation state, and cross-turn persistence that give the mode its value.

### Definitive conflicts (fork must be removed)

1. `context: fork` set AND `allowed-tools` contains `Task`, `TeamCreate`, `TaskCreate`, or `SendMessage` — orchestrator violation.
2. `context: fork` set AND the skill body defines a user-visible pause AND a later step or mode that resumes on the user's response — interactive violation.
3. `context: fork` set AND the skill is invoked as a persistent reasoning mode rather than a discrete task — mode-style violation.

Skills without `context: fork` run inline and cannot be used by subagents. If the skill is Class B, C, or D, inline is the correct choice.

## Invocation Control Matrix

| Frontmatter | You can invoke | Claude can invoke | Subagents can use |
|-------------|----------------|-------------------|-------------------|
| (default) | Yes | Yes | No (runs inline) |
| `context: fork` | Yes | Yes | Yes |
| `disable-model-invocation: true` | Yes | No | No |
| `context: fork` + `disable-model-invocation: true` | Yes | No | Yes (when explicitly delegated) |

## Additional Examples

### Reference skill that runs inline

```yaml
---
name: api-conventions
description: "Documents API design patterns for this codebase. Use when writing new endpoints or reviewing API consistency."
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
```

No `context: fork` needed -- this skill provides reference guidance that runs inline in the conversation.

### Medium-freedom skill with tool restrictions

```yaml
---
name: data-pipeline
description: "Processes CSV files into structured database records with validation
  and error recovery. Use when users mention data import, CSV processing, ETL,
  or database ingestion."
context: fork
allowed-tools: Read, Grep, Bash(python3 *)
---

<instructions>
1. Detect delimiter and encoding from the file header
2. Validate columns against `references/column_mapping.md`
3. Run `scripts/transform.py` on validated rows
4. Report results: rows processed, skipped, and errors
</instructions>
```

Medium freedom: workflow steps are fixed but transformation logic adapts to different schemas. `allowed-tools` restricts tool access to reading, searching, and running Python scripts.
