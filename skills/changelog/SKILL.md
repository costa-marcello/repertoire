---
name: changelog
description: "Generates the CHANGELOG.md section for the next version from the commits since the last tag and creates the tagged release: writes CHANGELOG.md, commits, tags, and pushes. Use when the user asks to cut, tag, or ship a release, or to release the changes since the last tag. Not for previewing the next version, editing version files such as package.json, or adding Unreleased entries without a release."
license: MIT
context: fork
background: false
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(git *), Bash(GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git *)
argument-hint: "[version] [repo-folder]"
---

# Changelog

Each run that passes its checks creates one versioned release: it gathers the commits since the last tag, writes a dated release section in CHANGELOG.md, commits, tags, and pushes. The section follows Keep a Changelog, and commits are read as Conventional Commits. The plugin runs the skill as `/repertoire:changelog`; a single-skill install runs it as `/changelog`.

The skill runs forked, without the conversation, and invoking it is the go-ahead for the commit, tag, and push. When a check fails it stops and reports why. When the push cannot happen (Cowork often has no git credentials), the release stays committed and tagged locally and the report ends with the commands for the user to run.

Arguments (empty when none were given): `$ARGUMENTS`. They may hold a version such as `v1.4.0` and a path to the repository folder.

<instructions>

## Step 1: Pre-Flight Checks

Run git through the Bash tool. The repository is the folder named in the arguments, else the current directory. When a folder was given, put `-C <folder>` right after `git` in every command below and edit `<folder>/CHANGELOG.md`, because the shell does not keep a `cd` between commands. Put `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never` in front of every command that contacts the remote, so a missing credential fails at once instead of opening a sign-in prompt that nobody can answer.

1. `git status --porcelain` must return empty (CHANGELOG.md exempt). If dirty, stop and tell the user to commit or stash first.
2. `git branch --show-current` prints the release branch, `<branch>` below. If it prints nothing (detached HEAD), stop and tell the user to check out a branch first.
3. `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git fetch origin`. If it fails (no credentials, no network, or no `origin`), do not retry or work around it: no new remotes, tokens, or credential helpers. Note "remote not checked", skip check 4, and continue; Step 6 then hands the push to the user.
4. `git rev-parse --verify --quiet origin/<branch>` must print a hash. If it prints nothing, the branch is not on origin yet: stop and tell the user to push it first with `git push -u origin <branch>`. Then `git rev-list --count HEAD..origin/<branch>` must print 0; otherwise stop and tell the user to pull first.

## Step 2: Determine Version

Find the last tag, the nearest tag reachable from HEAD:

```bash
git describe --tags --abbrev=0
```

If it exits non-zero, there are no tags: the current version is `0.0.0`, and every `<last-tag>..HEAD` below becomes `HEAD` (the full history).

Scan the commits with `git log --pretty=format:"%h %s%n%b" <last-tag>..HEAD` and categorize each one with the [Commit Categorization](#commit-categorization) table. If there are no commits, or the table drops all of them, report "No release needed" with the commit counts and stop.

If the arguments hold a version, use it without its leading `v` and skip the bump table. Otherwise apply the highest-priority rule that matches an included commit:

| Priority | Signal | Bump |
|----------|--------|------|
| 1 | Breaking change: `!` after the type (`feat!:`, `fix(api)!:`) or a `BREAKING CHANGE:` footer | Major; Minor while the major version is 0 (1.0.0 only when passed as the version) |
| 2 | An included commit that goes under Added | Minor |
| 3 | Any other included commit | Patch |

Report the version before continuing:

```
Next version: X.Y.Z (bump — reason)
Commits since <last-tag>: N total (N included, N dropped)
```

## Step 3: Check the Tag

The new tag follows the last tag's style: `vX.Y.Z`, or `X.Y.Z` when the last tag has no `v`. With no tags, use `vX.Y.Z`. Below, `vX.Y.Z` stands for that tag name.

Run `git tag -l vX.Y.Z`. If the tag already exists, or X.Y.Z is not higher than the last tag's version, stop and report the conflict.

## Step 4: Draft the Bullets

Read `${CLAUDE_SKILL_DIR}/references/changelog_format.md` before writing the first bullet. It holds the six sections and their order, the breaking-change bullet, the writing style, and a complete example.

Using the categories from Step 2, write one user-facing bullet per change in the section the table gives it. Commits that make one change share a bullet.

## Step 5: Update CHANGELOG.md

1. If no CHANGELOG.md exists, create it with the header from [Output Format](#output-format).
2. If CHANGELOG.md exists, read it and preserve all existing content.
3. Add `## [X.Y.Z] - YYYY-MM-DD` with today's date above the existing version sections, holding the Step 4 bullets.
4. If an `## [Unreleased]` section exists, move its entries into the new section (keep every entry; merge one that repeats a commit-derived entry), then delete the empty Unreleased heading and its footer link.
5. Add the new footer link above the older ones, copying the pattern of the existing links: `[X.Y.Z]: <base>/compare/<last-tag>...vX.Y.Z`, or `[X.Y.Z]: <base>/releases/tag/vX.Y.Z` for the first release. For a new file, `<base>` is `git remote get-url origin` as an https URL without `.git` (`git@github.com:owner/repo.git` becomes `https://github.com/owner/repo`). GitLab uses `<base>/-/compare/...` and `<base>/-/tags/vX.Y.Z`. Leave the links out when origin is missing or is not a GitHub or GitLab URL.
6. **Verify:** re-read the new section. Every included commit and every entry moved from Unreleased appears in at least one bullet, no bullet comes from a dropped commit, and the `[Unreleased]` heading and its footer link are gone.

## Step 6: Commit, Tag, Push

1. `git add CHANGELOG.md`
2. `git commit -m "Release vX.Y.Z"`
3. `git tag -a vX.Y.Z -m "Release vX.Y.Z - <one-line summary of changes>"`. Keep `-a`, because `git push --follow-tags` skips lightweight tags.
4. Push once: `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git push --follow-tags origin <branch>`. Naming the branch works even when it has no upstream set. Skip the push when the Step 1 fetch failed, because it would fail the same way.
5. **Verify:** `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git ls-remote --tags origin vX.Y.Z` prints the tag. Report the version, tag, and commit hash. If it prints nothing, the push did not land: handle it as a failed push below.

**When the push fails or was skipped** (common in Cowork, which may have no git credentials): do not retry, change the remote, or look for tokens. The commit and tag stay local. Quote git's error, report the version, tag, and commit hash, and end with the commands for the user to run from a terminal that can push:

```text
Release vX.Y.Z is committed and tagged locally but not pushed.
Run from the repository:
  git push --follow-tags origin <branch>
  git ls-remote --tags origin vX.Y.Z
```

If the Step 1 fetch failed, list `git fetch origin` and `git status -sb` before the push. If the branch turns out to be behind, the release has to be redone so its section covers the new commits: the user drops the local release with `git tag -d vX.Y.Z` and `git reset --hard HEAD~1` (the release commit holds only the CHANGELOG.md change), runs `git pull`, and runs the skill again.

**When `git commit` or `git tag` fails** (often no `user.name` or `user.email` in a fresh container, or a signing key that asks for a passphrase): do not change git config. Stop, quote the error, say which Step 6 commands already ran, and end with the remaining Step 6 commands for the user to run.

## Gotchas

- The `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never` prefix is POSIX shell syntax. Run git through the Bash tool (Git Bash on Windows); in PowerShell the prefix is a parse error. When only PowerShell is available, start the same call with `$env:GIT_TERMINAL_PROMPT='0'; $env:GCM_INTERACTIVE='never';` before the git command, because PowerShell keeps no variables between calls.
- `git describe` returns the nearest tag reachable from HEAD, so on a maintenance branch the range starts at that branch's last release, not at the highest tag in the repository.
- Squash merges often leave the pull request title as the commit subject, with no type prefix. Those commits take the "No recognized prefix" row; keep their `(#123)` references in the bullet.

---

## Commit Categorization

This table is the only rule for which commits go into the changelog and where. A scope counts as its type (`feat(api):` is `feat:`). Use the first row that matches each commit:

| Commit | Section | Include |
|--------|---------|---------|
| Breaking: any type with `!` (`feat!:`, `fix(api)!:`) or a `BREAKING CHANGE:` footer | The section that fits the change, as a `**BREAKING**:` bullet listed first | Always, even for a type dropped in the next row |
| Merge commits; `docs:`, `style:`, `test:`, `build:`, `ci:`, `chore:` | None | Never |
| `security:`, or a `fix:` that closes a vulnerability | Security | Always |
| `feat:` | Added | Always |
| `fix:` | Fixed | Always |
| `perf:` | Changed | Only when the message names an effect users notice (faster startup, lower memory); otherwise drop |
| `refactor:` | Changed | Only when `git show --stat <sha>` shows it touches a public API, CLI flag, configuration schema, or user-facing output; otherwise drop |
| `revert:` or `Revert "..."` | Removed (a released feature) or Fixed (a released change that broke something) | Always, except when the commit it reverts is also since the last tag: then drop both |
| No recognized prefix | Read the message and `git show --stat <sha>`: Added, Fixed, or Changed | Always, unless it reads as a type dropped in the second row |

Translate technical commits to user-friendly language:
- `fix(auth): resolve JWT expiry edge case` -> "Fixed session timeout issues for long-running sessions"
- `feat(api): add /users endpoint` -> "Added user management API endpoints"

</instructions>

<formatting>

## Output Format

A new CHANGELOG.md starts with this header. Each release goes above the older ones, and the footer links run newest first:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-13

### Added
- New feature description

### Changed
- Modified behavior description

### Fixed
- Bug fix description

## [1.0.0] - 2026-02-01

### Added
- Initial release features

[1.1.0]: https://github.com/owner/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/owner/repo/releases/tag/v1.0.0
```

</formatting>

## Examples

<example>
**User request**: `/repertoire:changelog` (no arguments, no tags, no CHANGELOG.md)
**Action**: Scan the full history. Create CHANGELOG.md. Commit, tag, push.
**Steps**:
1. Auto-detect: v0.1.0 (minor — first release, feature commits found)
2. Create CHANGELOG.md with `## [0.1.0] - 2026-02-13` and the footer link `[0.1.0]: https://github.com/owner/repo/releases/tag/v0.1.0`
3. `git add CHANGELOG.md`
4. `git commit -m "Release v0.1.0"`
5. `git tag -a v0.1.0 -m "Release v0.1.0 - Initial release"`
6. `git push --follow-tags origin main` (Step 6)
**Output**: Released v0.1.0, tagged, and pushed.
</example>

<example>
**User request**: `/repertoire:changelog` (existing CHANGELOG.md, new commits since v1.2.0)
**Action**: Auto-detect version. Write the versioned section. Commit, tag, push.
**Steps**:
1. Auto-detect: v1.3.0 (minor — new feature commits detected)
2. Write the `## [1.3.0] - 2026-02-13` section to CHANGELOG.md
3. `git add CHANGELOG.md`
4. `git commit -m "Release v1.3.0"`
5. `git tag -a v1.3.0 -m "Release v1.3.0 - Dark mode and CSV export"`
6. `git push --follow-tags origin main` (Step 6)
**Output**: Released v1.3.0, tagged, and pushed.
</example>

<example>
**User request**: `/repertoire:changelog v2.0.0` (explicit version)
**Action**: Use provided version. Write the versioned section. Commit, tag, push.
**Steps**:
1. Version: v2.0.0 (explicit, skip the bump table)
2. Write the `## [2.0.0] - 2026-02-13` section
3. `git add CHANGELOG.md`
4. `git commit -m "Release v2.0.0"`
5. `git tag -a v2.0.0 -m "Release v2.0.0 - Complete API redesign"`
6. `git push --follow-tags origin main` (Step 6)
**Output**: Released v2.0.0, tagged, and pushed.
</example>

<example>
**User request**: `/repertoire:changelog` (only docs, test, and CI commits since v1.3.0)
**Action**: The table drops every commit. No release needed.
**Output**: No release needed. All 3 commits since v1.3.0 are docs, test, or CI changes.
</example>

<example>
**User request**: `/repertoire:changelog` in Cowork, where git has no credentials for the remote
**Action**: The Step 1 fetch fails ("could not read Username"). Note "remote not checked", write the section, commit, and tag; skip the push.
**Output**: Released v1.4.0 locally (commit a1b2c3d, tag v1.4.0), not pushed: `fatal: could not read Username for 'https://github.com': terminal prompts disabled`. Run from the repository: `git fetch origin`, `git status -sb`, `git push --follow-tags origin main`, then `git ls-remote --tags origin v1.4.0`.
</example>

## References

| File | Content |
|------|---------|
| `references/changelog_format.md` | Keep a Changelog sections, the breaking-change bullet, writing style, anti-patterns, and a complete example. Read it in Step 4. |
