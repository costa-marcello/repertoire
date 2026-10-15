# Skill Review Rules

The single source of truth for grading skills. `create-skill/references/authoring_rules.md` mirrors the rule index below (same IDs, titles, and severities) as authoring instructions, and `create-skill/scripts/quick_validate.py` implements the definitive checks.

## Contents

1. [How grading works](#how-grading-works)
2. [Rule index](#rule-index)
3. [Major rules](#major-rules)
4. [Minor rules](#minor-rules)
5. [Style rules](#style-rules)
6. [Frontmatter fields](#frontmatter-fields)
7. [Validator contract](#validator-contract)

## How grading works

**Severity is set by impact:**
- **Major (M)**: the skill fails to load, triggers wrongly, misbehaves at run time, or misleads Claude.
- **Minor (m)**: the skill works, but less reliably, efficiently, or portably.
- **Style (S)**: Repertoire house convention. Reported in a separate "Style notes" section and never graded.

**Confidence:**
- **Definitive** checks are decided mechanically, by `quick_validate.py` or by the procedure stated in the rule.
- **Heuristic** checks need judgment. A heuristic finding counts only after the reviewer confirms it and quotes the evidence (`file:line` plus the offending text). A validator `check` line is a lead, not a finding.

**Platform target:** grade against `claude-code` unless the user asks for `portable`. The report's "Graded for" row states it.
- **`claude-code` (default): Claude Code and Cowork.** The skill ships in a plugin (or a Claude Code skills folder), may use every Claude Code frontmatter field, and must also run in Cowork, which runs the Claude Code engine. M11 covers what breaks there.
- **`portable`: single-skill uploads to claude.ai and the Claude API, and other Agent Skills clients.** These uploads accept only six frontmatter fields (see [Frontmatter fields](#frontmatter-fields)). Cowork rejects a standalone upload that has any other field, which is why Cowork gets skills through the plugin rather than through `portable`.

**Counting:** each rule ID counts once per skill, however many locations it has. List every location under the finding.

**F triggers override the counts.** Grade F if any of these hold:
- There is no `SKILL.md`.
- The frontmatter is missing or does not parse as YAML.
- `description` is missing or empty.
- The body is empty.

**Grade bands** (apply top to bottom; the first match wins):

| Grade | Condition |
|-------|-----------|
| F | An F trigger, or 4 or more Major |
| D | 2-3 Major, or 1 Major with 4 or more Minor |
| C | 1 Major, or 0 Major with 3 or more Minor |
| B | 0 Major with 1-2 Minor |
| A | 0 Major and 0 Minor |

There are no per-aspect letter grades and no criterion pass counts. The deep-review lenses in `research-backed-criteria.md` and the content lenses in `content-quality-checklist.md` are ways to find issues; each issue they find maps to a rule ID below, or it is reported as advisory.

## Rule index

IDs m5-m8 are retired and are never reused.

| ID | Title | Severity | Source | Confidence |
|----|-------|----------|--------|------------|
| M1 | SKILL.md over 500 lines | Major | Anthropic, Spec | definitive |
| M2 | context: fork on a skill that cannot work forked | Major | Claude Code | mixed |
| M3 | Wrong degree of freedom for the task | Major | Anthropic | heuristic |
| M4 | No verification step for destructive or long workflows | Major | Anthropic | heuristic |
| M5 | Contradictions or broken references within or across files | Major | Anthropic | mixed |
| M6 | Scripts that swallow errors or wait for input | Major | Anthropic, Spec | mixed |
| M7 | Core instructions are unactionable | Major | Anthropic | heuristic |
| M8 | Description lacks what or when, or uses first or second person | Major | Anthropic | mixed |
| M9 | Skill will not load or loads wrong | Major | Spec, Claude Code | definitive |
| M10 | Secrets, undisclosed network use, or harmful instructions | Major | Anthropic | mixed |
| M11 | Breaks in Cowork | Major | Claude Code | mixed |
| M12 | Fails its own evals | Major | Anthropic | heuristic |
| m1 | Explains what Claude already knows | Minor | Anthropic | heuristic |
| m2 | Three or more options with no default | Minor | Anthropic | heuristic |
| m3 | Time-sensitive content | Minor | Anthropic | heuristic |
| m4 | Inconsistent terminology | Minor | Anthropic | heuristic |
| m9 | Long reference file without a table of contents | Minor | Anthropic | definitive |
| m10 | Reference chains deeper than one level | Minor | Anthropic | heuristic |
| m11 | Non-portable paths in Markdown | Minor | Anthropic | definitive |
| m12 | Loader hygiene problems | Minor | Claude Code | mixed |
| m13 | Unclear script contract | Minor | Anthropic | heuristic |
| m14 | MCP tool named without its server | Minor | Anthropic | heuristic |
| m15 | Emphasis overuse without reasons | Minor | Anthropic | heuristic |
| S1 | Workflows or examples not wrapped in XML tags | Style | Repertoire | definitive |
| S2 | Fewer than 3 or more than 5 example blocks | Style | Repertoire | definitive |
| S3 | SKILL.md over 400 lines or about 5k tokens | Style | Repertoire | definitive |
| S4 | Unexpected files in the skill root | Style | Repertoire | definitive |
| S5 | No evals | Style | Repertoire | definitive |
| S6 | Description does not open with a third-person verb | Style | Repertoire | definitive |
| S7 | Mixed filename separators in one skill | Style | Repertoire | definitive |

## Major rules

### M1 SKILL.md over 500 lines
- **Detect:** count lines the way `quick_validate.py` does (Python `splitlines()` on the whole file). More than 500 is M1.
- **Fix:** move detailed or conditional content into `references/` and link it from SKILL.md, saying when to read each file.

### M2 context: fork on a skill that cannot work forked
A forked skill runs as a fresh subagent. It gets the skill body as its prompt, but none of the conversation history. It runs in the background by default (`background: false` makes the turn wait), and it cannot ask the user anything. A missing fork is never an issue: running inline is the default and is always valid.
- **Detect, definitive:** `context: fork` is set and the body, or a reference the body sends Claude to as a step, asks the user something or waits for the user. Examples: `AskUserQuestion`, "ask the user", "ask user for confirmation", "wait for confirmation", "after the user approves", "after user approval", "get user approval", "Ask all 10 questions", and a choice prompt such as "Apply these changes? [All / Select / Cancel]" or "Continue? (y/n)". A choice prompt counts inside a code block too; "user approval" does not count when it names a UI element being built ("a user approval dialog"). A reference is sent to as a step when SKILL.md names it on a numbered step line (not a numbered item that opens with the file name, which only lists files) or on a line that says to read it first or before something ("1. **Intake**: use `references/intake.md`", "Read `references/api.md` before writing code").
  - Ignore mentions negated in the same clause, such as "do not wait for confirmation", "never ask the user", "instead of asking the user", "subagents lose `AskUserQuestion`", "user approval is not required", or "`AskUserQuestion` is not available".
  - A negation inside or before a condition governs another verb, so "If the format is not given, ask the user" and "Do not proceed until you get user approval" are still pauses. Two negations cancel: "Never edit files without user approval" is a pause.
  - A clause runs to the next sentence or clause punctuation, across soft line wraps. A tool name in backticks still counts. A forked skill that lacks an argument must print usage and stop; asking for the argument counts as a pause.
- **Detect, heuristic:** with fork set, also confirm any of these:
  - a reference SKILL.md links but does not send Claude to as a step asks or waits for the user, and the skill reads it on a path it takes (the validator prints one `check` line per such reference);
  - the body uses the Workflow tool, which subagents do not get;
  - it depends on the conversation ("the bug the user described", "earlier in this conversation");
  - it has no explicit task (guidelines only, so the subagent returns nothing useful);
  - it is a reasoning mode applied to the ongoing conversation;
  - its `agent` type lacks tools the body needs (for example `agent: Explore` with steps that write files).
- **Advisory, not a finding:** fork combined with Agent dispatch works within the nesting limit (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, default 3; verify against the Claude Code docs). Note this; do not count it.
- **Fix:** remove `context: fork`, `agent`, and `background`.
- **Decision test:** fork only when the skill does all of the following:
  - it performs an explicit task with a returnable result;
  - it needs nothing from the conversation beyond its arguments;
  - it never asks the user anything;
  - it does not use Workflow;
  - it is acceptable for it to finish in the background.
- **Pass/fail:** "Convert the CSV at `$ARGUMENTS` and report row counts" passes, so fork is fine. "Find the root cause of the bug we are discussing" fails: it needs the history.

### M3 Wrong degree of freedom for the task
- **Detect:** a fragile, order-dependent operation (migrations, OOXML edits, releases) is described loosely, or an open-ended task (review, analysis) is forced into rigid steps.
- **Fix:** give exact commands or scripts for fragile operations, and heuristics with a default for open-ended ones.
- **Pass/fail:** "Run `scripts/migrate.py --dry-run`, then without `--dry-run`" passes for a migration. "Update the schema carefully" fails.

### M4 No verification step for destructive or long workflows
- **Detect:** a workflow that deletes, overwrites, publishes, or migrates, or a workflow of 5 or more steps, has no check before the irreversible step or at the end (validator run, diff, test, re-read).
- **Fix:** add a validate-fix-repeat loop before the irreversible step and a final verification.
- **Pass/fail:** "Validate with `scripts/validate.py`; fix errors and re-run until it passes; then pack" passes. "Edit the XML, then pack" fails.

### M5 Contradictions or broken references within or across files
- **Detect, definitive:** SKILL.md references a bundled file that does not exist, or whose letter case differs from the file on disk (case-insensitive file systems hide the break until the skill runs on Linux or claude.ai). A bundled path starts at a word boundary (so `ooxml/scripts/x.py` belongs to another tree), after `./`, or after `${CLAUDE_SKILL_DIR}/`. It counts when its last part has an extension, when it ends with `/`, or when it has at least two segments below `scripts/`, `references/`, `assets/`, or `evals/`. Trailing punctuation, line ranges (`:10-20`), and `:function` suffixes are not part of the path. Paths inside `<example>` blocks are skipped. Missing paths under `evals/` and missing `../<other-skill>/` paths are `check` leads only, because packaging strips `evals/` and sibling skills are optional installs.
- **Detect, heuristic:** the same default, threshold, rule, or path is stated differently in two places (within a file or across files), or a cross-reference points to a renamed or deleted section.
- **Fix:** state each fact once and link to it. Fix or remove stale references.
- **Pass/fail:** one default stated in SKILL.md and nowhere else passes. "Default 3 retries" in SKILL.md with "default 5" in a reference fails.

### M6 Scripts that swallow errors or wait for input
- **Detect, definitive:** a bundled Python script has a bare `except:`, an `except Exception:` or `except BaseException:` whose body is only `pass`, or calls `input()`, `raw_input()`, or `getpass.getpass()`.
- **Detect, heuristic:** a catch-all handler that hides the cause and has no recovery or actionable message; a Python script that reads `sys.stdin` interactively; a shell script that runs `read`.
- **Fix:** catch specific exceptions, print what failed and how to fix it, and take inputs as arguments, flags, or environment variables.

### M7 Core instructions are unactionable
- **Weak verbs (canonical list):** consider, ensure, handle appropriately, handle properly, as needed, as appropriate, if applicable, where relevant. "Handle ... appropriately/properly" counts with up to three words in between ("handle errors appropriately").
- **Detect:** count the directives (imperative sentences in the body, outside code, inline code, and quotes) that rest on a weak verb and give no concrete default, command, or check. Three or more is M7.
- **Fix:** replace each one with a concrete action: "Run X", "Check that Y returns Z", "Default to A; use B when C".
- **Pass/fail:** "On HTTP 429, wait 2^n seconds (max 60), retry 3 times" passes. "Handle rate limits appropriately" fails.

### M8 Description lacks what or when, or uses first or second person
- **What:** the description says what the skill does (a capability). This part is heuristic.
- **When, definitive:** a trigger clause: "Use when/whenever/for/if...", "Use this skill when/whenever/for/if...", "Use it when...", "Triggers on/when...", "Invoke (this skill) when...", "Activates when...", or "when the user/users...". In Claude Code a `when_to_use` field also satisfies it; for the portable platform target only `description` counts.
- **Person, definitive:** first or second person outside quotes is M8: "I", "I'm", "we", "our", "Let me", "you", "your", "you're". An imperative "Use this skill when..." is acceptable. A preference for a third-person verb opening is Style (S6).
- **Fix:** write one sentence on the capability and one on the triggers, with the key use case first.
- **Pass/fail:** "Extracts tables from PDFs. Use when the user mentions PDF tables or reports." passes. "Helps with documents" fails: there is no trigger, and the capability is vague.

### M9 Skill will not load or loads wrong
- **Detect, definitive:**
  - `name` (when present) breaks the spec: it must be 1-64 characters of `a-z`, `0-9`, and hyphens, with no leading, trailing, or doubled hyphen, and it must equal the folder name.
  - `description` is over 1024 characters or contains `<` or `>`.
  - The folder is named `synced` (any case) or starts with `anthropic-skills`.
  - Template leftovers remain: `[TODO` in SKILL.md, or the init placeholders `scripts/example.py`, `references/api_reference.md`, or `assets/example_asset.txt`.
- **Portable platform target, definitive:** additionally, `name` is missing, a frontmatter key falls outside the portable set (see [Frontmatter fields](#frontmatter-fields)), or `name` contains `anthropic` or `claude`.
- **Fix:** rename to match the spec and the folder, shorten the description, and remove the leftovers.

### M10 Secrets, undisclosed network use, or harmful instructions
- **Detect, definitive:** `security_scan.py` (gitleaks) reports a secret.
- **Detect, heuristic:** confirm any of these:
  - scripts or instructions make network calls, or send data, that SKILL.md does not disclose;
  - instructions act against the user (hidden actions, data exfiltration, disabling safeguards);
  - instructions tell the model to reveal its hidden reasoning, which newer models refuse.
- **Fix:** move secrets to environment variables, disclose network use and its purpose in SKILL.md, and delete the harmful instructions.
- **Pass/fail:** "Fetches the release list from the GitHub API (network)" stated in SKILL.md passes. A script that silently POSTs file contents to an unlisted host fails.

### M11 Breaks in Cowork
Cowork runs the Claude Code engine with the plugin's skills, inside a desktop VM or a cloud container. It has no display, never reads `~/.claude/skills`, and does not run dynamic context injection. M11 applies to both platform targets, because claude.ai and the API share these limits.
- **Detect, definitive:**
  - SKILL.md contains dynamic context injection: a `!` at the start of a line or after whitespace, followed by a backtick command, or a fenced block opened with three backticks and `!`. Code fences count. Desktop Cowork replaces the command with a placeholder, and in Claude Code a failing command aborts the invocation.
  - SKILL.md, a Markdown file under `references/`, or a bundled script reaches the skill's own files through an install location: `~/.claude/skills/<own-name>/`, `$HOME/...`, `%USERPROFILE%/...`, the same under `.agents/skills/`, or a project-relative `.claude/skills/<own-name>/` or `.agents/skills/<own-name>/`. Plugin installs live elsewhere, and Cowork never reads these folders. `<example>` blocks are skipped. For the skill's own name this overrides the `~/.claude/skills/` exemption in m11; paths to other skills stay under m11. A Glob or `find` for a file in the skill's own folder (the skill-folder block's `**/<own-name>/<file>` search) names no install location and is not M11.
- **Detect, heuristic:** confirm any of these:
  - a step needs a display or a browser (a GUI window, `webbrowser.open`, a headed browser, a preview the user must look at) and offers no file output or headless path;
  - a step depends on a local stdio MCP server or a `localhost` service and states no fallback. These run only on a computer (desktop Cowork, or a cloud session linked to it through the desktop app), never in a cloud session with no linked computer;
  - a step shells out to `claude -p`;
  - secrets are read only from a home-directory dotfile (such as `~/.config/<tool>/.env`), with no environment variable route.
- **Fix:** reach bundled files through `${CLAUDE_SKILL_DIR}` in Markdown, behind the skill-folder block from create-skill's `bundled_resources.md`, and through the script's own location (`Path(__file__).resolve().parent`) in scripts; turn injection into an explicit step ("Run `git status`"); write results to files (the outputs folder in Cowork) instead of opening them; state the fallback for each local service; read secrets from environment variables.
- **Pass/fail:** "Run `python ${CLAUDE_SKILL_DIR}/scripts/report.py`" passes. "Run `python ~/.claude/skills/report/scripts/report.py`" in the `report` skill fails: plugin installs and Cowork keep the skill elsewhere.
- **Advisory, not graded:** a skill that runs, reads, or copies bundled files without the skill-folder block. A skill loaded before a Cowork or claude.ai chat moves to a cloud session can get a base directory, and likely a `${CLAUDE_SKILL_DIR}`, that points at a folder that does not exist (https://github.com/anthropics/claude-code/issues/98790), but the documented behavior is that Cowork substitutes the token, so the gap goes under advisory notes. The block's Glob in `~/.claude` searches the session's own files, so it does not conflict with Cowork never reading the user's `~/.claude/skills`.

### M12 Fails its own evals
- **When it runs:** only in a **regression** run, never in a plain review. A regression run starts when the user says `regression`, after the fix loop (Auto-Fix) changes a skill inside the user's own repository, or when create-skill's update flow asks for one. It runs only on skills in the user's own repository, and in Review Only it asks before running, because running evals executes the skill. It never runs inside an eval subagent or inside create-skill's Layer 3 review gate.
- **Detect, heuristic:** run each case in `evals/evals.json` in a fresh subagent that has the skill, under the isolation rules in `mode-regression.md`: an inputs folder holding copies of the case's `files`, a separate output folder, no outward actions (no push, post, send, or publish), and "do not use the Skill tool". Grade every expectation against the outputs. Re-run a failing case once; only a case that fails twice counts. Quote the failed expectation and the evidence.
- **Fix:** change the skill until the case passes. When the expectation itself is wrong, fix the eval and say why in the report.
- **Pass/fail:** every case passes, or fails once and passes on the re-run: no finding. A case that fails both runs is M12.

## Minor rules

### m1 Explains what Claude already knows
- **Detect:** a paragraph explains a general concept (what JSON, REST, git, or PDF is) rather than skill-specific knowledge.
- **Fix:** delete it. Keep gotchas and project-specific facts.

### m2 Three or more options with no default
- **Detect:** three or more tools or approaches are offered with no recommended default and no decision criteria.
- **Fix:** "Default to X. Use Y when Z."

### m3 Time-sensitive content
- **Detect:** date-conditional logic ("before August 2025, use..."), "currently", or a pinned version with no note.
- **Fix:** state the current method. Put deprecated methods in a collapsed "Old patterns" section. Pin versions with "verify against official docs".

### m4 Inconsistent terminology
- **Detect:** one concept is named two ways across the skill ("subagent" vs "sub-agent", "field" vs "property").
- **Fix:** pick one term and use it everywhere.

### m9 Long reference file without a table of contents
- **Detect:** a Markdown file under `references/` is longer than 100 lines and has no `Contents` or `Table of Contents` heading in its first 30 lines.
- **Fix:** add a `## Contents` list near the top.

### m10 Reference chains deeper than one level
- **Detect:** a file that SKILL.md links to sends the reader to another bundled file for essential content, and SKILL.md does not link that second file directly.
- **Fix:** link every file Claude needs straight from SKILL.md, saying when to read it.

### m11 Non-portable paths in Markdown
- **Detect:** SKILL.md or a reference uses backslash-separated paths (a drive letter followed by a backslash, or a bundled folder such as `scripts` followed by a backslash), or user-specific absolute paths such as `/Users/<real-name>/`, `/home/<real-name>/`, or a drive-letter `Users` folder with a real name. These are exempt:
  - generic placeholders (`username`, `user`, `<user>`, `you`, `your-name`, `name`, `me`, `example`, `shared`, `public`, and names starting with `<`, `{`, `$`, or `%`);
  - home-relative locations such as `~/.claude/skills/` (except a path to the skill's own files, which is M11);
  - fenced code blocks tagged `powershell`, `ps1`, `pwsh`, `cmd`, or `bat`.
- **Fix:** use forward slashes and paths relative to the skill directory.

### m12 Loader hygiene problems
- **Detect, definitive:**
  - A frontmatter key is unknown to Claude Code (often a typo; see [Frontmatter fields](#frontmatter-fields)).
  - `agent` or `background` is set without `context: fork` (a dead key).
  - `name` contains `anthropic` or `claude`, which blocks upload to claude.ai and the API.
  - `description` plus `when_to_use` exceeds 1536 characters (the skill listing truncates the rest).
- **Detect, heuristic:** a literal `$ARGUMENTS`, `$ARGUMENTS[N]`, or `$N` inside teaching text or an example. Claude Code substitutes it at invocation, so the example no longer reads as written.
- **Fix:** correct the key, remove the dead key, rename, shorten, and escape or move teaching examples into `references/`.

### m13 Unclear script contract
- **Detect:** SKILL.md references a script without saying whether to run it or read it, or a script needs packages or tools that SKILL.md does not name.
- **Fix:** "Run `python scripts/x.py <in>`" or "Read `scripts/x.py` for the algorithm". List the requirements ("Requires pypdf: `pip install pypdf`").

### m14 MCP tool named without its server
- **Detect:** instructions name an MCP tool without its server. Accept both `Server:tool_name` and `mcp__server__tool_name`.
- **Fix:** qualify every MCP tool name.

### m15 Emphasis overuse without reasons
- **Detect:** three or more all-caps directives (MUST, NEVER, ALWAYS, CRITICAL, IMPORTANT, REQUIRED, MANDATORY) in SKILL.md, outside code and quotes, that give no reason. Newer models over-apply shouted rules.
- **Fix:** state the rule in plain words with its reason: "Keep the original filename, because downstream tools match on it."

## Style rules

Style findings are listed under "Style notes (not graded)". Auto-Fix applies them only when the user asks.

- **S1 Workflows or examples not wrapped in XML tags:** SKILL.md has no `<instructions>` block around its workflow (definitive), or has worked examples outside `<example>` tags (heuristic; the validator checks only the first part).
- **S2 Fewer than 3 or more than 5 example blocks:** count the lines in SKILL.md that open with `<example>`, outside code fences.
- **S3 SKILL.md over 400 lines or about 5k tokens:** more than 400 lines, or more than 20,000 characters counted with LF line endings.
- **S4 Unexpected files in the skill root:** the root may hold only `SKILL.md`, `LICENSE*`, `scripts/`, `references/`, `assets/`, `evals/`, and `tests/`. Dotfiles are ignored.
- **S5 No evals:** `evals/evals.json` is missing or has fewer than 3 cases, or `evals/trigger_queries.json` is missing. Packaging strips `evals/`, so this rule never affects the grade.
- **S6 Description does not open with a third-person verb:** the first word should be a third-person verb ("Extracts", "Reviews"), not "Use" or a noun. Skipped while the description still contains `[TODO`.
- **S7 Mixed filename separators in one skill:** files under `references/` mix `-` and `_` separators.

## Frontmatter fields

**Claude Code** accepts exactly these 20 keys (anything else is m12; verify the list against the Claude Code skills docs when it changes):

| Key | Key | Key | Key |
|-----|-----|-----|-----|
| `name` | `description` | `when_to_use` | `argument-hint` |
| `arguments` | `disable-model-invocation` | `user-invocable` | `allowed-tools` |
| `disallowed-tools` | `model` | `effort` | `context` |
| `agent` | `background` | `hooks` | `paths` |
| `shell` | `metadata` | `license` | `compatibility` |

Plugin skills keep all 20 keys in both Claude Code and Cowork.

The **portable** platform target accepts only `name`, `description`, `license`, `compatibility` (at most 500 characters), `metadata` (string-to-string map), and `allowed-tools`. Anything else is M9 for portable. A standalone skill upload to claude.ai, which is also how Cowork would load a loose skill, accepts only these six.

`allowed-tools` pre-approves the listed tools for the invoking turn. It does not restrict which tools exist; `disallowed-tools` removes tools.

## Validator contract

`create-skill/scripts/quick_validate.py <skill-dir> [--portable]` prints one line per finding, in this format:

```text
[<ID>] <major|minor|style> <definitive|check> <file>:<line> <message>
```

It then prints a summary line:

```text
RESULT major=<n> minor=<n> style=<n> checks=<n>
```

The counts are numbers of definitive finding lines; `checks` counts heuristic leads. One rule ID can print several lines (one per location), while grading counts each ID once. F triggers print as `[F] major definitive` lines and count as Major in `RESULT` and the exit code; the grade is then F. An unexpected internal error exits 3, never 1.

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | No definitive Major or Minor |
| 1 | At least one definitive Major |
| 2 | Usage error |
| 3 | Environment error (PyYAML missing: `python -m pip install pyyaml`; unreadable file) |
| 4 | Definitive Minor only |

`check` lines and Style findings never change the exit code. `validate_skill(path)` returns `(valid, message, warnings)`, where `valid` means no definitive Major. `package_skill.py` relies on that return value.

**Other scripts:**

| Script | Usage |
|--------|-------|
| `init_skill.py` | `<name> --path <dir> [--fork] [--resources scripts,references,assets]` |
| `package_skill.py` | `<skill-dir> [output-dir]`; builds a single-skill zip for claude.ai and the API, never for Cowork (Cowork installs the plugin), so it validates against the portable platform target. It refuses when a definitive Major remains, when the output folder is inside the skill, when `.security-scan-passed` is missing or no longer matches the content, when the skill contains a symlink or junction, or when SKILL.md references a bundled file the zip leaves out (a reference to a local `.env` file or virtualenv is only a warning). The zip leaves out the top-level `evals/`, `.git/`, `__pycache__/`, `node_modules/`, `.venv/`, `venv/`, `.env` files and folders except `.env.example`, `*.pyc`, `*.zip`, OS junk files, and the marker. Exit codes: 0 packaged, 1 refused or failed (including a missing or broken sibling script), 2 usage error; refusals and errors go to stderr. |
| `security_scan.py` | `<skill-dir> [--verbose] [--no-marker]`; exit 0 clean, 1 high-severity secrets, 2 critical secrets, 3 gitleaks not installed, 4 scan or usage error. Pattern leads from `--verbose` never change the exit code. A clean scan writes `.security-scan-passed` unless `--no-marker` is given. |

**security_scan.py findings map to rules:**

| Finding | Rule |
|---------|------|
| gitleaks secret | `[M10] major definitive` |
| Dangerous code, a network call, or a gitleaks config shipped in the skill | `[M10] major check` |
| User-specific path | `[m11] minor check` |
| Email address, plain-HTTP URL, a link that was not followed, or an unreadable file | `[info]`, no rule |

security_scan.py ends with `RESULT secrets=<n> leads=<n>` once the scan has started; usage errors, a target that is not a folder, and internal errors exit 4 with a one-line message instead. Treat exit 1 or 2 as secrets only when the `RESULT` line shows `secrets` above 0. gitleaks always scans a temporary copy of the skill's regular files, so links are never followed and a gitleaks config inside the skill (an `[M10] major check` lead) is left out.

**Evals format** (field-compatible with Anthropic's skill-creator):

```jsonc
// evals/evals.json
{"skill_name": "my-skill",
 "evals": [{"id": 1, "prompt": "...", "expected_output": "...", "files": [], "expectations": ["..."]}]}
```

```jsonc
// evals/trigger_queries.json
[{"query": "...", "should_trigger": true}, {"query": "...", "should_trigger": false}]
```
