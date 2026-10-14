---
name: changelog
description: "Generates a changelog entry from the commits since the last tag and creates the tagged release: writes CHANGELOG.md, commits, tags, and pushes. Use when the user asks to cut, prepare, or tag a release, bump the version, or release the changes since the last tag."
license: MIT
context: fork
background: false
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(git *), Bash(GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git *)
argument-hint: "[version]"
---

# Changelog

Every invocation creates a versioned release. Gathers commits since the last tag, writes a dated release entry in CHANGELOG.md, commits, tags, and pushes. Follows Keep a Changelog format and Conventional Commits conventions.

The skill runs forked, without the conversation, and invoking it is the go-ahead for the commit, tag, and push. When a check fails it stops and reports why. When the push cannot happen (Cowork often has no git credentials), the release stays committed and tagged locally and the report ends with the commands for the user to run.

<instructions>

## Step 1: Pre-Flight Checks

Put `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never` in front of every command that contacts the remote, so a missing credential fails at once instead of opening a sign-in prompt that nobody can answer.

1. `git status --porcelain` must return empty (CHANGELOG.md exempt). If dirty, stop and tell the user to commit or stash first.
2. `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git fetch origin`. If it fails (no credentials, no network, or no `origin`), do not retry or work around it: no new remotes, tokens, or credential helpers. Note "remote not checked", skip check 3, and continue; Step 6 then hands the push to the user.
3. Branch not behind remote: `git rev-list --count HEAD..origin/$(git branch --show-current)`. If behind, stop and tell the user to pull first.

## Step 2: Determine Version

If `$ARGUMENTS` contains a version (e.g., `v1.2.0`), use it directly.

Otherwise, auto-detect from commits since the last tag:

```bash
git tag --sort=-v:refname | head -1
```

If no tags exist, treat the current version as `0.0.0`.

Scan commits: `git log --pretty=format:"%s%n%b" <last-tag>..HEAD`. Apply the highest-priority rule:

| Priority | Signal | Bump |
|----------|--------|------|
| 1 | Breaking change — BREAKING CHANGE in body/footer, or type! suffix (feat!, fix!) | Major |
| 2 | New feature — feat or feat(scope) prefix | Minor |
| 3 | Bug fix or improvement — fix, perf, or other included types | Patch |

If all commits were filtered (docs, test, ci, chore only), report "No release needed" and stop.

Report the detected version before continuing:

```
Next version: X.Y.Z (bump — reason)
Commits since vCURRENT: N total (N included, N filtered)
```

## Step 3: Check No Duplicate Tag

`git tag -l vX.Y.Z`. If the tag already exists, abort and report the conflict.

## Step 4: Gather and Categorize Commits

1. Get all commits since the last tag: `git log --oneline <last-tag>..HEAD`
2. Categorize using the mapping below.
3. Filter noise: always drop merge commits, `ci:`, `chore:`, `test:`, `docs:`, and `style:` commits. For `refactor:` commits, include only when the diff touches a public API, CLI flag, configuration schema, or user-facing output; otherwise drop.
4. Translate technical commits to user-friendly descriptions.

## Step 5: Write Release Entry

1. If no CHANGELOG.md exists, create one with a header and footer links (detect remote URL with `git remote get-url origin`).
2. If CHANGELOG.md exists, read it and preserve all existing content.
3. Add a new versioned section `## [X.Y.Z] - YYYY-MM-DD` with today's date, placed above existing version sections.
4. If an `## [Unreleased]` section exists, move its entries into the new section (keep every entry; merge one that repeats a commit-derived entry), then delete the empty Unreleased heading and its footer link.
5. Update footer comparison links.
6. **Verify:** Entry count matches the categorized commit count (minus filtered) plus the entries moved from Unreleased.

## Step 6: Commit, Tag, Push

1. `git add CHANGELOG.md`
2. `git commit -m "Release vX.Y.Z"`
3. `git tag -a vX.Y.Z -m "Release vX.Y.Z - <one-line summary of changes>"`
4. Push once: `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git push --follow-tags`. Skip it when the Step 1 fetch failed, because the push would fail the same way.
5. **Verify:** `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git ls-remote --tags origin vX.Y.Z` prints the tag. Report the version, tag, and commit hash.

**When the push fails or was skipped** (common in Cowork, which may have no git credentials): do not retry, change the remote, or look for tokens. The commit and tag stay local. Quote git's error, report the version, tag, and commit hash, and end with the commands for the user to run from a terminal that can push:

```text
Release vX.Y.Z is committed and tagged locally but not pushed.
Run from the repository:
  git push --follow-tags
  git ls-remote --tags origin vX.Y.Z
```

If the Step 1 fetch failed, list `git fetch origin` and `git status -sb` before the push. If the branch turns out to be behind, the user runs `git tag -d vX.Y.Z`, `git pull --rebase`, and the tag command from item 3 again before pushing.

---

## Commit Categorization

Map Conventional Commits prefixes to Keep a Changelog sections. See `references/changelog_format.md` for the full mapping, writing style, and anti-patterns.

| Commit Prefix | Changelog Section |
|---------------|-------------------|
| `feat:` | Added |
| `fix:` | Fixed |
| `refactor:` (user-visible) | Changed |
| `security:` | Security |
| `docs:`, `test:`, `ci:`, `chore:` | Filter out |

**Always include:** features, user-facing bug fixes, breaking changes, security fixes.
**Always filter:** merge commits, internal refactors, test changes, CI config, typos.

Translate technical commits to user-friendly language:
- `fix(auth): resolve JWT expiry edge case` -> "Fixed session timeout issues for long-running sessions"
- `feat(api): add /users endpoint` -> "Added user management API endpoints"

## Git Analysis Commands

```bash
# All commits since last tag
git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || echo "")..HEAD

# Commits between tags
git log --oneline v1.0.0..v1.1.0

# Current tags
git tag --sort=-v:refname | head -10
```

</instructions>

<formatting>

## Output Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

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
**User request**: `/changelog` (no arguments, first time)
**Action**: No CHANGELOG.md. Create from full git history. Auto-detect version as v0.1.0.
**Steps**:
1. Auto-detect: v0.1.0 (minor — first release, feature commits found)
2. Generate CHANGELOG.md with `## [0.1.0] - 2026-02-13`
3. `git add CHANGELOG.md`
4. `git commit -m "Release v0.1.0"`
5. `git tag -a v0.1.0 -m "Release v0.1.0 - Initial release"`
6. Push with `--follow-tags` (Step 6)
**Output**: Released v0.1.0, tagged, and pushed.
</example>

<example>
**User request**: `/changelog` (existing CHANGELOG.md, new commits since last tag)
**Action**: Auto-detect version. Write versioned entry. Commit, tag, push.
**Steps**:
1. Auto-detect: v1.3.0 (minor — new feature commits detected)
2. Write `## [1.3.0] - 2026-02-13` entry to CHANGELOG.md
3. `git add CHANGELOG.md`
4. `git commit -m "Release v1.3.0"`
5. `git tag -a v1.3.0 -m "Release v1.3.0 - Dark mode and CSV export"`
6. Push with `--follow-tags` (Step 6)
**Output**: Released v1.3.0, tagged, and pushed.
</example>

<example>
**User request**: `/changelog v2.0.0` (explicit version)
**Action**: Use provided version. Write versioned entry. Commit, tag, push.
**Steps**:
1. Version: v2.0.0 (explicit, skip auto-detection)
2. Write `## [2.0.0] - 2026-02-13` entry
3. `git add CHANGELOG.md`
4. `git commit -m "Release v2.0.0"`
5. `git tag -a v2.0.0 -m "Release v2.0.0 - Complete API redesign"`
6. Push with `--follow-tags` (Step 6)
**Output**: Released v2.0.0, tagged, and pushed.
</example>

<example>
**User request**: `/changelog` (no new commits since last tag)
**Action**: All commits filtered. No release needed.
**Output**: No release needed. All commits since v1.3.0 are docs/test/CI changes.
</example>

<example>
**User request**: `/changelog` in Cowork, where git has no credentials for the remote
**Action**: The Step 1 fetch fails ("could not read Username"). Note "remote not checked", write the entry, commit, and tag; skip the push.
**Output**: Released v1.4.0 locally (commit a1b2c3d, tag v1.4.0), not pushed: git could not authenticate. Run from the repository: `git fetch origin`, `git status -sb`, `git push --follow-tags`, then `git ls-remote --tags origin v1.4.0`.
</example>

## References

| File | Content |
|------|---------|
| `references/changelog_format.md` | Full Keep a Changelog spec, Conventional Commits mapping, writing style guide, anti-patterns, release workflow reference, complete example |
