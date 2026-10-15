# Worked Examples

Three end-to-end runs of the create-skill workflow, step by step. SKILL.md has short versions; this file shows how the steps fit together. Paths such as `brand-guidelines/references/colors.md` belong to the example skill, not to create-skill.

## Contents

1. [brand-guidelines: an inline guideline skill](#1-brand-guidelines-an-inline-guideline-skill)
2. [csv-report: a forked task skill](#2-csv-report-a-forked-task-skill)
3. [changelog: updating a skill after a failure](#3-changelog-updating-a-skill-after-a-failure)

## 1. brand-guidelines: an inline guideline skill

**Request:** `/create-skill brand-guidelines Apply our brand colours, typography, and logo rules to anything user-facing`

**Step 1, intent.**
- The name and purpose come from the input.
- One question remains: where the brand files are, and whether the skill is personal or for the project. The user answers "the design-system repo, for the whole team".
- Location: `.claude/skills/brand-guidelines/` in that repository, which has no `.claude-plugin/`. Target: `claude-code`. The team works in Claude Code, so a project skill is enough; to reach Cowork too, it would go into a plugin repository instead (`distribution.md`).

**Step 2, evals and baseline.**
- Workspace: `brand-guidelines-workspace/` in the scratchpad.
- Eval cases:
  1. "make a hero section for the spring sale landing page";
  2. "turn these release notes into a title slide";
  3. "marketing wants a dark-mode banner for the newsletter".
- Expectations include "uses only palette colours", "sets headlines in the display typeface", and "uses the dark-mode palette on dark backgrounds".
- Trigger queries:
  - should trigger: "can you make this email template look on-brand?" and "restyle the pricing page, it looks off compared to the rest of the site";
  - near-misses: "pick a colour scheme for my personal blog", "explain complementary colours", "write our company mission statement".
- Baseline: three subagents in one turn. All three pick generic blues and system fonts, and none knows that the dark-mode variants exist.

**Step 3, plan.**
- Freedom: high, because design judgment is open-ended, with fixed facts for the palette and type scale.
- Resources:
  - `brand-guidelines/references/colors.md` (palette, contrast pairs, dark-mode variants);
  - `brand-guidelines/references/typography.md`;
  - `brand-guidelines/assets/logo.svg`, which the user provides.
  - No scripts.
- Fork decision test: it fails condition 1, because a guideline skill has no task to return, and condition 2, because it applies to whatever the conversation is building. The skill runs inline.
- Frontmatter: `name`, `description`, `license`.
- The user approves the plan.

**Step 4, init.**
```bash
python ${CLAUDE_SKILL_DIR}/scripts/init_skill.py brand-guidelines --path .claude/skills --resources references,assets
```
Then copy the workspace evals over the skeletons.

**Step 5, write.**
- Description: "Applies the company's brand colours, typography, and logo rules to UI, documents, and slides. Use whenever the user creates or restyles anything user-facing (pages, emails, decks, banners), even without mentioning the brand."
- Body: a short `<instructions>` block (identify the output type; read `colors.md` before any colour choice; read `typography.md` before setting text) and three `<example>` blocks.
- Replace the TODO placeholders, and ask the user for the logo.

**Step 6, validate.**
- Pass 1:
  - quick_validate exits 0 with `style=0`. The Cowork check finds nothing: no scripts, no injection, and the outputs are files.
  - The with-skill runs meet 8 of 9 expectations. The dark-mode case uses the light palette, because `colors.md` lists the dark variants at the end and SKILL.md never points to them.
  - Fix: one line in SKILL.md, "On dark backgrounds, use the dark-mode table in `colors.md`."
- Pass 2: all expectations pass, and the review-skill subagent reports Grade A with zero Style notes.

**Steps 7 to 9.**
- Sanitization: the user declines, because the skill is internal.
- The security scan is clean.
- The skill is used in place: no package, and the repository has no marketplace file.

**Step 10, iterate.** A week of real use shows Claude B rereading `typography.md` for heading sizes in every session. The 4-line size table moves into SKILL.md.

## 2. csv-report: a forked task skill

**Request:** `/create-skill csv-report Summarise a CSV file into a Markdown table of row counts, column types, and empty cells`

**Step 1, intent.** Everything except the location comes from the input. The default applies: `.claude/skills/csv-report/` in the current project.

**Step 2, evals and baseline.**
- Eval cases:
  1. a clean comma-separated file;
  2. a semicolon-delimited file with a UTF-8 byte-order mark;
  3. a path that does not exist.
- Baseline:
  - All three runs write similar parsing code from scratch.
  - Two runs read the semicolon file as a single column.
  - The missing-file run asks the user for another path.

**Step 3, plan.**
- Freedom: low. A bundled script, `csv-report/scripts/summarise.py`, uses the standard library's `csv.Sniffer` and needs no third-party packages.
- Fork decision test:
  1. an explicit task with a returnable table: yes;
  2. needs nothing beyond the path argument: yes;
  3. never asks: yes (a missing argument prints usage and stops, and a missing file is reported as an error);
  4. no Workflow: yes;
  5. can finish in the background: yes.

  So the skill forks. The user wants the table in the same turn, so add `background: false`.

**Step 4, init.**
```bash
python ${CLAUDE_SKILL_DIR}/scripts/init_skill.py csv-report --path .claude/skills --fork --resources scripts
```

**Step 5, write.**
- Frontmatter and body: see the "Forked task skill" example in `frontmatter_reference.md`. Because SKILL.md uses the argument placeholder as intended, it carries no teaching examples of substitution.
- Script:
  - argparse;
  - a documented `SNIFF_BYTES = 64 * 1024` constant (enough rows for the sniffer to tell delimiters apart);
  - `encoding="utf-8-sig"` for byte-order marks;
  - specific exceptions;
  - exit 2 for usage errors and 1 for unreadable files.
- SKILL.md states that the script needs only the Python standard library.

**Step 6, validate.**
- Pass 1:
  - quick_validate exits 0, but `RESULT` shows `style=1`: an `[S2]` line reports only 2 `<example>` blocks. Exit 0 is not enough, so add a third example for the missing-file case and re-run until `RESULT` shows `style=0`.
  - The Cowork check passes: SKILL.md runs the script through `${CLAUDE_SKILL_DIR}/scripts/summarise.py`, and the script prints the table instead of opening anything.
  - The with-skill runs pass every expectation.
  - The review-skill subagent reports Grade A with zero Style notes.
- Pass 2: quick_validate exits 0 with `style=0`, and the review-skill subagent again reports Grade A with zero Style notes.

**Steps 7 to 9.** No sanitization (built from scratch). The scan is clean. The skill is used in place.

**Step 10, iterate.** A Haiku run on a file with Windows line endings miscounts the rows. A fourth eval case covers that input. Its baseline runs while `.claude/skills/csv-report/` is installed, so its prompt adds "Do not use the Skill tool.", and its transcript shows no Skill call. The fix opens files with `newline=""`, and step 6 passes again within this round.

## 3. changelog: updating a skill after a failure

**Request:** "The changelog skill said 'No release needed' on our repo, but we merged four PRs since the last tag. Fix it."

**Step 1, intent.**
- This is an update, so first find the source copy. The invoked copy sits under `~/.claude/plugins/cache/`, so locate the source repository (`skills/changelog/` in the kit) and edit there.
- Read `changelog/SKILL.md` and `changelog/references/changelog_format.md` in full.
- Snapshot the skill to `changelog-workspace/skill-snapshot/`.
- Root cause: the PR titles live only in merge commits. The subject is "Merge pull request #41 from org/feat-export", the body is "feat: add CSV export", and the skill drops every merge commit.

**Step 2, evals and baseline.**
- The skill has no `evals/` yet, so write three eval cases:
  1. the reported failure (a history with conventional-commit titles only in merge-commit bodies);
  2. a linear history with one `feat:` commit (expects a minor release);
  3. a docs-only history (expects "No release needed").
- Each case's input is a git bundle of a small fixture history in `changelog/evals/files/`, because the skill creates tagged releases. The subagents clone it into their output folders with a local bare remote, so a tag push only reaches that local remote, and any `gh release` or other hosting-service command lands in `would_run.txt` instead of a real repository.
- Add 10 trigger queries.
- Run the baseline against the snapshot: case 1 fails, and cases 2 and 3 pass.

**Step 3, plan.**
- One rule changes: a merge commit whose body opens with a conventional-commit subject counts as that commit, and other merge commits are still dropped.
- The frontmatter and the rest of the workflow stay as they are; findings that predate the change go to the user as a separate list, not into this fix.

**Step 4.** Skipped, because the skill exists.

**Step 5, write.**
- Grep the skill for every statement of the merge-commit rule. It appears twice in SKILL.md (the filter step and the "Always filter" line), and not in `changelog_format.md`.
- Update each copy, so that no two places disagree (M5).
- Copy the new evals into `changelog/evals/`.

**Step 6, validate.**
- quick_validate exits 4 with the pre-existing `[m9]` line on `changelog/references/changelog_format.md` (356 lines, no Contents heading). The change did not cause it, so list it under findings that predate the change instead of fixing it.
- With the skill, case 1 now produces a minor release that lists "Add CSV export", and cases 2 and 3 still pass.
- Run the review-skill gate and fix what it reports about the changed lines, within 3 passes.
- Report findings about untouched parts of the skill to the user instead of fixing them silently.
- Regression: once a pass is clean, invoke `repertoire:review-skill` (or `review-skill`) from the main conversation with the absolute path of `skills/changelog` and `report only regression`. It asks the user, who says yes, then re-runs all three cases from `changelog/evals/evals.json`; each passes on the first run, so nothing blocks finishing.

**Steps 7 to 9.**
- No sanitization is needed.
- The scan is clean. No zip: the skill ships through the plugin.
- Marketplace: the kit has `.claude-plugin/marketplace.json`, and its entries carry no `version`, so `marketplace_update.md` says to add none. Run `claude plugin validate .`, check the diff, and tell the user to push: Claude Code users get the fix with `/plugin marketplace update`, and Cowork picks up the pushed commit.

**Step 10, iterate.** Run the new case on Haiku as well. It passes, so the fix is done. Report the before and after results per eval case to the user.
