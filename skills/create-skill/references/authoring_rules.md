# Authoring Rules

These are the rules `review-skill` grades against, written as instructions for the author. Apply them while drafting, so the first review finds nothing. The rule IDs, titles, and severities match review-skill's `references/rules.md` exactly. This file is self-contained, so it works when review-skill is not installed.

## Contents

1. [Grading in one paragraph](#grading-in-one-paragraph)
2. [Rule index](#rule-index)
3. [Deciding on context: fork](#deciding-on-context-fork)
4. [Major rules: how to satisfy them](#major-rules-how-to-satisfy-them)
5. [Minor rules: how to satisfy them](#minor-rules-how-to-satisfy-them)
6. [Style rules: how to satisfy them](#style-rules-how-to-satisfy-them)

## Grading in one paragraph

Grade A means 0 Major and 0 Minor findings. Style findings are skillkit house conventions; they are reported but never graded. create-skill still aims for zero Style notes, so that its output matches the kit. Each rule ID counts once per skill. Some checks are definitive (the validator decides) and others heuristic (a reviewer confirms them with quoted evidence), so a clean `quick_validate.py` run is necessary but not sufficient.

## Rule index

| ID | Title | Severity | How to satisfy while authoring |
|----|-------|----------|--------------------------------|
| M1 | SKILL.md over 500 lines | Major | Keep SKILL.md under 400 lines; move detail into `references/` as you write. |
| M2 | context: fork on a skill that cannot work forked | Major | Leave fork out unless the skill passes the fork decision test below. |
| M3 | Wrong degree of freedom for the task | Major | Use exact commands for fragile steps and heuristics with a default for open-ended ones. |
| M4 | No verification step for destructive or long workflows | Major | End every destructive or 5+ step workflow with a check (validator, diff, test). |
| M5 | Contradictions or broken references within or across files | Major | State each fact once, link to it, and keep every referenced file present. |
| M6 | Scripts that swallow errors or wait for input | Major | Catch specific exceptions with an actionable message; never prompt interactively. |
| M7 | Core instructions are unactionable | Major | Write concrete actions; avoid the weak verbs listed under M7. |
| M8 | Description lacks what or when, or uses first or second person | Major | One capability sentence plus a "Use when..." clause; no "I" or "you". |
| M9 | Skill will not load or loads wrong | Major | Valid name equal to the directory, description under 1024 characters with no `<` or `>`, no template leftovers. |
| M10 | Secrets, undisclosed network use, or harmful instructions | Major | No secrets; disclose network use; nothing that acts against the user. |
| m1 | Explains what Claude already knows | Minor | Delete general explanations; keep only skill-specific knowledge. |
| m2 | Three or more options with no default | Minor | "Default to X. Use Y when Z." |
| m3 | Time-sensitive content | Minor | No date-conditional logic; pin versions with a note. |
| m4 | Inconsistent terminology | Minor | One term per concept, everywhere. |
| m9 | Long reference file without a table of contents | Minor | Give every reference over 100 lines a `## Contents` list near the top. |
| m10 | Reference chains deeper than one level | Minor | Link every needed file directly from SKILL.md. |
| m11 | Non-portable paths in Markdown | Minor | Forward slashes and skill-relative paths only. |
| m12 | Loader hygiene problems | Minor | Use only known frontmatter keys, no `agent` without fork, no `claude`/`anthropic` in the name. |
| m13 | Unclear script contract | Minor | Say "Run" or "Read" for each script, and name its requirements. |
| m14 | MCP tool named without its server | Minor | Write `Server:tool_name` or `mcp__server__tool_name`. |
| m15 | Emphasis overuse without reasons | Minor | Plain-language rules with a reason; avoid shouted MUST/NEVER. |
| S1 | Workflows or examples not wrapped in XML tags | Style | Wrap the workflow in `<instructions>` and each example in `<example>`. |
| S2 | Fewer than 3 or more than 5 example blocks | Style | Put 3-5 short `<example>` blocks in SKILL.md; move long ones to `references/`. |
| S3 | SKILL.md over 400 lines or about 5k tokens | Style | Stay under 400 lines and 20,000 characters. |
| S4 | Unexpected files in the skill root | Style | Only SKILL.md, LICENSE*, scripts/, references/, assets/, evals/, and tests/ in the root. |
| S5 | No evals | Style | Ship `evals/evals.json` (3+ cases) and `evals/trigger_queries.json`. |
| S6 | Description does not open with a third-person verb | Style | Start with "Extracts...", "Reviews...", "Generates...". |
| S7 | Mixed filename separators in one skill | Style | Pick `-` or `_` for reference filenames, and use only that one. |

## Deciding on context: fork

Run inline (no `context: fork`) unless the skill does **all** of the following:

1. It performs an explicit task with a result to return. Guideline-only skills return nothing when forked.
2. It needs nothing from the conversation beyond its arguments. A forked skill sees no history.
3. It never asks the user anything, and neither do the references it sends Claude to as steps (an intake questionnaire, a "read this first" guide). A forked skill cannot ask, approve, or answer a choice prompt such as "Apply these changes? [All / Select / Cancel]"; when arguments are missing it prints usage and stops.
4. It does not use the Workflow tool, which subagents do not get.
5. It is acceptable for it to finish in the background. If the result is needed in the same turn, add `background: false`.

When forking, set `agent` only if the default `general-purpose` agent is wrong, and choose an agent type that has every tool the body needs. Dispatching subagents with the Agent tool from a forked skill works within the nesting limit (default depth 3).

<example>
**Fork:** `csv-report` takes a file path, runs `scripts/summarise.py`, and returns a table. It has a task and needs only its argument, so `context: fork` is fine.

**Inline:** a debugging skill that investigates "the bug we are discussing" requires the conversation, so it runs inline. `create-skill` asks clarifying questions, so it runs inline as well.
</example>

## Major rules: how to satisfy them

- **M1:** watch the running line count. When a section passes about 50 lines, move it to a reference and leave a one-line pointer that says when to read it.
- **M3:** decide the freedom level per section before writing it. Fragile, ordered operations get exact commands or a script; analysis and review get heuristics and a default.
- **M4:** after the last step of any destructive or 5+ step workflow, add "Verify: ..." with a concrete check. Use a validate-fix-repeat loop before irreversible steps.
- **M5:** when a fact (a default, path, or threshold) is needed in two places, write it once and link to it. Before finishing, open every file SKILL.md mentions and confirm it exists and agrees.
- **M6:** in scripts, catch named exceptions, print what failed and how to fix it, and take every input from arguments or environment variables.
- **M7:** the weak verbs are: consider, ensure, handle appropriately, handle properly (also with words in between, as in "handle errors appropriately"), as needed, as appropriate, if applicable, where relevant. Replace each with a command, a check, or "Default to X".
- **M8:** write the description first. Sentence one says what the skill does; sentence two starts "Use when..." and lists the triggers, key use case first. No first or second person anywhere in it: no "I", "we", "you", or "your".
- **M9:**
  - Name rules: 1-64 characters of `a-z`, `0-9`, and single hyphens, equal to the directory name. Avoid the directory names `synced` and `anthropic-skills*`.
  - The description is at most 1024 characters and contains no angle brackets.
  - Replace every `[TODO` placeholder before validating. Skills made from older templates may also hold `scripts/example.py`, `references/api_reference.md`, or `assets/example_asset.txt`; delete them.
  - Keep dynamic context injection syntax out of SKILL.md unless the command should run on every invocation.
  - For the portable target (claude.ai, the API, other clients), also include `name` and use only the portable keys.
- **M10:** keep secrets in environment variables. When a script uses the network, say so in SKILL.md and give the purpose. Never instruct the model to reveal its hidden reasoning.

## Minor rules: how to satisfy them

- **m1:** for each paragraph ask "would Claude get this wrong without it?". If not, delete it.
- **m2:** every list of three or more alternatives names a default and the condition for each alternative.
- **m3:** describe the current method only. Put deprecated methods in a collapsed "Old patterns" section, and add "verify against official docs" next to pinned versions.
- **m4:** pick terms at the start (for example "subagent", "reference file") and grep for variants before finishing.
- **m9:** add a `## Contents` list within the first 30 lines of any reference that grows past 100 lines.
- **m10:** if a reference would point to another file for essential content, link that file from SKILL.md instead.
- **m11:** never write backslash paths or a real user's home directory. Paths are relative to the skill directory (`scripts/x.py`); in Claude Code, `${CLAUDE_SKILL_DIR}/scripts/x.py` also works.
- **m12:**
  - Use only the 20 Claude Code frontmatter keys listed in `frontmatter_reference.md`, and set `agent` or `background` only together with `context: fork`.
  - Keep `description` plus `when_to_use` under 1536 characters.
  - Put teaching examples that contain `$ARGUMENTS` in `references/` (they would be substituted in SKILL.md).
- **m13:** introduce each script with "Run `python scripts/x.py ...`" or "Read `scripts/x.py` for ...". List the packages it needs.
- **m14:** qualify MCP tools with their server name.
- **m15:** write rules in normal case and give the reason. Reserve emphasis for the one rule whose violation causes real damage.

## Style rules: how to satisfy them

`init_skill.py` produces a template that already satisfies S1, S2, S4, and S5. Keep it that way:

- **S1/S2:** keep the workflow inside `<instructions>`, and keep 3-5 short `<example>` blocks in SKILL.md.
- **S3:** stay under 400 lines and 20,000 characters. Content after the first ~5,000 tokens may be dropped when a long session compacts, so put the most important instructions first.
- **S4:** add files only under `scripts/`, `references/`, `assets/`, `evals/`, or `tests/`.
- **S5:** write `evals/evals.json` and `evals/trigger_queries.json` before the skill itself (see `evals_guide.md`).
- **S6:** open the description with a third-person verb.
- **S7:** use one filename separator for all reference files.
