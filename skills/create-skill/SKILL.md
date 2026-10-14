---
name: create-skill
description: "Creates, updates, and validates Claude Code skills (SKILL.md, scripts, references, evals) so they pass review-skill on the first run. Use when the user wants to create a new skill, turn a repeated workflow into a skill, improve or restructure an existing skill, or asks about skill structure, frontmatter, or evals."
license: MIT
argument-hint: "[skill-name] [what it should do]"
---

# Create Skill

Builds skills evals-first: write eval cases, measure Claude without the skill, write the smallest skill that closes the gaps, then validate until review-skill grades it A with zero Style notes. Every graded rule is in `references/authoring_rules.md`. Write to it from the first draft, because fixing afterwards costs extra passes.

User input: $ARGUMENTS

Read the user input as `[skill-name] [what it should do]`:

- **Name and purpose:** take both from it and ask only about what is missing (step 1).
- **Name only, or empty:** mine the conversation first (a workflow the user just walked through is the best source), then ask for the rest.
- **A path or the name of an existing skill:** this is an update. Follow the update notes in steps 1, 2, 4, and 5.
- **A question about skill structure, frontmatter, or evals:** answer it from the matching reference file (table at the end) and stop.

## Ground rules

- **Edit at the source location, never in `~/.claude/plugins/cache/`.** The cache is overwritten on every plugin refresh. If the path contains `/plugins/cache/`, find the source repository or ask the user where it lives.
- **Python:** run `python`; use `python3` only where `python` is not on the path (on Windows `python3` is often the Microsoft Store stub).
- **Script paths** are relative to this skill's directory, not the working directory. In Claude Code that is `${CLAUDE_SKILL_DIR}`, so `scripts/quick_validate.py` means `${CLAUDE_SKILL_DIR}/scripts/quick_validate.py`. Quote paths that contain spaces.
- **Requirements:** Python 3.10 or later for quick_validate's full checks (older versions skip its m13 import check); PyYAML for quick_validate and package_skill (`python -m pip install pyyaml`); gitleaks for security_scan, whose clean scan packaging requires. Ask the user before installing anything.
- **No user to reply** (`claude -p`, or running as a subagent): when the input gives a name and purpose, state the plan and the defaults you chose, then continue. Each question takes its stated default, and a step that stops to ask ends the run with the step 10 report. Never install anything then; report the missing tool.
- **Refused writes:** when a write into `.claude/skills/` is refused, ask the user to allow it or to choose another location, and never work around the permission. With no user to reply, report the refusal and stop.
- **Workspace:** keep eval drafts, snapshots, and run outputs in one workspace per skill, outside every skill directory. Default to `<skill-name>-workspace/` in the session scratchpad or the system temp directory. Stray files in a skill's root are an S4 finding, and a draft in the baseline's reach spoils it.

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
- [ ] 6. Validate: quick_validate, eval runs, review-skill gate (at most 3 passes)
- [ ] 7. Sanitize, only if the user agrees; validate again after changes
- [ ] 8. Security scan
- [ ] 9. Package and update the marketplace, only for distribution
- [ ] 10. Iterate on real use (at most 2 rounds), then report
```

### Step 1: Capture intent

1. Extract what the conversation already shows: tools used, the order of steps, the user's corrections, and the input and output formats.
2. Ask only for what is still missing, in one message (AskUserQuestion when available): what the skill does, what a user would type to trigger it, what it produces, and where it lives.
3. Defaults, unless the user says otherwise:
   - **Location:** `.claude/skills/<skill-name>/` in the current project. Use `~/.claude/skills/` for a personal skill, and the repository's `skills/` directory in a skill or plugin repository.
   - **Target:** `claude-code`. Switch to `portable` when the user mentions claude.ai, the Claude API, or another Agent Skills client. Portable skills include `name` and use only the portable fields in `references/frontmatter_reference.md`.
   - **Name:** lowercase letters, digits, and single hyphens, at most 64 characters, equal to the directory name, and specific (`pdf-forms`, not `helper`).
4. **Updates:** read the whole skill first (SKILL.md, every reference file, every script). Keep its name and directory, and copy it to `<workspace>/skill-snapshot/` before any edit. The snapshot is the baseline.

Move on when the purpose fits in one sentence and you can name three realistic requests and the expected output.

### Step 2: Write evals and run the baseline

Read `references/evals_guide.md` for the formats, the subagent prompts, isolation, and grading.

1. In the workspace, write `evals/evals.json` (3 realistic eval cases) and `evals/trigger_queries.json` (10 trigger queries: 5 that should trigger, 5 near-misses that should not). For a `disable-model-invocation: true` skill, mark all 10 `should_trigger: false` and skip the trigger check, because Claude never sees its description.
2. Run the baseline before step 4, so no draft exists for it to pick up: one fresh general-purpose subagent per eval case (Agent tool, all in the same turn) with the baseline prompt from `references/evals_guide.md`, which never mentions a skill. For an update, the baseline follows the snapshot.
3. **Isolate every eval subagent** (here and in step 6), because it acts in the user's real environment and cannot ask anyone. It gets only an inputs folder and an output folder (never one holding `evals.json`), works only in the workspace, uses a local bare repository as any remote, and writes any command that pushes to a real remote, publishes, posts, sends, or opens a PR, issue, release, or tag to `would_run.txt` instead of running it. Side-effect cases use local fixtures; the prompts in `references/evals_guide.md` carry these rules.
4. Record what each baseline run got wrong, skipped, or worked out from scratch. That list is what the skill teaches; leave out what the baseline already does well.
5. If the baseline meets every expectation, tell the user the skill may add little or the cases are too easy, and ask whether to continue (the default) or harden the cases.
6. **Without subagents** (for example on claude.ai): skip the baseline, and run the cases yourself one after another in step 6.

### Step 3: Plan the contents

Read `references/authoring_rules.md` now if it is not loaded, and `references/bundled_resources.md` for resource decisions.

1. **Freedom level** per section (`references/anthropic_guidance.md`): exact commands or a script for fragile, ordered operations (migrations, releases); a preferred pattern with parameters where variation is fine; heuristics with a default for open-ended work (review, analysis).
2. **Resources:** a script when the baseline runs wrote the same code each time; a reference file for knowledge needed in only some runs; an asset for files copied into the output.
3. **Frontmatter:** start from `name`, `description`, and `license`. Add `argument-hint` when the skill takes input, and `disable-model-invocation: true` for side effects the user should trigger (deploys, releases). Other fields: `references/frontmatter_reference.md`.
4. **Fork decision:** run the fork decision test in "Deciding on context: fork" in `references/authoring_rules.md`. Default to inline; fork only when all five of its conditions hold.
5. Show the plan in a few lines (name, draft description, files, freedom level, fork decision) and wait for the user's go-ahead before creating files.

### Step 4: Initialize the skill directory

Skip this step for updates. Run the command below, listing only the resource directories the plan needs, and add `--fork` only when the fork decision test passed:

```bash
python scripts/init_skill.py <skill-name> --path <parent-dir> --resources scripts,references
```

It creates `<parent-dir>/<skill-name>/` with a SKILL.md template, skeleton files in `evals/`, and the listed resource directories, empty. On exit 1 it leaves nothing behind. Copy the workspace's `evals.json` and `trigger_queries.json` over the skeletons in `<skill-dir>/evals/`.

### Step 5: Write the skill

Read `references/anthropic_guidance.md` for the description and body.

1. **Description first:** what the skill does, then "Use when..." with the triggers, key use case first. Open with a third-person verb, no "I" or "you"; a little pushy (Claude tends to under-trigger skills), never all-caps; at most 1,024 characters, no angle brackets.
2. **Lead with what matters:** after compaction, Claude Code re-attaches only the first 5,000 tokens of an invoked skill. Explain why instead of shouting, give a default instead of a menu, and spend words on what the baseline got wrong.
3. **Directives, scripts, paths:** a command, a check, or "Default to X; use Y when Z" (the M7 weak verbs fail review); "Run ..." or "Read ... for ..." for each script, with the packages it needs; forward-slash paths relative to the skill directory.
4. **Keep out of SKILL.md** (see `references/frontmatter_reference.md`): teaching examples with argument-substitution tokens, which are substituted on invocation, and dynamic context injection, which runs on every invocation.
5. **Structure:** the workflow in one `<instructions>` block and 3 to 5 short `<example>` blocks; SKILL.md under 400 lines and 20,000 characters; detail in `references/`, each file linked directly from SKILL.md with when to read it; a `## Contents` list in the first 30 lines of any reference file over 100 lines.
6. Replace every TODO placeholder, and delete any resource directory the skill does not use.
7. **Updates:** after each change, grep SKILL.md and `references/` for every fact you changed (defaults, paths, thresholds) and update each copy, so no two files disagree.

### Step 6: Validate

A pass runs all three layers. Fix what they find, then start the next pass. Stop after 3 passes.

**Layer 1: quick_validate.** Run:

```bash
python scripts/quick_validate.py <skill-dir>   # append --portable for the portable target
```

| Exit | Meaning | Action |
|------|---------|--------|
| 0 | No definitive Major or Minor | Continue, after the checks below |
| 1 | At least one definitive Major | Fix each `major` line, `[F]` lines (F triggers) first |
| 4 | Definitive Minor only | Fix each `minor` line |
| 2 | Usage error | Check the path argument |
| 3 | Environment or internal error | Install PyYAML or fix the unreadable file; otherwise report the error |

Findings print as `[ID] severity confidence file:line message`, followed by a `RESULT` line with the counts. Exit 0 is not enough: `RESULT` must also show `style=0`. Each `check` line is a lead: read the cited line, then fix it or dismiss it with a reason.

**Layer 2: eval runs.** Dispatch one fresh with-skill subagent per eval case, all in the same turn, with the with-skill prompt from `references/evals_guide.md`: it reads a copy of the skill without `evals/` and follows the isolation rules of step 2. Grade each expectation and compare the result with the baseline. Read the transcripts as well as the outputs: wasted steps point to instructions to cut.

**Layer 3: review-skill gate.** Dispatch a fresh subagent each pass with: `Run /review-skill "<absolute-skill-dir>" report only and return the full report.` The quotes keep a path with spaces as one argument. Append `portable` for the portable target.
- If it cannot invoke review-skill, it reads review-skill's SKILL.md (`../review-skill/` beside this skill, `.claude/skills/review-skill/`, or `~/.claude/skills/review-skill/`) and follows its report-only mode.
- If review-skill is unavailable, apply `references/authoring_rules.md` yourself, rule by rule with quoted evidence, and tell the user the review-skill gate did not run.

**The bar:** Grade A (0 Major, 0 Minor) with zero Style notes, a clean Layer 1, and with-skill runs that meet the expectations the baseline missed. After the third pass, stop: report the remaining findings with their locations, and ask the user whether to accept them, keep fixing, or change the scope.

### Step 7: Sanitize (optional)

When the skill came from a business or internal project and will be shared, ask first (default: no) whether to run a sanitization pass that removes company names, people, internal paths, and jargon. Skip it for public skills built from scratch, private skills, and when the user declines. On a yes, follow `references/sanitization_checklist.md`. If anything changed, run step 6 again with at most 2 passes, then report what remains.

### Step 8: Security scan

Run:

```bash
python scripts/security_scan.py <skill-dir> --verbose
```

`--verbose` adds the pattern checks for dangerous code and network calls; without it, only gitleaks runs. The last line is `RESULT secrets=<n> leads=<n>`.

- **Exit 1 or 2:** secrets only when `RESULT` shows `secrets` above 0. Each is M10: move it to an environment variable and scan again. Otherwise, and on exit 4 (scan or usage error), read the error and fix the cause.
- **gitleaks missing (exit 3):** relay the install instructions it prints (`winget install gitleaks` on Windows, `brew install gitleaks` on macOS) and ask whether to install. If the user declines, report that the scan did not run, so step 9 cannot package the skill.
- **Leads:** confirm each `[M10] major check` line (dangerous code, network calls): remove the call, or disclose the network use and its purpose in SKILL.md. Each `[m11] minor check` line is a user-specific path to replace.
- **Marker:** a clean scan writes `.security-scan-passed` into the skill directory. Pass `--no-marker` when the skill will not be packaged. Scan again after any later edit.

### Step 9: Package and update the marketplace

Default: skip packaging for a skill used in place (`.claude/skills/`, `~/.claude/skills/`, a plugin repository). Package when the user wants a zip, for example for claude.ai:

```bash
python scripts/package_skill.py <skill-dir> [output-dir]
```

It writes `<skill-name>.zip` to the output directory (default: the current directory) and leaves out `evals/`, caches, `.git`, OS files, `.env` files (not `.env.example`), zips, and the scan marker. It refuses on a definitive Major, a link inside the skill, an output directory inside the skill, or when the security marker is missing or no longer matches the content; in that last case, run step 8 again. Only a clean gitleaks scan writes the marker, so without gitleaks the skill cannot be packaged: tell the user, with the install command from step 8.

Update the marketplace only when `.claude-plugin/marketplace.json` exists at the repository root: follow `references/marketplace_update.md`, then run `claude plugin validate .`. Otherwise skip it.

### Step 10: Iterate and report

Run at most 2 rounds of items 1 to 3. When failures remain after the second round, stop, list them, and ask the user whether to continue.

1. **Claude A / Claude B:** a fresh instance (Claude B) uses the skill on real tasks while this session (Claude A) edits it. Note where Claude B hesitates, reads files out of order, misses a reference file, or ignores a section.
2. **Models:** run the with-skill evals on Haiku, Sonnet, and Opus (the Agent tool's model setting).
3. **Fixes:** for each failure, add an eval case that reproduces it and run its baseline by the late-baseline rule in `references/evals_guide.md`. Find the responsible section, make the smallest fix, and run step 6 again. Add only what fixes an observed failure.
4. **Real trigger measurement:** see "Upgrade paths" in `references/evals_guide.md`; `claude plugin eval` needs a plugin (a `plugin.json` or a skills-directory plugin).
5. **Report to the user:** the skill path, the final quick_validate `RESULT` line, the review-skill grade (or that the gate did not run), baseline versus with-skill results per eval case, and every skipped step with its reason.

</instructions>

## Examples

<example>
**Input:** `/create-skill csv-report Summarise a CSV file into a Markdown table of row counts and column types`

1. Name and purpose come from the input; ask only where it lives (default `.claude/skills/csv-report/`).
2. Write 3 eval cases (clean, semicolon-delimited, missing file). In the baseline, all three runs write the same parsing code, and two miss the semicolon delimiter.
3. Bundle a script (low freedom). The fork decision test passes, so initialize with `--fork --resources scripts`, write, and validate until Grade A with zero Style notes.
</example>

<example>
**Input:** "The changelog skill said 'No release needed' on a repo where every PR lands as a merge commit. Fix it."

1. Update: find the source copy (not the plugin cache), read every file, and snapshot it to the workspace.
2. Add an eval case for the failure (conventional-commit titles only in merge-commit bodies); against the snapshot, the baseline reports no release.
3. Count a merge commit whose body opens with a conventional-commit subject as that commit, update every copy of the old rule, and validate: the new case produces a release entry, and the old cases still pass.
</example>

<example>
**Input:** "Turn the release checklist we just walked through into a skill."

1. Take the steps, commands, and corrections from the conversation; ask only for the name and location.
2. It waits for the user's confirmation before tagging, so it runs inline. Add `disable-model-invocation: true` (the user triggers releases), and mark all 10 trigger queries `should_trigger: false`.
3. Run the eval cases on a fixture repository with a local bare remote, so tags and pushes stay in the workspace. Write the confirmation step and a final check that the tag exists on the remote, then validate.
</example>

<example>
**Input (claude.ai, no subagents, review-skill not installed):** "Make me a skill that turns meeting transcripts into decisions and action items."

1. Portable target: only portable frontmatter fields; validate with `--portable`.
2. Skip the baseline, run each eval case yourself, apply `references/authoring_rules.md` rule by rule, and say the review-skill gate did not run.
3. Packaging needs a clean scan. Without gitleaks there, `scripts/package_skill.py` refuses: say so, and tell the user to install gitleaks (`winget install gitleaks` or `brew install gitleaks`) and package on their own machine.
</example>

## Reference files

| File | When to read it |
|------|-----------------|
| `references/authoring_rules.md` | Before step 3 and while fixing: every graded rule and the fork decision test |
| `references/anthropic_guidance.md` | Before step 5: descriptions, conciseness, freedom levels, scripts, iteration |
| `references/frontmatter_reference.md` | When choosing frontmatter fields, substitutions, or invocation control |
| `references/bundled_resources.md` | In step 3: scripts, references, assets, file naming, paths |
| `references/evals_guide.md` | In steps 2, 6, and 10: formats, subagent prompts, isolation, grading, upgrade paths |
| `references/worked_examples.md` | For end-to-end walkthroughs: an inline guideline skill, a forked task skill, an update |
| `references/sanitization_checklist.md` | In step 7 |
| `references/marketplace_update.md` | In step 9, only when `.claude-plugin/marketplace.json` exists |
