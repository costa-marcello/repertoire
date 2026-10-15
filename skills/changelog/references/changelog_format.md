# Changelog Format Specification

How the release section reads: the Keep a Changelog sections, the breaking-change bullet, the writing style, and a complete example. Which commits are included, and in which section, is decided by the Commit Categorization table in SKILL.md.

## Contents

1. [Sections](#sections)
2. [Breaking Changes](#breaking-changes)
3. [Writing Style Guidelines](#writing-style-guidelines)
4. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
5. [Complete Example](#complete-example)

## Sections

Based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/). Use only these six section headers, in this order, and only the ones with content (empty sections add noise):

| Section | Purpose | Examples |
|---------|---------|----------|
| **Added** | New features | New API endpoints, UI components, commands |
| **Changed** | Modifications to existing functionality | Updated algorithms, changed defaults |
| **Deprecated** | Features marked for future removal | Old API versions, legacy methods |
| **Removed** | Features deleted in this release | Dropped support, removed endpoints |
| **Fixed** | Bug corrections | Resolved crashes, fixed edge cases |
| **Security** | Vulnerability patches | CVE fixes, patched auth bypasses |

## Breaking Changes

A breaking change goes in the section that fits it, first in that section, as a bullet that starts with `**BREAKING**:` and tells users what to do instead.

**In the commit:**
```
feat!: remove deprecated endpoints

BREAKING CHANGE: The /v1/users endpoint has been removed.
Use /v2/users instead.
```

**In the changelog:**
```markdown
### Removed
- **BREAKING**: Removed the /v1/users endpoint; use /v2/users instead
```

## Writing Style Guidelines

### Audience-Appropriate Language

Default to end-user wording. Use developer wording when the people who use the release are developers: a library, an API, or a developer tool.

**For developers (API changelogs):**
```markdown
### Added
- Added the `POST /api/v2/webhooks` endpoint for event subscriptions
- Added the `retry_count` parameter to job configuration
```

**For end users (app store/product):**
```markdown
### Added
- Added real-time notifications for important events
- Added automatic retries when a job hits a temporary failure
```

### Entry Format

- Start with a capital letter
- Use the past tense ("Added", "Fixed", "Removed")
- No trailing periods
- One bullet per logical change
- Keep issue and pull request references such as `(#123)`

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

Group related items under one parent bullet when they belong to one feature:

```markdown
### Added
- Added export options:
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
| Mixing audiences | Technical and user-facing mixed | Write for the people who use the release; leave internal detail to the commit log |
| Inconsistent format | Different styles across versions | Use this spec consistently |
| Empty sections | Adds noise | Only include sections with content |
| Missing dates | Hard to track timelines | Always include release date |
| Vague entries | "Various improvements" | Be specific about what changed |

## Complete Example

A changelog right after a release, as this skill leaves it: no `[Unreleased]` section, newest version first, and footer links newest first.

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-11-15

### Added
- Added dark mode theme support
- Added CSV export for report data
- Added keyboard shortcuts for common actions

### Changed
- Improved dashboard loading time by 60%
- Updated authentication flow for better security

### Fixed
- Fixed crash when processing files over 100MB
- Resolved timezone display issues in reports

## [2.0.0] - 2025-10-01

### Added
- Added a plugin architecture for extensions
- Added real-time collaboration

### Changed
- Redesigned settings interface

### Deprecated
- Deprecated the legacy export format, which v3.0 will remove

### Removed
- **BREAKING**: Removed the API v1 endpoints; migrate to v2
- Removed support for Internet Explorer 11

### Security
- Fixed XSS vulnerability in comment rendering (CVE-2025-1234)

## [1.5.0] - 2025-09-15

### Added
- Added report generation and the first public command-line interface

[2.1.0]: https://github.com/owner/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/owner/repo/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/owner/repo/releases/tag/v1.5.0
```
