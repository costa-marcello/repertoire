---
name: create-skill
description: "Creates, updates, and validates skills for Claude Code and Cowork (SKILL.md, scripts, references, evals) so they pass review-skill on the first run. Use when the user wants to create a new skill, turn a repeated workflow into a skill, add a skill to a plugin, improve or restructure an existing skill, or asks about skill structure, frontmatter, or evals. Grading a skill or only fixing its review findings belongs to review-skill."
license: MIT
argument-hint: "[skill-name] [what it should do]"
---

# Create Skill

Builds skills evals-first: write eval cases, measure Claude without the skill, write the smallest skill that closes the gaps, then validate until review-skill grades it A with zero Style notes. Every graded rule is in `references/authoring_rules.md`. Write to it from the first draft, because fixing afterwards costs extra passes.

User input: $ARGUMENTS

Read the user input as `[skill-name] [what it should do]`:

- **Name and purpose:** take both from it and ask only about what is missing (step 1).
- **Name only, or empty:** mine the conversation first (a workflow the user just walked through is the best source), then ask for the rest.
- **A path or the name of an existing skill:** this is an update. Follow the update notes in steps 1, 2, 4, 5, and 6.
- **A question about skill structure, frontmatter, or evals:** answer it from the matching reference file (table at the end) and stop.

## Ground rules

- **Edit at the source location, never in `~/.claude/plugins/cache/`,** which every plugin refresh overwrites. If the path contains `/plugins/cache/`, find the source repository or ask the user where it lives.
- **Skill folder:** Use `${CLAUDE_SKILL_DIR}` unless it is blank, unexpanded, or a bundled file proves missing there. Then use the "Base directory for this skill" if it holds `scripts/quick_validate.py`, else the folder two levels above the last match Glob lists for `**/create-skill/scripts/quick_validate.py` in `~/.claude`. That folder replaces `CLAUDE_SKILL_DIR` and anchors every relative bundled path. If nothing matches, say the scripts and references were not found and follow this file alone.
- **Requirements:** `python` 3.10 or later (`python3` only where `python` is missing; on Windows it is often the Microsoft Store stub; older versions skip quick_validate's m13 import check); PyYAML for quick_validate and package_skill (`python -m pip install pyyaml`); gitleaks for security_scan. Ask the user before installing anything.
- **No user to reply** (`claude -p`, or running as a subagent): when the input gives a name and purpose, state the plan and the defaults you chose, then continue. Each question takes its stated default; a question with none, or a step that stops to ask, ends the run with the step 10 report. Never install anything then; report the missing tool.
- **Refused writes:** when a write into a skills folder is refused, ask the user to allow it or to choose another location; never work around the permission. With no user to reply, report the refusal and stop.
- **Workspace:** keep eval drafts, snapshots, and run outputs in `<skill-name>-workspace/` in the session scratchpad or the system temp directory, outside every skill directory: stray files in a skill's root are an S4 finding, and a draft in the baseline's reach spoils it.

## Workflow

<instructions>

Copy this checklist into the todo list or the reply, and tick items as they complete:

```text
Skill progress:
- [ ] 1. Capture intent (purpose, triggers, output, name, location, target)
- [ ] 2. Write evals and run the baseline, before the skill directory exists
- [ ] 3. Plan the contents and the fork decision; get the user's go-ahead
- [ ] 4. Initialize the skill directory with init_skill.py
- [ ] 5. Write the skill
- [ ] 6. Validate: quick_validate and Cowork check, eval runs, review gate, regression for updates
- [ ] 7. Sanitize, only if the user agrees; validate again after changes
- [ ] 8. Security scan
- [ ] 9. Package and update the marketplace, only for distribution
- [ ] 10. Iterate on real use (at most 2 rounds), then report
```

### Step 1: Capture intent

1. Extract what the conversation already shows: tools used, the order of steps, the user's corrections, and the input and output formats.
2. Ask only for what is still missing, in one message (AskUserQuestion when available): what the skill does, what a user would type to trigger it, what it produces, and where it lives.
3. Defaults, unless the user says otherwise:
   - **Location:** in Cowork, the connected folder; in a plugin repository (`.claude-plugin/` at its root), its `skills/<skill-name>/`; otherwise `.claude/skills/<skill-name>/` in the current project, or `~/.claude/skills/<skill-name>/` for a personal skill. For Cowork or a plugin repository, follow "Where a new skill goes" in `references/distribution.md`.
   - **Target:** `claude-code`, meaning Claude Code and Cowork, which both get every frontmatter field through the plugin; Cowork is never a reason to switch or to drop fields. Use `portable` only for a single-skill upload to claude.ai or the Claude API, or another Agent Skills client: it adds `name` and allows only the portable fields in `references/frontmatter_reference.md`.
   - **Name:** lowercase letters, digits, and single hyphens, at most 64 characters, equal to the directory name, and specific (`pdf-forms`, not `helper`).
4. **Updates:** read the whole skill first (SKILL.md, every reference file, every script). Keep its name and directory, and copy it to `<workspace>/skill-snapshot/` before any edit. The snapshot is the baseline.

Move on when the purpose fits in one sentence and you can name three realistic requests and the expected output.

### Step 2: Write evals and run the baseline

Read `references/evals_guide.md` for formats, prompts, isolation, and grading.

1. In the workspace, write `evals/evals.json` (3 realistic eval cases) and `evals/trigger_queries.json` (10 trigger queries: 5 that should trigger, 5 near-misses that should not). For a `disable-model-invocation: true` skill, mark all 10 `should_trigger: false` and skip the trigger check, because Claude never sees its description.
2. Run the baseline before step 4, so no draft exists for it to pick up: one fresh general-purpose subagent per eval case, all in the same turn, with the baseline prompt from `references/evals_guide.md`, which never mentions a skill. For an update, the baseline follows the snapshot.
3. **Isolate every eval subagent** (here and in step 6), because it acts in the user's real environment and cannot ask anyone: only an inputs folder and an output folder (never one holding `evals.json`), a local bare repository as any remote, and `would_run.txt` for any command that pushes, publishes, posts, or sends.
4. Record what each baseline run got wrong, skipped, or worked out from scratch. That list is what the skill teaches; leave out what the baseline already does well.
5. If the baseline meets every expectation, the skill may add little or the cases are too easy: ask the user whether to continue (the default) or harden them.
6. **Without subagents:** skip the baseline; run the cases yourself in step 6.

### Step 3: Plan the contents

Read `references/authoring_rules.md` now if it is not loaded, and `references/bundled_resources.md` for resource decisions.

1. **Freedom level** per section (`references/anthropic_guidance.md`): exact commands or a script for fragile, ordered operations (migrations, releases); heuristics with a default for open-ended work (review, analysis).
2. **Resources:** a script when the baseline runs wrote the same code each time; a reference file for knowledge needed in only some runs; an asset for files copied into the output.
3. **Frontmatter:** start from `name`, `description`, and `license`. For the claude-code target, add `argument-hint` when the skill takes input, and `disable-model-invocation: true` for side effects the user should trigger (deploys, releases). Other fields: `references/frontmatter_reference.md`.
4. **Fork decision:** run the fork decision test in "Deciding on context: fork" in `references/authoring_rules.md`. Default to inline; fork only when all five of its conditions hold.
5. Show the plan in a few lines (name, draft description, files, freedom level, fork decision) and wait for the user's go-ahead before creating files.

### Step 4: Initialize the skill directory

Skip this step for updates. Run the command below, listing only the resource directories the plan needs, and add `--fork` only when the fork decision test passed:

```bash
python scripts/init_skill.py <skill-name> --path <parent-dir> --resources scripts,references
```

It creates `<parent-dir>/<skill-name>/` with a SKILL.md template, `evals/` skeletons, and the listed empty resource directories; on exit 1 it leaves nothing behind. Copy the workspace's `evals.json` and `trigger_queries.json` over the skeletons in `<skill-dir>/evals/`.

### Step 5: Write the skill

Read `references/anthropic_guidance.md` for the description and body.

1. **Description first:** what the skill does, then "Use when..." with the triggers, key use case first. A third-person verb opening, no "I" or "you"; a little pushy (Claude under-triggers skills), never all-caps; at most 1,024 characters, no angle brackets.
2. **Lead with what matters:** after compaction, Claude Code re-attaches only the first 5,000 tokens of an invoked skill. Explain why instead of shouting, give a default instead of a menu, and spend words on what the baseline got wrong.
3. **Directives, scripts, paths:** a command, a check, or "Default to X; use Y when Z" (the M7 weak verbs fail review); "Run ..." or "Read ... for ..." for each script, with the packages it needs; own files through `CLAUDE_SKILL_DIR` or forward-slash relative paths plus the skill-folder block (`references/bundled_resources.md`), never an install location.
4. **Keep out of SKILL.md** (see `references/frontmatter_reference.md`): teaching examples with argument-substitution tokens, which are substituted on invocation, and dynamic context injection, which Cowork replaces with a placeholder.
5. **Structure:** the workflow in one `<instructions>` block and 3 to 5 short `<example>` blocks; SKILL.md under 400 lines and 20,000 characters; detail in `references/`, each file linked from SKILL.md with when to read it, and a `## Contents` list in any reference over 100 lines.
6. Replace every TODO placeholder, and delete any resource directory the skill does not use.
7. **Updates:** after each change, grep SKILL.md and `references/` for every fact you changed (defaults, paths, thresholds) and update each copy, so no two files disagree.

### Step 6: Validate

A pass runs all three layers. Fix what they find, then start the next pass. Stop after 3 passes.

**Layer 1: quick_validate and the Cowork check.** Run:

```bash
python scripts/quick_validate.py <skill-dir>   # append --portable for the portable target
```

On exit 1, fix each `major` line, `[F]` lines (F triggers) first; on 4, each `minor` line; on 2, check the path argument; on 3, install PyYAML (ask first) or fix the unreadable file, otherwise report the error. Exit 0 (no definitive Major or Minor) is not enough: the `RESULT` line must also show `style=0`. Each `check` line is a lead: read the cited line, then fix it or dismiss it with a reason.

Then run the Cowork check (M11, both targets; see `references/authoring_rules.md`). Read the skill for what quick_validate misses:
- **No display:** results go to files (in Cowork, the outputs folder), never a window or browser.
- **Own files** through `CLAUDE_SKILL_DIR` and the skill-folder block (scripts: `Path(__file__)`), never an install location.
- **No dynamic context injection** in SKILL.md, code fences included.
- **Local services** (a stdio MCP server, `localhost`) have a stated fallback; no `claude -p`.
- **Secrets** from environment variables, not only a home-directory dotfile.

**Layer 2: eval runs.** Dispatch one fresh with-skill subagent per eval case, all in the same turn, with the with-skill prompt from `references/evals_guide.md` (a copy of the skill without `evals/`, isolated as in step 2). Grade each expectation against the baseline, and read the transcripts too: wasted steps point to instructions to cut.

**Layer 3: review-skill gate.** Dispatch a fresh subagent each pass with: `Invoke repertoire:review-skill, or review-skill if that name is unknown, with "<absolute-skill-dir>" report only, and return the full report.` Append `portable` for the portable target. The gate is report-only, so M12 "Fails its own evals" never runs inside it.
- If it cannot invoke review-skill, it reads review-skill's SKILL.md from the first of `${CLAUDE_SKILL_DIR}/../review-skill/`, `review-skill/` under `.claude/skills/`, `.agents/skills/`, or `~/.agents/skills/`, or the last match Glob lists for `**/*review-skill/SKILL.md` in `~/.claude` or `/mnt/skills`, and follows its report-only mode.
- If review-skill is unavailable, apply `references/authoring_rules.md` yourself, rule by rule with quoted evidence, and say the gate did not run.

**Updates: regression run.** Once a pass is clean, invoke `repertoire:review-skill` (or `review-skill`) from this conversation, never a subagent, with `"<absolute-skill-dir>" report only regression`. It asks the user (default: yes), then re-runs each case in the skill's `evals/evals.json` and repeats a failing case once; you make the fixes. Without review-skill, follow "Regression runs" in `references/evals_guide.md`. A case that fails twice blocks finishing: fix the skill, or a wrong expectation (say why), and run it again. Inside an eval run (a subagent confined to an inputs and an output folder), skip it and say so.

**The bar:** Grade A (0 Major, 0 Minor) with zero Style notes, a clean Layer 1, with-skill runs that meet the expectations the baseline missed, and for an update no case failing the regression twice. In an update, findings in parts the change did not touch go to the user as a separate list and do not block the bar. After the third pass, stop: report the remaining findings with their locations, and ask the user whether to accept them, keep fixing, or change the scope.

### Step 7: Sanitize (optional)

When the skill came from a business or internal project and will be shared, ask first (default: no) whether to remove company names, people, internal paths, and jargon. On a yes, follow `references/sanitization_checklist.md`; if anything changed, run step 6 again (at most 2 passes) and report what remains.

### Step 8: Security scan

Run `python scripts/security_scan.py <skill-dir> --verbose --no-marker`; `--verbose` adds pattern checks for dangerous code and network calls.

- **Exit 1 or 2 with `secrets` above 0:** each secret is M10; move it to an environment variable and scan again. On any other exit 1, 2, or 4, read the error and fix the cause.
- **Exit 3 (no gitleaks):** relay the install instructions it prints and ask whether to install; if the user declines, report that the scan did not run.
- **Leads:** confirm each `[M10] major check` line (remove the call, or disclose the network use and its purpose in SKILL.md), and replace the user-specific path behind each `[m11] minor check` line.
- **Marker:** drop `--no-marker` only when step 9 packages a zip, which needs the `.security-scan-passed` marker. Scan again after any later edit.

### Step 9: Package and update the marketplace

Default: skip packaging. A zip is for claude.ai and the Claude API, not Cowork, which installs the plugin. For such an upload ("Packaging a zip" in `references/distribution.md`), run `python scripts/package_skill.py <skill-dir> [output-dir]`. It refuses whatever fails the portable target, such as `argument-hint`, and a missing or stale scan marker (run step 8 again).

Update the marketplace only when `.claude-plugin/marketplace.json` exists at the repository root: follow `references/marketplace_update.md`, then run `claude plugin validate .`, or its by-hand check where the `claude` CLI is missing. For a plugin, tell the user to push the change ("Shipping a change" in `references/distribution.md`).

### Step 10: Iterate and report

Run at most 2 rounds of items 1 to 3. If failures remain after round 2, stop, list them, and ask the user whether to continue.

1. **Claude A / Claude B:** a fresh instance (Claude B) uses the skill on real tasks while this session (Claude A) edits it; note where B hesitates or skips a file or section.
2. **Models:** run the with-skill evals on Haiku, Sonnet, and Opus (the Agent tool's model setting).
3. **Fixes:** for each failure, add an eval case that reproduces it and run its baseline by the late-baseline rule in `references/evals_guide.md`. Make the smallest fix in the responsible section, and run step 6 again. Add only what fixes an observed failure.
4. **Real trigger measurement:** "Upgrade paths" in `references/evals_guide.md`.
5. **Report to the user:** the skill path, the final quick_validate `RESULT` line, the review-skill grade (or that the gate did not run), baseline versus with-skill results per eval case, the regression result for an update, and every skipped step with its reason.

</instructions>

## Examples

<example>
**Input (in a plugin repository):** `/create-skill csv-report Summarise a CSV file into a Markdown table of row counts and column types`

1. Name and purpose come from the input. `.claude-plugin/` exists, so the skill goes to `skills/csv-report/`; the repository has the link script and `~/.claude/skills/<plugin-name>` is missing, so tell the user to run `python -B scripts/link_user_skills.py` once.
2. 3 eval cases (clean, semicolon-delimited, missing file): every baseline run writes the same parsing code, and two miss the semicolon.
3. Bundle a script (low freedom). The fork decision test passes: initialize with `--fork --resources scripts`, then write and validate.
</example>

<example>
**Input:** "The changelog skill said 'No release needed' on a repo where every PR lands as a merge commit. Fix it."

1. Update: find the source copy (not the plugin cache), read every file, and snapshot it to the workspace.
2. Add an eval case for the failure (conventional-commit titles only in merge-commit bodies); the snapshot baseline reports no release.
3. Count a merge commit whose body opens with a conventional-commit subject as that commit, update every copy of the rule, and validate. The `regression` run passes the new case and every old one.
</example>

<example>
**Input (claude.ai chat, no subagents, review-skill not installed):** "Make me a skill that turns meeting transcripts into decisions and action items."

1. Portable target: only portable frontmatter fields; validate with `--portable`.
2. Skip the baseline, run each eval case yourself, apply `references/authoring_rules.md` rule by rule, and say the review-skill gate did not run.
3. Without gitleaks, `scripts/package_skill.py` refuses: tell the user to install it and package on their own machine.
</example>

## Reference files

| File | When to read it |
|------|-----------------|
| `references/authoring_rules.md` | Before step 3, for step 6's Cowork check, and while fixing: graded rules, fork decision test |
| `references/anthropic_guidance.md` | Before step 5: descriptions, conciseness, freedom levels |
| `references/frontmatter_reference.md` | When choosing frontmatter fields or substitutions |
| `references/bundled_resources.md` | In step 3: scripts, references, assets, naming, paths |
| `references/evals_guide.md` | In steps 2, 6, and 10: formats, prompts, isolation, regression runs |
| `references/worked_examples.md` | For end-to-end walkthroughs |
| `references/distribution.md` | In step 1 for Cowork or a plugin repository, and in step 9 |
| `references/sanitization_checklist.md` | In step 7 |
| `references/marketplace_update.md` | In step 9, when `.claude-plugin/marketplace.json` exists |
