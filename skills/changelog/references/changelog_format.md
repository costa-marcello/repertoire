# Changelog Format Specification

## Contents

1. [Keep a Changelog Standard](#keep-a-changelog-standard)
2. [Conventional Commits Integration](#conventional-commits-integration)
3. [Writing Style Guidelines](#writing-style-guidelines)
4. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
5. [Complete Example](#complete-example)
6. [Tool Integration](#tool-integration)
7. [Release Workflow Reference](#release-workflow-reference)

Comprehensive reference for Keep a Changelog format, Conventional Commits integration, and best practices from industry standards.

## Keep a Changelog Standard

Based on [keepachangelog.com](https://keepachangelog.com/en/1.1.0/).

### Core Principles

1. **Written for humans, not machines** - Prioritize readability over parseability
2. **Entry for every version** - Document all notable changes
3. **Group by change type** - Use consistent sections
4. **Linkable versions** - Enable direct linking to specific releases
5. **Reverse chronological** - Latest changes first
6. **Include release dates** - Use ISO 8601 format (YYYY-MM-DD)
7. **Follow Semantic Versioning** - MAJOR.MINOR.PATCH

### Required Sections

Use only these six section headers, in this order:

| Section | Purpose | Examples |
|---------|---------|----------|
| **Added** | New features | New API endpoints, UI components, commands |
| **Changed** | Modifications to existing functionality | Updated algorithms, changed defaults |
| **Deprecated** | Features marked for future removal | Old API versions, legacy methods |
| **Removed** | Features deleted in this release | Dropped support, removed endpoints |
| **Fixed** | Bug corrections | Resolved crashes, fixed edge cases |
| **Security** | Vulnerability patches | CVE fixes, auth improvements |

**Only include sections with content.** Empty sections add noise.

### Version Header Format

```markdown
## [VERSION] - YYYY-MM-DD
```

Examples:
- `## [1.0.0] - 2025-09-15` (use actual release date)
- `## [2.3.1] - 2025-11-22`

For yanked (recalled) releases:
```markdown
## [1.0.1] - 2025-09-16 [YANKED]
```

**Note:** All dates must be actual release dates in ISO 8601 format, never placeholders in the final output.

### Unreleased Section

Use an Unreleased section at the top to accumulate changes between releases:

```markdown
## [Unreleased]

### Added
- Work-in-progress feature descriptions

### Fixed
- Bug fixes not yet released
```

When releasing, rename Unreleased to the new version and remove the Unreleased section entirely. The `/changelog` skill does not maintain an Unreleased section between releases; it writes one versioned entry per invocation.

### Footer Links

Add comparison links at the bottom for navigation:

```markdown
[Unreleased]: https://github.com/owner/repo/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/owner/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/owner/repo/releases/tag/v1.0.0
```

## Conventional Commits Integration

Based on [conventionalcommits.org](https://www.conventionalcommits.org/).

### Commit Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type to Section Mapping

| Commit Type | Changelog Section | Include? |
|-------------|-------------------|----------|
| `feat` | Added | Always |
| `fix` | Fixed | Always |
| `perf` | Changed | If user-visible |
| `refactor` | Changed | If API changes |
| `docs` | - | If user-facing |
| `style` | - | Rarely |
| `test` | - | Never |
| `build` | - | Rarely |
| `ci` | - | Never |
| `chore` | - | Rarely |
| `revert` | Fixed/Removed | Depends |

### Breaking Changes

Mark breaking changes prominently:

**In commit:**
```
feat!: remove deprecated endpoints

BREAKING CHANGE: The /v1/users endpoint has been removed.
Use /v2/users instead.
```

**In changelog:**
```markdown
### Changed
- **BREAKING**: Removed /v1/users endpoint - use /v2/users instead
```

Or use a dedicated section:
```markdown
### Breaking Changes
- Removed /v1/users endpoint - use /v2/users instead
```

## Writing Style Guidelines

### Audience-Appropriate Language

**For developers (API changelogs):**
```markdown
### Added
- `POST /api/v2/webhooks` endpoint for event subscriptions
- `retry_count` parameter to job configuration
```

**For end users (app store/product):**
```markdown
### Added
- Subscribe to real-time notifications for important events
- Jobs now automatically retry when temporary failures occur
```

### Entry Format

- Start with a capital letter
- Use present tense or past tense consistently (prefer past: "Added", "Fixed")
- No trailing periods
- One bullet per logical change
- Include relevant links or references

**Good:**
```markdown
- Added dark mode support (#123)
- Fixed crash when uploading large files
- Improved search performance by 40%
```

**Bad:**
```markdown
- added dark mode.
- Fixed the bug where the app crashes when you try to upload files that are really big
- Search is faster now
```

### Grouping Related Changes

Group related items when appropriate:

```markdown
### Added
- Export functionality:
  - PDF export with customizable margins
  - CSV export with column selection
  - JSON export for API consumers
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Commit dump | Too granular, noisy | Consolidate related changes |
| Missing context | "Fixed bug" - which bug? | Include issue number or description |
| Internal jargon | "Fixed JIRA-123" | "Fixed login timeout issue (#123)" |
| Mixing audiences | Technical and user-facing mixed | Separate changelogs or clear sections |
| Inconsistent format | Different styles across versions | Use this spec consistently |
| Empty sections | Adds noise | Only include sections with content |
| Missing dates | Hard to track timelines | Always include release date |
| Vague entries | "Various improvements" | Be specific about what changed |

## Complete Example

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GraphQL API support (experimental)

## [2.1.0] - 2025-11-15

### Added
- Dark mode theme support
- Export data to CSV format
- Keyboard shortcuts for common actions

### Changed
- Improved dashboard loading time by 60%
- Updated authentication flow for better security

### Fixed
- Fixed crash when processing files over 100MB
- Resolved timezone display issues in reports

## [2.0.0] - 2025-10-01

### Added
- New plugin architecture for extensions
- Real-time collaboration features

### Changed
- **BREAKING**: API v1 endpoints removed - migrate to v2
- Redesigned settings interface

### Deprecated
- Legacy export format (will be removed in v3.0)

### Removed
- Support for Internet Explorer 11

### Security
- Fixed XSS vulnerability in comment rendering (CVE-2025-1234)

## [1.5.0] - 2025-09-15

### Added
- Initial public release

[Unreleased]: https://github.com/owner/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/owner/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/owner/repo/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/owner/repo/releases/tag/v1.5.0
```

## Tool Integration

### Git Commands for Changelog Generation

```bash
# List commits since last tag with conventional format
git log --pretty=format:"%s" $(git describe --tags --abbrev=0)..HEAD

# Group commits by type
git log --pretty=format:"%s" v1.0.0..v1.1.0 | grep "^feat:"
git log --pretty=format:"%s" v1.0.0..v1.1.0 | grep "^fix:"

# Include commit bodies for breaking change detection
git log --pretty=format:"%B---" v1.0.0..v1.1.0 | grep -A5 "BREAKING"

# Get commits with issue references
git log --oneline v1.0.0..HEAD | grep -E "#[0-9]+"
```

### Automation Tools

The `/changelog` skill handles generation natively. Use external tools only when you need CI/CD integration or team-wide automation:

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **git-cliff** | Fast, customizable generation (default choice for automation) | `cliff.toml` |
| **semantic-release** | Fully automated CI/CD releases | `.releaserc` |
| **standard-version** | Bump version + generate changelog | `.versionrc.js` |
| **conventional-changelog** | Generate from conventional commits | CLI options |

## Release Workflow Reference

Reference for git operations used by the `/changelog` skill during commit, tag, and push workflows.

### Git Commands

```bash
# Stage changelog
git add CHANGELOG.md

# Commit (update mode)
git commit -m "Update changelog"

# Commit (release mode)
git commit -m "Release vX.Y.Z"

# Create annotated tag (release mode only)
git tag -a vX.Y.Z -m "Release vX.Y.Z - summary of changes"

# Push commit only (update mode)
git push

# Push commit and tags together (release mode)
git push --follow-tags
```

### Tag Naming Convention

- Always use the `v` prefix: `v1.0.0`, `v2.3.1`
- Tags follow Semantic Versioning: `vMAJOR.MINOR.PATCH`
- Match the tag version to the changelog heading version exactly

### Annotated vs Lightweight Tags

Always create **annotated tags** (`git tag -a`) for releases:

| Type | Command | Use Case |
|------|---------|----------|
| Annotated | `git tag -a v1.0.0 -m "message"` | Releases (stores author, date, message) |
| Lightweight | `git tag v1.0.0` | Never use for releases |

Annotated tags store the tagger name, email, date, and message. They are proper git objects and are the standard for release tags. `git push --follow-tags` only pushes annotated tags, not lightweight ones.

### The `--follow-tags` Flag

`git push --follow-tags` pushes commits and any annotated tags that point to commits being pushed. This ensures the tag and commit arrive at the remote together in a single operation.

Benefits:
- Atomic: tag and commit pushed together
- Safe: only pushes annotated tags (not lightweight)
- Only pushes tags reachable from the commits being pushed

### Pre-Flight Checks

```bash
# Check for uncommitted changes
git status --porcelain

# Fetch latest remote state
git fetch origin

# Check if local branch is behind remote
git rev-list --count HEAD..origin/$(git branch --show-current)

# Check if tag already exists
git tag -l "vX.Y.Z"

# Verify tag reached remote after push
git ls-remote --tags origin | grep "vX.Y.Z"
```

