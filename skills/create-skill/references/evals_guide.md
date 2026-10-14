# Evals Guide

How to write a skill's evals, run them with subagents before and after the skill exists, read the results, and when to move to real trigger measurement. The formats are field-compatible with Anthropic's skill-creator, so its tooling can read them.

## Contents

1. [Why evals come first](#why-evals-come-first)
2. [File formats](#file-formats)
3. [Writing eval cases](#writing-eval-cases)
4. [Writing trigger queries](#writing-trigger-queries)
5. [Workspace layout](#workspace-layout)
6. [Isolating eval runs](#isolating-eval-runs)
7. [Running the baseline](#running-the-baseline)
8. [Running with the skill](#running-with-the-skill)
9. [Grading and comparing](#grading-and-comparing)
10. [Regression runs](#regression-runs)
11. [Checking trigger queries](#checking-trigger-queries)
12. [What this approximation cannot measure](#what-this-approximation-cannot-measure)
13. [Upgrade paths](#upgrade-paths)

## Why evals come first

Evals written before the skill measure what Claude gets wrong without it, and that list defines what the skill has to contain. Evals written afterwards tend to test what the skill already says. This is Anthropic's evaluation-driven development (`anthropic_guidance.md`).

## File formats

`evals/evals.json`:

```json
{
  "skill_name": "csv-report",
  "evals": [
    {
      "id": 1,
      "prompt": "my manager dropped q3_orders.csv in the repo root. how many rows, which columns are mostly empty, and do the dates parse?",
      "expected_output": "A Markdown table with one row per column (type, empty share) and a total row count.",
      "files": ["evals/files/q3_orders.csv"],
      "expectations": [
        "Reports the total row count as 1,204",
        "Lists all 9 columns",
        "Flags the 2 columns that are more than 50% empty"
      ]
    }
  ]
}
```

| Field | Meaning |
|-------|---------|
| `skill_name` | Equal to the skill's `name` |
| `id` | Unique integer |
| `prompt` | The request as a real user would type it |
| `expected_output` | One or two sentences describing a good result |
| `files` | Input files, relative to the skill directory; `[]` when there are none |
| `expectations` | Statements that are each checkable as pass or fail |

`evals/trigger_queries.json`:

```json
[
  {"query": "can you profile this csv before I load it into postgres? it's data/raw/customers.csv", "should_trigger": true},
  {"query": "convert data/raw/customers.csv to parquet", "should_trigger": false}
]
```

Write about 10 entries: 5 with `should_trigger: true` and 5 near-misses with `false`. A user-only skill is the exception (see [Writing trigger queries](#writing-trigger-queries)). skill-creator's description optimizer works best with about 20, half of them near-misses, so extend the file before running it. review-skill's S5 check needs 3 or more eval cases and the trigger file to be present.

## Writing eval cases

- **Coverage.** Write three cases: the typical request, a variant (a different input shape or phrasing), and an edge or error case (missing input, a malformed file, or the trap the baseline falls into).
- **Realistic prompts.** Include concrete detail: file names, a bit of context, casual phrasing, sometimes a typo. "Summarise a CSV" tests little; the prompt in the example above tests a lot.
- **Checkable expectations.** A reader or a script should be able to check each one: "Lists all 9 columns", "Detects the semicolon delimiter". "The output is good" cannot be checked.
- **Subjective skills** (writing style, design): use fewer expectations, and plan a qualitative review by the user.
- **Input files.** Put them in `evals/files/` and list them in `files`.
- **Side effects.** A case whose task pushes, tags, releases, posts, or deploys runs against a local fixture listed in `files`, such as a git bundle of a small throwaway repository (`git bundle create repo.bundle --all`, run inside that repository, then moved to `evals/files/`). Its prompt points at the fixture, never at the user's real repository or accounts.

## Writing trigger queries

- **Five should-trigger queries.**
  - Different phrasings of the core intent, formal and casual.
  - At least two indirect ones that never name the skill or its obvious keyword.
  - One where this skill competes with a neighbouring skill and should win.
- **Five near-miss should-not queries.** Each shares keywords or a domain with the skill but needs something else: an adjacent task, a neighbouring skill's job, or a question about the topic rather than a request to do the work.
- **Hard negatives.** An obviously irrelevant negative ("write a fibonacci function" for a CSV skill) tests nothing.
- **Substantive queries.** Claude handles simple one-step requests without consulting any skill, so a trivial should-trigger query fails whatever the description says.
- **User-only skills.** With `disable-model-invocation: true`, Claude never sees the description and can never pick the skill. Mark all 10 queries `should_trigger: false` (Claude must never pick it) and skip [Checking trigger queries](#checking-trigger-queries). S5 still needs the file.

## Workspace layout

```text
<skill-name>-workspace/
  evals/                  drafts of evals.json and trigger_queries.json (step 2); never shown to a subagent
  grading/                iteration-<N>.md comparison tables and check scripts; never shown to a subagent
  inputs/
    eval-1/               copies of eval 1's input files and fixtures
  skill-snapshot/         the old version of the skill, for updates, without its evals/ folder
  snapshot-evals/         the snapshot's evals/ folder, moved out of the baseline's reach
  under-test/
    <skill-name>/         a copy of the draft without evals/, read by with-skill runs
  iteration-1/
    eval-1/
      baseline/           output folder of the baseline run
      with_skill/         output folder of the with-skill run
  iteration-2/
  regression-1/
    eval-1/
      run-1/              output folder of the first regression run
      run-2/              output folder of the repeat, only after a failure
```

Keep the workspace outside every skill directory, for two reasons: files in a skill's root are an S4 finding, and a baseline run must not find a draft of the skill.

## Isolating eval runs

Eval subagents act in the user's real environment, with the user's repositories and accounts, and they cannot ask anyone. A confirmation step in the skill is therefore skipped or improvised, and in bypass or auto-accept permission modes, or for allowlisted commands, nothing asks first. Every baseline and with-skill run follows these rules, and the prompts below carry them:

- **Two folders.** A subagent reads input files only from its inputs folder, `<workspace>/inputs/eval-<id>/`, and works and writes only inside its output folder. With-skill runs also read the skill copy below. Before dispatch, copy the case's `files` into its inputs folder.
- **No expectations in reach.** Never give a subagent `<workspace>/evals/`, `<workspace>/grading/`, `<workspace>/snapshot-evals/`, or a skill's own `evals/` folder: a run that can read its expectations no longer tests anything.
- **Skill copy without evals.** With-skill runs read `<workspace>/under-test/<skill-name>/`. Refresh it before each with-skill round, and dispatch only after it prints `under-test ready`:

  ```bash
  rm -rf "<workspace>/under-test" && mkdir -p "<workspace>/under-test" \
    && cp -R "<skill-dir>" "<workspace>/under-test/<skill-name>" \
    && rm -rf "<workspace>/under-test/<skill-name>/evals" \
    && test -f "<workspace>/under-test/<skill-name>/SKILL.md" && echo "under-test ready"
  ```

  For an update, move `<workspace>/skill-snapshot/evals/` (when it exists) to `<workspace>/snapshot-evals/` before the baseline runs. The two folders together still hold the whole original.
- **No outward side effects.** A subagent clones any repository it needs into its output folder and uses a local bare repository as the remote. It never pushes to a real remote, never publishes, posts, or sends anything, and never opens PRs, issues, releases, or tags on a hosting service. It writes any such command to `would_run.txt` in its output folder instead of running it. Grade that file like any other output.
- **Fresh subagents.** Dispatch a new general-purpose subagent for every run, never one that inherits this conversation, which holds the drafts and the expectations.
- **No regression runs inside.** An eval subagent never starts a regression run (see [Regression runs](#regression-runs)), even when the skill under test asks for one, as create-skill's update flow does; it says that it skipped it.
- **Late baselines.** A baseline that runs while a draft is installed (a case added in step 10, or any baseline after the first edit of an update) can load the draft through the Skill tool. Add "Do not use the Skill tool." to its prompt, check its transcript for Skill tool calls, and rerun it if any appear.

## Running the baseline

- **When.**
  - New skill: before `init_skill.py` runs, so no draft exists that a subagent could discover.
  - Update: snapshot the skill to `<workspace>/skill-snapshot/` first, move its `evals/` folder out (see [Isolating eval runs](#isolating-eval-runs)), and use the snapshot as the baseline.
  - A case added in step 10: follow "Late baselines" in [Isolating eval runs](#isolating-eval-runs).
- **How.** Copy each case's input files into its inputs folder, then dispatch one fresh general-purpose subagent per eval case with the Agent tool, all in the same turn, so they finish together. Prompt for a new skill:

```text
Complete the task below.
No user can answer questions during this run. Where you would ask the user, choose the safest
answer, say which one in your note, and carry on.
Read input files only from <workspace>/inputs/eval-<id>/ (or: none).
Work and write only inside <workspace>/iteration-<N>/eval-<id>/baseline/, and save every output file there.
Clone any repository you need into that folder, and use a local bare repository there as its remote.
Never push to a real remote, never publish, post, or send anything, and never open PRs, issues,
releases, or tags on a hosting service. Write any such command to would_run.txt in that folder
instead of running it, then carry on with the rest of the task.
Finish with a short note: what you did, and anything you were unsure about.

Task: <prompt from evals.json>
```

For an update, replace the first line with "Read `<workspace>/skill-snapshot/SKILL.md` and follow it to complete the task below." For a late baseline, add "Do not use the Skill tool." after the first line.

- **Without subagents** (claude.ai chat): skip the baseline. The comparison then rests on the user's review of the outputs.

## Running with the skill

Refresh `<workspace>/under-test/<skill-name>/` (see [Isolating eval runs](#isolating-eval-runs)), then dispatch one fresh subagent per eval case, all in the same turn:

```text
Read <workspace>/under-test/<skill-name>/SKILL.md and follow it to complete the task below.
Read the reference files and run the scripts it points to, as it directs.
Where it says ${CLAUDE_SKILL_DIR}, use <workspace>/under-test/<skill-name>.
No user can answer questions during this run. Where the skill says to ask the user, choose the
safest answer, say which one in your note, and carry on.
Read input files only from <workspace>/inputs/eval-<id>/ (or: none).
Work and write only inside <workspace>/iteration-<N>/eval-<id>/with_skill/, and save every output file there.
Clone any repository you need into that folder, and use a local bare repository there as its remote.
Never push to a real remote, never publish, post, or send anything, and never open PRs, issues,
releases, or tags on a hosting service. Write any such command to would_run.txt in that folder
instead of running it, then carry on with the rest of the task.
Finish with a short note: what you did, which skill files you read, which questions you answered
yourself, and anything you were unsure about.

Task: <prompt from evals.json>
```

- **Iterations.** Use a new `iteration-<N>/` directory after each round of edits, and keep the old ones for comparison.
- **Models.** Before release, run the with-skill cases at least once on each model the skill will be used with, through the Agent tool's model setting.
- **Without subagents.** Read SKILL.md and follow it for each case yourself, one at a time. This is less rigorous, because the author is also the tester, so ask the user to review the outputs.

## Grading and comparing

Record each expectation for both arms in `<workspace>/grading/iteration-<N>.md`:

| Eval | Expectation | Baseline | With skill | Evidence |
|------|-------------|----------|------------|----------|
| 1 | Detects the semicolon delimiter | fail | pass | `with_skill/report.md` line 3 shows 9 columns |

- **Scripts first.** When an expectation can be checked programmatically, write a small check script in `<workspace>/grading/` (not in the skill) and reuse it each iteration.
- **Transcripts, not just outputs.**
  - Helper code that every run rewrote should become a bundled script.
  - A step that wastes time comes from an instruction to cut.
  - A reference file that was never opened has a link that is not prominent, or is not needed.
- **Non-discriminating expectations** pass in both arms and measure nothing. Replace them with harder ones.
- **Failing in both arms** means the skill does not teach that point yet, or the expectation is wrong.
- **Show the user** the table, and the outputs of subjective cases, before revising.

## Regression runs

A regression run re-runs a skill's own `evals/evals.json` after a change, to show that nothing its cases cover broke. review-skill grades the result as M12 "Fails its own evals".

- **Who runs it.** create-skill's update flow asks review-skill for it, from the main conversation and never from a subagent, because review-skill asks the user before running: invoke `repertoire:review-skill` (or `review-skill` if that name is unknown) with the skill path and `report only regression`. Report only keeps review-skill from fixing untouched parts of the skill. Run it yourself, as below, only when review-skill is unavailable.
- **When not to.** Never inside an eval subagent and never inside the Layer 3 review gate, and only on skills in the user's own repository.
- **How.** Refresh `<workspace>/under-test/<skill-name>/` and copy each case's `files` into its inputs folder (see [Isolating eval runs](#isolating-eval-runs)). Dispatch one fresh subagent per case, all in the same turn, with the with-skill prompt from [Running with the skill](#running-with-the-skill), the output folder `<workspace>/regression-<N>/eval-<id>/run-1/`, and "Do not use the Skill tool." after its first line.
- **Grading.** Record each expectation as pass or fail with its evidence in `<workspace>/grading/regression-<N>.md`. Re-run each failing case once, in a new subagent, into `run-2/`. Only a case that fails both runs counts.
- **A case that fails twice** blocks finishing. Change the skill until the case passes; when the expectation itself is wrong, fix the eval and say why in the report. Then run the regression again.
- **Without subagents** (claude.ai chat): run each case yourself, one at a time, and ask the user to review the outputs.

## Checking trigger queries

Skip this check for a user-only skill (`disable-model-invocation: true`). Otherwise, as an approximation, dispatch one fresh subagent with this prompt:

```text
Here are the skills available to you (name: description):
<this skill's name and description>
<the names and descriptions of neighbouring skills it competes with>

For each request below, answer with the name of the skill you would load, or "none".
Do not carry out the requests.

1. <query>
2. <query>
```

Compare each answer with `should_trigger`, then revise the description:

- **A missed should-trigger query:** add the missing terms or phrasing to the "Use when..." clause.
- **A near-miss that triggered:** narrow the capability sentence, or name what the skill does not cover.

## What this approximation cannot measure

- **Real triggering.** The with-skill subagent is told where the skill is, so it tests the instructions, and the trigger check shows descriptions out of context. Neither exercises the real skill listing.
- **Listing pressure.** The approximation misses truncation at 1,536 characters, the listing budget, and the dropped descriptions of rarely used skills.
- **The user's own environment.** Other installed skills, CLAUDE.md files, and MCP tools all change what Claude picks.
- **Variance.** A single run can pass by luck, so run flaky cases 3 times.
- **Fork behaviour.** A subagent told to read a skill does not reproduce `context: fork` (no history, a background run).

## Upgrade paths

**`claude plugin eval`** runs eval suites for a plugin, with a with-plugin arm and a without-plugin arm.
- **Trigger grading.** A `tool_used: Skill` grader measures whether the skill was actually invoked.
- **Plugin needed.** It needs a `plugin.json` or a skills-directory plugin. A skill in a plugin repository (`.claude-plugin/plugin.json` at its root, as in Repertoire) already qualifies, and a checkout linked into `~/.claude/skills/` loads as the skills-directory plugin `<plugin-name>@skills-dir`. Wrap a standalone skill from `.claude/skills/` or `~/.claude/skills/` in a plugin first.
- **Case layout.** Each case is a directory, `evals/<case>/prompt.md`, with grader files under `graders/*.md`. The tool does not read `evals.json`.
  - Translate each eval case into a case directory, and each expectation into a grader.
  - Add a `tool_used: Skill` grader for the trigger check.
  - Check the layout against the plugin docs before relying on it.
- **Version.** It needs a recent Claude Code; run `claude plugin eval --help` to check.
- **Native Windows.** Suites that grant Bash need WSL2.

**Anthropic's skill-creator** reads the same `evals.json` and trigger query formats.
- **Description optimizer.** It runs each trigger query several times through `claude -p`, splits the queries into train and test sets, and proposes better descriptions. Run it on the user's own machine; it does not run in Cowork.
- **Native Windows.** Its trigger loop does not work there, because it waits on a pipe with `select()`; run it under WSL.
- **Validator.** It accepts only the portable fields, so for a skill with the default `claude-code` target (Claude Code and Cowork) its findings about fields such as `context` do not apply.
