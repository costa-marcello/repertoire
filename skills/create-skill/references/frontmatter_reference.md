# Frontmatter Reference

The YAML block between the `---` markers at the top of SKILL.md. This file covers every field Claude Code reads, the portable subset, invocation control, substitutions, and dynamic context injection. The fork decision test is in `authoring_rules.md`.

## Contents

1. [Minimal frontmatter](#minimal-frontmatter)
2. [Claude Code fields](#claude-code-fields)
3. [Portable subset](#portable-subset)
4. [Invocation control](#invocation-control)
5. [Running forked](#running-forked)
6. [String substitutions](#string-substitutions)
7. [Referencing bundled scripts](#referencing-bundled-scripts)
8. [Dynamic context injection](#dynamic-context-injection)
9. [Examples](#examples)

## Minimal frontmatter

```yaml
---
name: pdf-forms
description: "Fills and validates PDF forms. Use when the user wants to fill a PDF form, list its fields, or check a filled form."
license: MIT
---
```

Quote the description. An unquoted value that contains a colon followed by a space breaks the YAML, and Claude Code then loads the skill with empty metadata.

## Claude Code fields

Claude Code reads exactly these 20 fields. It ignores any other field silently, and review-skill reports one as m12, because it is usually a typo.

| Field | Default | Semantics |
|-------|---------|-----------|
| `name` | Directory name | 1-64 characters of `a-z`, `0-9`, and single hyphens, equal to the directory name. No `anthropic` or `claude`, which blocks upload to claude.ai and the API. |
| `description` | First non-empty body line | What the skill does and when to use it, key use case first. At most 1,024 characters, no `<` or `>`. |
| `when_to_use` | None | Extra trigger context (phrases, example requests), appended to `description` in the skill listing. The two together are truncated at 1,536 characters. It satisfies M8's "when" in Claude Code only. |
| `argument-hint` | None | Autocomplete hint, such as `[issue-number]` or `[filename] [format]`. |
| `arguments` | None | Named positional arguments, as a space-separated string or a YAML list. Names map to positions in order: with `arguments: [issue, branch]`, `$issue` is the first argument and `$branch` the second. |
| `disable-model-invocation` | `false` | `true`: only the user can invoke the skill, and its description leaves the listing. Use for side effects such as deploys. |
| `user-invocable` | `true` | `false`: hidden from the `/` menu, so only Claude invokes it. Use for background knowledge. |
| `allowed-tools` | None | Pre-approves the listed tools for the invoking turn, so they run without a permission prompt. The grant clears on the next message. It does not restrict which tools are available. Accepts a space- or comma-separated string or a YAML list; patterns such as `Bash(git *)` work. |
| `disallowed-tools` | None | Removes the listed tools while the skill is active. Use this field, not `allowed-tools`, to restrict tools. |
| `model` | Session model | Model override for the current turn. |
| `effort` | Session effort | `low`, `medium`, `high`, `xhigh`, or `max`; the available levels depend on the model. |
| `context` | Inline | `fork` runs the skill as a new subagent; see [Running forked](#running-forked). |
| `agent` | `general-purpose` | Subagent type for `context: fork`, either built-in (such as `Explore` or `Plan`) or a custom agent from `.claude/agents/`. Without fork it is a dead field (m12). |
| `background` | `true` | Applies only with `context: fork`. `false` makes the invoking turn wait for the result. |
| `hooks` | None | Hooks that Claude Code registers when the skill is invoked; they stay active for the rest of the session. |
| `paths` | None | Glob patterns, as a comma-separated string or a YAML list. When set, Claude loads the skill automatically only when working with matching files. |
| `shell` | `bash` | `bash` or `powershell`: the shell used for dynamic context injection commands. |
| `metadata` | None | String-to-string map. Accepted; Claude Code does not act on it. |
| `license` | None | License name or bundled license file. Accepted; not acted on. |
| `compatibility` | None | Environment requirements, at most 500 characters. Accepted; not acted on. |

## Portable subset

claude.ai, the Claude API, and other Agent Skills clients follow the Agent Skills spec. For the portable target, use only these fields:

- `name` (required)
- `description` (required)
- `license`
- `compatibility` (at most 500 characters)
- `metadata` (string-to-string map)
- `allowed-tools` (experimental, space-separated)

For the portable target, review-skill treats these as M9: any other field, a missing `name`, and a `name` that contains `anthropic` or `claude`. Check with `quick_validate.py <skill-dir> --portable`. Anthropic's skill-creator validator and `skills-ref validate` also reject every field outside this set, so they flag Claude Code fields such as `context` and `disable-model-invocation`.

## Invocation control

The official table from the Claude Code docs:

| Frontmatter | You can invoke | Claude can invoke | When loaded into context |
|-------------|----------------|-------------------|--------------------------|
| (default) | Yes | Yes | Description always in context; full skill loads when invoked |
| `disable-model-invocation: true` | Yes | No | Description not in context; full skill loads when you invoke it |
| `user-invocable: false` | No | Yes | Description always in context; full skill loads when invoked |

There is no separate subagent column. Subagents do not inherit the skills invoked in the parent conversation, but they can invoke project, user, and plugin skills through the Skill tool. A subagent definition's `skills:` field preloads full skill content.

## Running forked

`context: fork` changes how the skill runs:

- **New subagent.** The skill runs as a new subagent of the `agent` type, with the SKILL.md body (after substitution) as its prompt.
- **No history.** It does not see the conversation, so the instructions and arguments have to stand alone. When the task depends on the conversation, fork the conversation instead, for example with `/subtask`.
- **Background.** By default it runs in the background, and the result arrives in the conversation when it finishes. `background: false` waits in the invoking turn.
- **No questions, no Workflow.** It cannot ask the user anything, because ordinary subagents lose AskUserQuestion, and it has no Workflow tool. It can dispatch subagents with the Agent tool within the nesting limit (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, default 3).
- **Explicit tasks only.** A guideline-only skill returns nothing useful when forked.

Decide with the fork decision test in `authoring_rules.md` ("Deciding on context: fork"). The default is inline, which is always valid.

## String substitutions

On invocation, Claude Code substitutes these tokens everywhere in SKILL.md, including code blocks and examples:

| Token | Expands to |
|-------|------------|
| `$ARGUMENTS` | All arguments as typed |
| `$ARGUMENTS[N]` | Argument N, 0-based |
| `$N` | Shorthand for `$ARGUMENTS[N]`: `$0` is the first argument |
| `$name` | A named argument declared in `arguments`; empty when its position has no argument |
| `${CLAUDE_SESSION_ID}` | The current session ID |
| `${CLAUDE_EFFORT}` | The current effort level |
| `${CLAUDE_SKILL_DIR}` | The directory that contains SKILL.md |
| `${CLAUDE_PROJECT_DIR}` | The project root |
| `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` | The plugin directory and its data directory (plugin skills only) |

Rules:

- **Unused arguments.** When the user passes arguments and no placeholder receives them, Claude Code appends `ARGUMENTS: <value>` to the skill content.
- **Escaping.** To write a literal dollar sign before a digit, `ARGUMENTS`, or a declared name, put one backslash before it: `\$1.00`. The backslash does not stop `${CLAUDE_*}` substitution.
- **Teaching examples.** Substitution also happens inside examples, so a teaching example that contains these tokens changes meaning in SKILL.md (m12). Keep such examples in `references/`. Claude reads reference files with the Read tool, so they are not substituted.

## Referencing bundled scripts

- **Claude Code:** write `${CLAUDE_SKILL_DIR}/scripts/extract.py`. It resolves to the skill's directory, whatever the working directory is.
- **Portable target:** write paths relative to the skill directory (`scripts/extract.py`), and Claude resolves them against the skill's location.
- **Plugin skills:** `${CLAUDE_PLUGIN_ROOT}` points at the plugin root, for files shared by several skills in the plugin.
- **Paths:** use forward slashes, and never an assumed install location such as a fixed home-directory path, because the skill may be installed per project, per user, or in a plugin.
- **Python:** write commands with `python`; use `python3` only where `python` is not on the path (on Windows `python3` is often the Microsoft Store stub).

## Dynamic context injection

Claude Code can run a shell command while loading SKILL.md, and put the command's output into the prompt before Claude sees anything. Two forms trigger it:

- an exclamation mark placed directly before an inline code span that holds a command;
- a fenced code block whose three opening backticks are directly followed by an exclamation mark.

The `shell` field picks bash or PowerShell.

- **Every invocation.** The command runs every time the skill is invoked, before Claude reads anything. A failing command aborts the invocation.
- **When to use it.** Only for context that every run needs and that is cheap and safe to compute, such as the current branch name.
- **Never as a demonstration in SKILL.md.** The demonstration would run on every invocation. Describe the syntax in words, as this section does, or keep a demonstration in a reference file, which Claude Code does not preprocess.
- **Review.** review-skill reports unintended injection as M9.

## Examples

Inline guideline skill. It has no task to return, so a fork would come back empty:

```yaml
---
name: api-conventions
description: "Documents this codebase's API rules for naming, error format, and pagination. Use when writing or reviewing API endpoints."
---
```

Forked task skill. It passes all five conditions of the fork decision test, and `background: false` returns the table in the same turn:

```yaml
---
name: csv-report
description: "Summarises a CSV file into a Markdown table of row counts, column types, and empty cells. Use when the user asks for a quick profile or summary of a CSV file."
argument-hint: "[csv-path]"
context: fork
background: false
---

Profile the CSV file at $ARGUMENTS.

1. If no path was given, print `usage: /csv-report <csv-path>` and stop.
2. Run `python ${CLAUDE_SKILL_DIR}/scripts/summarise.py "$ARGUMENTS"`.
3. Return the table it prints, or its error message if it exits non-zero.
```

Side-effect skill that only the user triggers. It confirms with the user before deploying, so it runs inline:

```yaml
---
name: deploy-staging
description: "Deploys the current branch to staging and reports the preview URL. Use when the user asks to deploy to staging or wants a staging preview."
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(./scripts/deploy.sh *)
---
```

`allowed-tools` here pre-approves the git and deploy commands for the turn, and it does not block other tools. To remove a tool, use `disallowed-tools`.
