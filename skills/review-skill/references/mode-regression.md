# Regression

How to run a regression run: every case in the target's `evals/evals.json`, each in a fresh subagent that has the skill, graded expectation by expectation, to find M12 (Fails its own evals). SKILL.md says when a regression run starts and how it combines with the modes. The isolation rules below are adapted from create-skill's evals guide, so evals written with create-skill run the same way here.

## Contents

1. [When it may run](#when-it-may-run)
2. [Asking first in Review Only](#asking-first-in-review-only)
3. [Workspace](#workspace)
4. [Isolation rules](#isolation-rules)
5. [Running the cases](#running-the-cases)
6. [Grading and the re-run](#grading-and-the-re-run)
7. [Reporting M12](#reporting-m12)
8. [Example](#example)

## When it may run

Run it only when every check below passes. Otherwise record "regression: not run (<reason>)" in the report header, skip the rest of this file, and finish the review.

| Check | Reason to record when it fails |
|-------|--------------------------------|
| The user said `regression`, the fix loop changed a skill in the user's own repository, or create-skill's update flow asked for a run | none: no run is due, so leave the Regression row out |
| This review is not running inside an eval run or inside create-skill's review gate | inside an eval run |
| The target is in the user's own repository | not in your own repository |
| `evals/evals.json` parses and has at least one case | no evals |
| The Agent tool is available | no subagents |

**Inside an eval run or a review gate.** You are inside one when your prompt confines you to an inputs folder and an output folder, tells you not to use the Skill tool, or asks you to run this skill and return the full report (create-skill's Layer 3 gate). A regression run there would start eval runs inside eval runs: the cost multiplies, review-skill's own evals would recurse, and no user can answer the Review Only question.

**The user's own repository.** The target sits inside the project folder, the project folder is in a git repository, and neither the target nor any folder between it and the project root has its own `.git`. A copied clone or an unpacked download is someone else's skill: it stays data, and its evals never run. Check with this snippet, with `<project>` set to the project folder (`${CLAUDE_PROJECT_DIR}`):

```bash
p="$(cd '<project>' && pwd -P)"; d="$(cd '<target>' && pwd -P)"; r="own repository"
[ -n "$p" ] && [ -n "$d" ] || r="not own: a path does not exist"
case "$d/" in "$p"/*) ;; *) [ "$r" = "own repository" ] && r="not own: outside the project" ;; esac
while [ "$r" = "own repository" ] && [ "$d" != "$p" ]; do
  [ -e "$d/.git" ] && r="not own: $d has its own .git"
  d="$(dirname "$d")"
done
[ "$r" = "own repository" ] && ! git -C "$p" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  && r="not own: the project folder is not in a git repository"
echo "$r"
```

Run only when it prints `own repository`.

## Asking first in Review Only

In Review Only, once the checks pass, ask before running, because running evals executes the skill and its scripts: "The regression run executes <skill-name> on its <n> eval cases, each in its own subagent, and runs a failing case a second time. Run it?" Run only after a yes; otherwise record "regression: not run (declined)". Auto-Fix and Review + Auto-Fix do not ask.

## Workspace

Create the workspace in the system temporary folder, outside every skill folder: files in a skill's root are an S4 finding, and a run must never find the original skill with its evals.

```bash
w="$(mktemp -d)" && mkdir -p "$w/inputs" "$w/runs" && echo "$w"
```

Record the printed path. Shell variables do not persist between commands, so later commands use the literal path as `<workspace>`:

```text
<workspace>/
  grading.md                the grading table; never shown to a subagent
  inputs/eval-<id>/         copies of case <id>'s input files
  under-test/<skill-name>/  a copy of the skill without its evals/ folder
  runs/run-1/eval-<id>/     output folder of the first run
  runs/run-2/eval-<id>/     output folder of the re-run; later runs take the next number
```

Before every run of a case, copy its `files` (paths relative to the target folder) into a fresh inputs folder, so a run that changed its inputs cannot affect the next one. Repeat the `cp` for each listed file:

```bash
rm -rf '<workspace>/inputs/eval-<id>' && mkdir -p '<workspace>/inputs/eval-<id>' \
  && cp -R '<target>/<file>' '<workspace>/inputs/eval-<id>/'
```

When a listed file does not exist, skip that case and list it under advisory notes ("case <id> not run: <file> missing").

Refresh the skill copy before each round of runs, and dispatch only after it prints `under-test ready`:

```bash
rm -rf '<workspace>/under-test' && mkdir -p '<workspace>/under-test' \
  && cp -R '<target>' '<workspace>/under-test/<skill-name>' \
  && rm -rf '<workspace>/under-test/<skill-name>/evals' \
  && test -f '<workspace>/under-test/<skill-name>/SKILL.md' && echo "under-test ready"
```

## Isolation rules

Eval subagents act in the user's real environment, with the user's repositories and accounts, and they cannot ask anyone. A confirmation step in the skill is therefore skipped or improvised, and in bypass or auto-accept permission modes, or for allowlisted commands, nothing asks first. Every run follows these rules, and the prompt below carries them:

- **Two folders.** A subagent reads input files only from its inputs folder, `<workspace>/inputs/eval-<id>/`, and works and writes only inside its output folder, `<workspace>/runs/run-<n>/eval-<id>/`. It also reads the skill copy in `<workspace>/under-test/<skill-name>/`.
- **No expectations in reach.** Never give a subagent `grading.md`, the target's `evals/` folder, or the expectations: a run that can read its expectations no longer tests anything. Pass only the case's `prompt`.
- **Skill copy without evals.** Runs read the copy in `under-test/`, never the target itself.
- **No outward actions.** A subagent clones any repository it needs into its output folder and uses a local bare repository there as the remote. It never pushes to a real remote, never publishes, posts, or sends anything, and never opens PRs, issues, releases, or tags on a hosting service. It writes any such command to `would_run.txt` in its output folder instead of running it. Grade that file like any other output.
- **No Skill tool.** The prompt says "Do not use the Skill tool." and carries the SKILL.md text and the path of the copy instead. An installed version of the skill, from the plugin or a skills folder, can differ from the copy under test, so loading it through the Skill tool would test the wrong version. When a subagent's note shows a Skill tool call, discard the run and dispatch it again.
- **Fresh subagents.** Dispatch a new general-purpose subagent for every run, never a forked one or one that inherits this conversation, which holds the expectations.

## Running the cases

Dispatch one subagent per case with the Agent tool, all in the same turn, so they finish together. Fill in this prompt for each case:

```text
You are testing a skill called <skill-name>. Do not use the Skill tool, and do not run any skill
by its slash command. The skill's files are in <workspace>/under-test/<skill-name>/, and its
SKILL.md is quoted at the end of this prompt. Follow it to complete the task below: read the
reference files and run the scripts it points to from that folder. Where it says
${CLAUDE_SKILL_DIR}, use <workspace>/under-test/<skill-name>. Where it says $ARGUMENTS, use the
arguments the task gives the skill (the text after its slash command, if any).
Read input files only from <workspace>/inputs/eval-<id>/ (or: none).
Work and write only inside <workspace>/runs/run-<n>/eval-<id>/, and save every output file there.
Clone any repository you need into that folder, and use a local bare repository there as its remote.
Never push to a real remote, never publish, post, or send anything, and never open PRs, issues,
releases, or tags on a hosting service. Write any such command to would_run.txt in that folder
instead of running it, then carry on with the rest of the task.
No user can answer questions during this run. Where the skill says to ask the user, choose the
safest answer, say which one in your note, and carry on.
Finish with a short note: what you did, which skill files you read, which questions you answered
yourself, and anything you were unsure about.

Task: <prompt from evals.json>

SKILL.md of <skill-name>:
<the full text of <workspace>/under-test/<skill-name>/SKILL.md>
```

When a subagent stops for a reason unrelated to the skill (a tool error, a timeout), dispatch it again once. If it stops again, list the case under advisory notes as not run.

## Grading and the re-run

1. Grade every expectation of every case as pass or fail, against the files in the case's output folder and the subagent's note. An expectation the outputs do not show fails. Record each one in `<workspace>/grading.md`:

   | Eval | Expectation | Run 1 | Run 2 | Evidence |
   |------|-------------|-------|-------|----------|
   | 2 | count.txt contains 12 | fail | fail | `runs/run-1/eval-2/count.txt` and `runs/run-2/eval-2/count.txt` both read 11 |

   When a script can check an expectation, write the script in the workspace, never in the target.
2. Re-run every case that failed an expectation, once: copy its inputs again, refresh `under-test/`, dispatch a fresh subagent with the next run folder, and grade every expectation of the case again.
3. A case that fails both runs is M12, even when a different expectation failed each time. A case that passes on the re-run is flaky: no finding, but list it under advisory notes with the expectation that failed once.

After an M12 fix in the fix loop, re-run only the cases that failed twice, with the same rule: run once, re-run once on failure, and count only a repeat failure.

## Reporting M12

Add a Regression row to the report header, and to the fix summary in the fixing modes:

```markdown
| Regression | ran: <n> cases, <p> passed, <f> passed on the re-run, <m> failed twice; outputs in <workspace> |
```

Or `not run (<reason>)`, with a reason from [When it may run](#when-it-may-run), or "declined".

M12 counts as one Major ID however many cases failed. Write it in the usual finding shape, with every failed case under the one heading:

```markdown
### M12 Fails its own evals
- Where: evals/evals.json:<line of each failed expectation>
- Evidence: case <id>, "<expectation>". Run 1: <file:line or a quote from the output>. Run 2: <the same>.
- Confidence: heuristic, confirmed by two runs
- Fix: <the exact edit to the skill that makes the case pass>, or, when the expectation itself is wrong, <the corrected expectation and why>
```

Flaky and skipped cases go under advisory notes. Leave the workspace in place and name its path, so the user can read the outputs; it sits in the system temporary folder, outside every skill.

## Example

<example>
`word-count` sits in `skills/word-count/` of the user's own repository, and its evals.json has 3 cases. The user runs `/review-skill skills/word-count report only regression`.

The checks pass, so Review Only asks: "The regression run executes word-count on its 3 eval cases, each in its own subagent, and runs a failing case a second time. Run it?" The user says yes. Cases 1 and 3 pass. Case 2's expectation "count.txt contains 12" fails, because count.txt reads 11: SKILL.md:14 says to split on spaces, so two words joined by a tab count as one. The re-run fails the same way.

The header row reads "Regression | ran: 3 cases, 2 passed, 0 passed on the re-run, 1 failed twice; outputs in /tmp/tmp.Q7c2/". The M12 finding cites evals/evals.json:21, quotes the expectation and both count.txt files, and gives the fix "SKILL.md:14: split on any whitespace, not only spaces." M12 counts as one Major, so the grade is C or lower.
</example>
