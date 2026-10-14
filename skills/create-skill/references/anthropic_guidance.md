# Anthropic Guidance for Skill Authors

What Anthropic and the Claude Code docs say about writing skills, and how it shapes this kit. The graded rules are in `authoring_rules.md`. This file gives the reasoning behind them. The linked pages change, so verify details against them before relying on a specific number.

## Contents

1. [Sources](#sources)
2. [Skill anatomy](#skill-anatomy)
3. [What loads when](#what-loads-when)
4. [Conciseness](#conciseness)
5. [Degrees of freedom](#degrees-of-freedom)
6. [Names and descriptions](#names-and-descriptions)
7. [Writing the body](#writing-the-body)
8. [Evaluation-driven development](#evaluation-driven-development)
9. [Claude A and Claude B](#claude-a-and-claude-b)
10. [Scripts](#scripts)
11. [Claude Code and Cowork specifics](#claude-code-and-cowork-specifics)
12. [Anti-patterns](#anti-patterns)
13. [Security review](#security-review)

## Sources

- Claude Code skills: https://code.claude.com/docs/en/skills
- Agent Skills best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Agent Skills specification: https://agentskills.io/specification
- Plugin marketplaces: https://code.claude.com/docs/en/plugins/marketplace-reference
- Anthropic's skill-creator skill (Apache-2.0), the source of the evals-first loop in `evals_guide.md`

## Skill anatomy

```text
skill-name/
  SKILL.md        frontmatter (name, description, ...) and Markdown instructions
  scripts/        code Claude runs; only the output enters context
  references/     documentation Claude reads when a step calls for it
  assets/         files used in the output: templates, images, fonts
  evals/          evals.json and trigger_queries.json (Repertoire convention; left out of zips)
```

Claude Code requires no frontmatter field. `name` defaults to the directory name, and `description` falls back to the first non-empty line of the body. Write both anyway. The description decides triggering, and the Agent Skills spec requires both fields. Claude Code ignores unknown fields silently, and malformed YAML loads the body with empty metadata. That is why `quick_validate.py` parses the frontmatter strictly.

## What loads when

| Level | Content | In context |
|-------|---------|------------|
| 1 | `name`, `description`, `when_to_use` | Always, in the skill listing (except with `disable-model-invocation: true`) |
| 2 | SKILL.md body | From invocation for the rest of the session |
| 3 | Reference files, scripts, assets | Only when a step reads or runs them; a script's source enters context only if read |

Consequences for authors:

- **Listing budget.** The skill listing gets about 1% of the context window (`skillListingBudgetFraction`). On overflow, the descriptions of the least-used skills are dropped. Each entry is truncated at 1,536 characters of description plus `when_to_use`. Put the key use case in the first sentence.
- **Compaction.** After compaction, Claude Code re-attaches the first 5,000 tokens of each recently invoked skill, within a combined budget of 25,000 tokens. Instructions further down can be lost in long sessions, so lead with the workflow and the rules that matter most.
- **Progressive disclosure.** SKILL.md is an overview that links reference files and says when to read each one. Keep references one level deep: SKILL.md links every file Claude needs. Give each reference file over 100 lines a table of contents, so a partial read still shows its scope.

## Conciseness

- The context window is shared with the conversation, other skills, and the task, so every paragraph competes for space.
- Assume Claude is capable. Delete explanations of general concepts. Keep what Claude would get wrong without the skill: project facts, gotchas, exact commands, defaults.
- Anthropic's limit is a SKILL.md body under 500 lines, and the spec recommends about 5,000 tokens. Repertoire's M1 counts the whole file, frontmatter included, so stay under 500 total lines; the house target is under 400 lines and 20,000 characters (S3).
- Skills written for earlier models are often too prescriptive for newer ones. When a model follows the intent without a rigid rule, remove the rule.

## Degrees of freedom

Match specificity to fragility. Anthropic's analogy: a narrow bridge with cliffs on both sides needs guardrails and exact directions, while an open field needs only a heading.

| Freedom | Use for | Instruction style | Examples |
|---------|---------|-------------------|----------|
| High | Many valid approaches; context decides | Heuristics with a default | Code review, troubleshooting, analysis |
| Medium | A preferred pattern, some variation is fine | Pseudocode or a script with parameters | API integration, report generation |
| Low | Fragile, order-dependent, consistency-critical | Exact commands or a bundled script, run unmodified | Database migrations, OOXML edits, releases |

Mixing levels in one skill is normal. A release skill can leave the notes' wording open and pin the tagging commands exactly.

## Names and descriptions

**Name**
- Use at most 64 characters of lowercase letters, digits, and hyphens, equal to the directory name.
- The words `anthropic` and `claude` are reserved on the Anthropic platform.
- A gerund (`processing-pdfs`) is one option. Noun phrases (`pdf-processing`) and action forms (`process-pdfs`) work equally well.
- Avoid vague names such as `helper` or `utils`.

**Description.** This is the one field that decides whether Claude loads the skill.
- **What and when.** State what the skill does and when to use it, key use case first.
- **Person.** Write in the third person. Anthropic's guidance is to avoid "I can help you" and "You can use this".
  - The imperative "Use this skill when...", which Anthropic's own skills open with, is acceptable (it passes M8).
  - Repertoire prefers a third-person verb opening ("Extracts...") as house style (S6).
- **Terms.** Include the words users actually type: file types, tool names, task verbs.
- **Pushiness.** Claude tends to under-trigger skills, so make the trigger clause a little pushy: "Use whenever the user mentions X or Y, even without naming Z." Avoid shouting, though. Newer models over-trigger on aggressive wording such as "CRITICAL: you MUST use this skill", so write a plain "Use when..." instead.
- **Limits.** At most 1,024 characters, with no XML tags (no `<` or `>`).

Good: "Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."

Bad: "Helps with documents." It has no trigger, and the capability is vague.

## Writing the body

- **Form.** Use the imperative ("Run", "Check") and give the reason behind each rule. A rule with a reason generalises to new cases; a bare "must" gets over-applied.
- **Defaults.** Give a default plus an escape hatch rather than a menu: "Use pdfplumber for text extraction. For scanned PDFs, use OCR instead."
- **Checklists.** For complex workflows, provide a checklist that Claude copies into its reply and ticks off. It keeps long workflows on track.
- **Feedback loops.**
  - Validate, fix, repeat.
  - For batch or destructive work, plan, validate, then execute: write the plan to a file, check it with a script, then apply it.
- **Templates and examples.**
  - Use templates for strict output formats.
  - Use input/output example pairs where output quality depends on style.
  - Anthropic writes examples as Markdown ("**Example 1:**") and requires neither XML tags nor a fixed number of examples. Repertoire's house style wraps the workflow in `<instructions>` and uses 3 to 5 `<example>` blocks (S1, S2), which is never graded.
- **Conditional detail.** Put it in reference files, with SKILL.md saying when to read each one.

## Evaluation-driven development

Anthropic's recommended order:

1. Run Claude on representative tasks without the skill, and record where it fails or lacks context.
2. Build three scenarios that test those gaps.
3. Measure the baseline.
4. Write the minimal instructions that close the gaps.
5. Run the scenarios again, compare with the baseline, and refine.

The Claude platform has no built-in eval runner. `evals_guide.md` describes the subagent-based approximation this kit uses and the upgrade paths.

## Claude A and Claude B

- **The loop.** Claude A, the session writing the skill, refines it. Claude B, a fresh instance with the skill installed, does real work with it. Bring Claude B's behaviour back to Claude A, refine, and repeat.
- **Observe navigation.** Each pattern points to a fix:
  - Files read in an unexpected order mean the structure is not intuitive.
  - A reference file never opened means the link is not prominent, or the file is not needed.
  - The same file read repeatedly means that content belongs in SKILL.md.
  - A section that is ignored should be cut, or moved up.
- **Diagnose.** Ask Claude A to explain the gap ("Claude B skipped the validation step; what in the skill made that easy?"). The authoring model is good at seeing how another instance reads instructions.
- **Models.** Test with every model that will use the skill: Haiku may need more guidance, and Opus may be slowed by detail it does not need.

## Scripts

- **Solve, don't defer.** Handle error cases in the script, for example a missing file or a bad encoding, instead of failing and leaving Claude to improvise.
- **No voodoo constants.** Comment each constant with the reason for its value (`TIMEOUT = 30  # requests in this API rarely exceed 30 seconds`).
- **Run or read.** Say whether Claude should run the script (the usual case, since only its output enters context) or read it as reference.
- **Dependencies.** List the required packages and show the install command; do not assume they are installed. Pin versions only with a "verify against official docs" note.
- **Interface.**
  - Keep scripts non-interactive: inputs come from arguments, flags, or environment variables.
  - Provide `--help`.
  - Put data on stdout and diagnostics on stderr.
  - Return meaningful exit codes, and keep the output size predictable.
- **MCP tools.** Write the fully qualified name, `ServerName:tool_name`, or `mcp__server__tool_name` in Claude Code. A bare tool name is ambiguous when several servers are connected.

## Claude Code and Cowork specifics

- **Locations,** by precedence: enterprise, then personal (`~/.claude/skills/<name>/SKILL.md`), then project (`.claude/skills/<name>/SKILL.md`).
  - Plugin skills are namespaced `/plugin:skill`. A plugin is the one route that reaches both Claude Code and Cowork (`distribution.md`).
  - Nested `.claude/skills/` directories load on first touch, and `--add-dir` directories load too.
  - Edits reload live, except in a top-level skills directory created during the session: Claude Code does not watch it, so run `/reload-skills` after each change there. A plugin, including a linked checkout (`distribution.md`), applies changes with `/reload-plugins` instead.
  - Do not name a skill directory `synced`, or `anthropic-skills*` outside plugins.
- **Tools.**
  - The agent-dispatch tool is Agent; `Task(...)` still works as an alias in settings and agent definitions.
  - TaskCreate, TaskList, TaskUpdate, and TaskGet manage the todo list and do not dispatch agents.
  - Workflow also dispatches agents, but subagents do not get it. SendMessage messages agents.
- **Subagents.**
  - Subagents can dispatch subagents up to 3 levels deep by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`). Ordinary subagents lose AskUserQuestion and Workflow.
  - Subagents do not inherit the parent's invoked skills, but they can invoke project, user, and plugin skills through the Skill tool. A subagent definition's `skills:` field preloads full skill content.
- **Fork.** `context: fork` semantics are in `frontmatter_reference.md`, and the fork decision test is in `authoring_rules.md`.
- **Cowork.** It runs the Claude Code engine with the installed plugins' skills, in a desktop VM or a cloud container.
  - Subagents (the Agent tool), hooks, scripts, and network access within the egress rules work, and `${CLAUDE_SKILL_DIR}` is substituted.
  - It never reads `~/.claude/skills`, has no display or browser, and desktop Cowork replaces dynamic context injection with a placeholder.
  - Local stdio MCP servers run only in desktop Cowork, never in cloud sessions, so a skill that uses one states a fallback.
  - These limits are M11 "Breaks in Cowork"; create-skill's step 6 checks them.
- **Diagnostics.** `/skill-doctor` reports each skill's context cost and usage; it is not a linter.
- **Testing.** Test with and without the skill, each in a fresh session.

## Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Windows-style backslash paths | Forward slashes everywhere; they work on every platform |
| Many options with no default | One default plus an escape hatch |
| Date-conditional instructions | State the current method; keep old ones in a collapsed "Old patterns" section |
| Inconsistent terminology | One term per concept, everywhere |
| Reference chains | Link every needed file from SKILL.md |
| Shouted all-caps rules | Plain wording with the reason |
| Explaining concepts Claude knows | Delete the explanation |
| Asking the model to print its hidden reasoning | Remove it; newer models refuse such requests |
| Undocumented constants | Comment the reason for each value |
| Assuming tools are installed | List requirements and install commands |
| Opening a window or browser to show results | Write files (in Cowork, to the outputs folder) |
| Reaching the skill's own files through an install location | `${CLAUDE_SKILL_DIR}/...`, which works wherever the skill is installed |

## Security review

- Install skills only from trusted sources, because a skill can direct Claude to run code and read files.
- Before shipping or installing a skill, audit every bundled file for:
  - network calls, and where the data goes;
  - file access outside the task;
  - instructions that act against the user, or that conflict with the skill's stated purpose;
  - hardcoded credentials;
  - data exfiltration.
- Apply skill-creator's principle of lack of surprise: described to the user, a skill's contents should hold no surprises.
- In this kit, `scripts/security_scan.py` runs gitleaks for secrets and pattern checks for dangerous code and network calls. Disclose any network use in SKILL.md (M10).
