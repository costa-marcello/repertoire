# Auto-PR

Commands and details for the Auto-PR mode in SKILL.md: contribute fixes to someone else's skill through a pull request. SKILL.md gives the steps; this file has the two confirmations, the exact commands, the change limits, the respect check, deferral examples, and tone. The URL check, the read-only review clone, and the cleanup command are in `mode-external-review.md`.

## Contents

1. [The two confirmations](#the-two-confirmations)
2. [Commands](#commands)
3. [What the PR may change](#what-the-pr-may-change)
4. [Deferred suggestions](#deferred-suggestions)
5. [Respect check](#respect-check)
6. [Tone](#tone)

## The two confirmations

Auto-PR acts on the user's GitHub account, so it stops twice for an explicit yes:

1. **Before `gh repo fork`**, and only after the read-only review found at least one fix the PR may make. Say which repository will be forked and that the fork appears under the user's account. A review with nothing to fix ends with the report, and no fork is created.
2. **Before pushing and `gh pr create`.** Show the PR title, the full body, and the staged summary from `git -C '<path>' diff --cached --stat`, and offer the full diff (`git -C '<path>' diff --cached`). Pushing to the fork publishes the branch, so the push waits for the same yes.

A vague reply ("sounds good, but...") is not a yes; ask again. If the user declines the PR, delete the title and body files and the clone, tell them the fork stays on their account, and stop.

## Commands

Run the snippets with the Bash tool (Git Bash on Windows), in order, keeping each placeholder inside its single quotes:

- `<path>` is the clone path that step 1 prints.
- `<ref>` is the branch the URL names, or the read-only clone's branch when it names none.
- `<branch>` is `review-skill/<skill-name>-<yyyymmdd>`, for example `review-skill/csv-report-20261014`.

`GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never` makes git fail instead of waiting for credentials.

1. **Fork, clone, and fetch upstream** in a fresh temporary folder. `gh repo fork --clone` makes the fork `origin` and the original repository `upstream`, and reuses a fork the user already has, which may be out of date; the fetch brings in the current upstream branches.
   ```bash
   t="$(mktemp -d)" && echo "$t" && cd "$t" && gh repo fork '<owner>/<repo>' --clone && cd '<repo>' && GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git fetch upstream && pwd -P
   ```
   Record both printed paths: the first is the temporary folder, the last is the clone. If `cd '<repo>'` fails, the user's fork has another name: list the temporary folder (the first path) and use the folder gh created.
2. **Pick an unused branch name.** Exit 2 from `ls-remote` means the name is free. Exit 0 means the fork already has it: add `-2` (then `-3`) and check again.
   ```bash
   git check-ref-format --branch '<branch>' && GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git -C '<path>' ls-remote --exit-code --heads origin '<branch>'
   ```
3. **Branch from upstream**, not from the fork's copy:
   ```bash
   git -C '<path>' checkout -b '<branch>' 'upstream/<ref>' && git -C '<path>' rev-parse HEAD
   ```
   When the printed commit differs from the one the read-only review graded, upstream has moved: run the review procedure again in this clone before fixing. The PR body names this commit.
4. **Fix, then run the respect check** (below). Write the commit title as one line to `<title-file>` and the PR body to `<body-file>`, both in the temporary folder that holds the clone, so neither shows up in the diff.
5. **After the user's yes, commit and push.** Never force-push (no `--force` or `--force-with-lease`), because the branch may already back an open PR.
   ```bash
   git -C '<path>' commit -F '<title-file>' && GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git -C '<path>' push -u origin '<branch>'
   ```
   If the push is rejected, keep the clone, stop, and ask the user how to proceed. If it fails because git has no credentials for github.com, ask the user to run `gh auth setup-git`, then push again.
6. **Open the PR and check its files.** `<fork-owner>` is the user's login (`gh api user --jq .login`).
   ```bash
   cd '<path>' && gh pr create --repo '<owner>/<repo>' --base '<ref>' --head '<fork-owner>:<branch>' --title "$(head -n 1 '<title-file>')" --body-file '<body-file>'
   gh pr view '<pr-url>' --json files --jq '.files[].path'
   ```
   The second command must list the same paths as the respect check. Report the PR URL.
7. **Clean up** after the PR is verified or declined:
   ```bash
   rm -f '<title-file>' '<body-file>'
   ```
   Then run the cleanup command in `mode-external-review.md` with `<path>` as the recorded path.

The title comes from a file because the skill name in it comes from the target; `git commit -F` and `$(head -n 1 ...)` pass it as data, never as shell code.

## What the PR may change

Edits to existing files and new files only. The diff must contain no deletes, renames, or moves, because those break the author's links, history, and installs in ways a review cannot see.

| Allowed | Not allowed (defer instead) |
|---------|-----------------------------|
| Rewriting the description (M8) | Deleting template leftovers such as an unused placeholder file (M9) |
| Removing `context: fork` from the frontmatter (M2) | Renaming reference files to one separator (S7) |
| Moving a long section of SKILL.md into a new reference file (M1): an edit plus an add | Moving loose root files into `references/` (S4) |
| Adding a `## Contents` list (m9) | Merging two reference files, which deletes one |
| Replacing weak-verb directives (M7) | Any Style fix, even when it is an edit |
| Editing `name` to match the folder (M9) | Renaming the folder to match `name` |

Keep the author's language: if SKILL.md is in Chinese, write the fixes in Chinese, and add an English README as a new file rather than translating the original.

## Deferred suggestions

Every fix the limits rule out goes into the PR body under "Deferred suggestions", with its rule ID and the exact change, so the author can apply it in one step:

```markdown
## Deferred suggestions

These need deletes, renames, or moves, which this PR avoids:

- M9: delete the placeholder script that the skill template created; nothing references it.
- S7: rename `api_notes.md` to `api-notes.md` in the references folder, so all reference files use hyphens.
- S4: move `tips.md` from the skill root into the references folder and link it from SKILL.md.
```

When a deferred Major fix leaves a Major finding open, the PR body says so and gives the grade the skill would reach after the deferred fixes.

## Respect check

Run before writing the PR body, and again after any later edit:

```bash
git -C '<path>' add -A && git -C '<path>' diff --cached --name-status
```

Every line must start with `M` (modified) or `A` (added). For a `D` or `R` line, restore the original path with `git -C '<path>' restore --source=HEAD --staged --worktree -- '<original-path>'`, remove any copy a rename left behind, and move the fix to "Deferred suggestions". The title and body files live outside the clone, so they never show up in this diff.

Then confirm by reading the diff:

```text
Respect check:
- [ ] Only M and A entries in the diff
- [ ] No Style fixes
- [ ] The original language is kept
- [ ] Every feature and mode of the original still works the same way
- [ ] The author's design choices (structure, naming, tone) are kept where no rule requires a change
- [ ] Each change maps to a rule ID listed in the PR body
```

## Tone

Frame changes as improvements for users, not corrections of the author.

| Instead of | Write |
|------------|-------|
| "Your skill doesn't follow best practices" | "This PR aligns the skill with Anthropic's skill guidance for better triggering" |
| "Fixed the incorrect description" | "Added trigger conditions to the description" |
| "Removed the non-standard metadata file" | (not allowed: list it under Deferred suggestions) |
| "Rewrote the README in English" | "Added README.en.md; the original README is unchanged" |

Thank the author for the parts that work well, and keep the PR to the changes the review found.
