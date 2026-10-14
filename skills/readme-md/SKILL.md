---
name: readme-md
description: Guides README creation, updates, and reviews with audience-matched templates. Use when writing READMEs for open source, personal, internal, or config projects, when a README is stale or missing sections, or when the user asks what a README should contain.
license: MIT
argument-hint: "[task and project type]"
---

# Crafting Effective READMEs

## Overview

Identify the audience first. Match sections, depth, and tone to what that audience needs.

<instructions>

## User Input

**User request:** $ARGUMENTS

If the request line above has text, extract the task type (creating, adding, updating, reviewing) and project type (OSS, personal, internal, config) from it. If it is empty or still shows an unfilled placeholder, take them from the user's message instead. When either source gives the task, skip Step 1 and proceed to Step 2. If neither source gives the task, begin at Step 1.

**Where the README goes:** write `README.md` in the root folder of the project it describes, the folder that holds its manifest (such as `package.json` or `pyproject.toml`). By default that is the working directory in Claude Code or the connected folder in Cowork; when the user names a subfolder (`packages/cli/`), it goes there. With no project folder (for example, a Cowork session with nothing connected), save it in the outputs folder. Always say where the file went.

## Gotchas

- Use only the commands, flags, versions, file paths, and license found in the project's files. Never invent a flag or a requirement; when the files don't say, ask the user or leave it out.
- A request to create a README when `README.md` already exists is an update: edit the existing file and keep its accurate parts instead of replacing it.
- A review reports and proposes; it leaves the file unchanged until the user asks for the edits.
- Link only files that exist; many projects have no `CONTRIBUTING.md` or `LICENSE` file.
- Add a badge only when something real backs it (a published package, a CI workflow file, a license file).

## Quick Workflow

Copy this checklist:

```
README Progress:
- [ ] Task identified: Creating / Adding / Updating / Reviewing
- [ ] Facts gathered from the project files
- [ ] Audience identified: _____
- [ ] Project type: OSS / Personal / Internal / Config
- [ ] Template selected from assets/templates/ (Creating or Adding only)
- [ ] Draft (or review report) complete; README location told to the user
- [ ] Verified against the project files (Step 4)
- [ ] Asked: "Anything else to highlight or include that I might have missed?"
```

## Process

### Step 1: Identify the Task

**Ask:** "What README task are you working on?"

| Task | When |
|------|------|
| **Creating** | New project, no README yet |
| **Adding** | Need to document something new |
| **Updating** | Capabilities changed, content is stale |
| **Reviewing** | Checking if README is still accurate |

### Step 2: Gather the Facts

Read the project before asking anything: the manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`), the entry points and CLI usage strings, `LICENSE`, and any existing `README.md`. Answer the questions below from those files; ask the user only what the files cannot answer. With no project folder, ask the user for the facts.

**Creating:**
1. What type of project is it? (see Project Types below)
2. What problem does it solve, in one sentence?
3. What's the quickest path to "it works"?
4. Anything notable to highlight?

**Adding a section:**
1. What needs documenting?
2. Where does it fit in the existing structure?
3. Who needs this info most?

**Updating:**
1. What changed? Ask only when the code doesn't show it.
2. Read the current README and find the stale sections.
3. Edit those sections in place, keeping the parts that are still accurate.

**Reviewing:**
1. Read the current README.
2. Check it against the project state: manifest, main files, CLI.
3. Report each stale or missing section with its evidence from the files and the replacement text.
4. Apply the edits only when the user asks; then also update the "Last reviewed" date, if the README has one.

### Step 3: Draft from the Template

When creating, copy the template for the project type (see Project Types) from the line after its `---` separator; the lines above it are notes for you. Replace every `[placeholder]`, and delete any section that has nothing real to say instead of leaving it empty. When adding a section to an existing README, model it on the matching section of the template.

Keep the template's section order. `references/art-of-readme.md` and `references/standard-readme-spec.md` order sections differently; read them as background, and follow the Standard Readme order only when the user asks for a Standard Readme compliant README.

### Step 4: Verify

Re-read the draft (or the review report) against the project files and fix what fails, then check again:
- Every command, flag, file path, version, and license appears in the project's files.
- No `[placeholder]` or template note remains.
- Every local link points to a file that exists.
- Every badge is backed by a real file, CI workflow, or published package.

### Step 5: Always Ask

After drafting or reporting, ask: **"Anything else to highlight or include that I might have missed?"**

## Project Types

| Type | Audience | Key Sections | Template |
|------|----------|--------------|----------|
| **OSS** (open source) | Contributors, users worldwide | Installation, Usage, Contributing, License | `assets/templates/oss.md` |
| **Personal** | Future-you, portfolio viewers | What it does, Tech stack, Learnings | `assets/templates/personal.md` |
| **Internal** | Teammates, new hires | Setup, Architecture, Runbooks | `assets/templates/internal.md` |
| **Config** | Future-you (confused) | What's here, Why, How to extend, Gotchas | `assets/templates/xdg-config.md` |

Tell the types apart from the files and the request: a published package or public repository with a license is OSS; dotfiles or tool settings with no build are Config; on-call, deployment, or private-registry details mean Internal; a side project or portfolio piece is Personal. **Ask the user** when these signals leave it unclear. Don't assume OSS defaults for everything.

## Essential Sections (All Types)

Every README needs at minimum:

1. **Name** - Self-explanatory title
2. **Description** - What + why in 1-2 sentences
3. **Usage** - How to use it (examples help). In a Config README, "How to Extend" and "Gotchas" play this part.

</instructions>

## Examples

<example>
**Task:** Creating README for OSS CLI tool

**Before (typical first draft):**
```markdown
# imgshrink
A tool for doing stuff with images.

## Installation
npm install imgshrink

## Usage
imgshrink [options]
```

**After (audience-focused; the Contributing and License sections are left out of this excerpt):**
````markdown
# imgshrink
Shrink PNG and JPEG files without visible quality loss. Works on whole folders and skips files it can't make smaller.

## Quick Start
```bash
npm install -g imgshrink
imgshrink photos/
```

## Common Use Cases
```bash
# Preview the savings without writing any file
imgshrink --dry-run photos/

# Keep each original next to its shrunk copy
imgshrink --keep-original banner.png
```
````

**Why better:** Shows the problem it solves, demonstrates real scenarios, gives copy-paste commands.
</example>

<example>
**Task:** Updating README after adding new feature

**Before (buried in wall of text):**
```markdown
## Features
This tool does X, Y, Z. It also now supports authentication via OAuth which can be configured using environment variables or a config file.
```

**After (scannable, actionable):**
````markdown
## Features
- **X** - Does this
- **Y** - Does that
- **Z** - Does the other thing
- **OAuth auth** (new in v2.0) - See [Authentication](#authentication)

## Authentication
Set `MYTOOL_OAUTH_TOKEN` or add to `~/.mytoolrc`:
```yaml
auth:
  provider: oauth
  token: your-token
```
````

**Why better:** New feature is discoverable, has its own section, shows exactly how to use it.
</example>

<example>
**Task:** Config folder README (for future-you)

**Before (no README or unhelpful):**
```markdown
# Config
My config files.
```

**After (answers future-you's questions):**
```markdown
# tmux Config

## What's Here
- `tmux.conf` - Entry point, sources everything else
- `conf/keys.conf` - All custom key bindings
- `plugins/` - Plugins, installed by TPM (not committed)

## Key Choices
- **Why TPM?** Installs and updates every plugin with one key press
- **Why `C-a` as the prefix?** Kept from years of GNU screen

## Gotchas
- Press `prefix + I` after pulling changes, or new plugins stay missing
- Edits apply only after `tmux source-file tmux.conf` or a server restart
```

**Why better:** Future-you at 2am will thank past-you for the "Gotchas" section.
</example>

<example>
**Task:** Creating README for internal team service

**Before (missing operational context):**
```markdown
# User Service
Handles users.

## Setup
Run `docker compose up`.
```

**After (onboarding-ready):**
````markdown
# User Service

Manages authentication, profiles, and role-based access for the platform.

**Team**: #platform-eng | **On-call**: PagerDuty rotation

## Dependencies
- **Upstream**: PostgreSQL, Redis, Auth0
- **Downstream**: Billing Service, Notification Service

## Local Setup

### Prerequisites
- Docker Desktop >= 4.x
- Access to 1Password `Platform Eng` vault for env vars

### Run

```bash
cp .env.example .env        # then fill from 1Password
docker compose up -d
curl http://localhost:3000/health   # expect {"status":"ok"}
```

### Tests

```bash
npm test                     # unit tests
npm run test:integration     # requires running Docker services
```

## Troubleshooting

### Auth0 callback fails locally
**Fix**: Set `AUTH0_BASE_URL=http://localhost:3000` in `.env`. The default points to staging.
````

**Why better:** New team members can run the service in under 5 minutes. Troubleshooting section prevents the most common support question.
</example>

<example>
**Task:** Reviewing an existing README for accuracy

**Before (stale, misleading):**
````markdown
# sheetsync
A Node library that copies a Google Sheet to CSV.

## Installation
npm install sheetsync

## Usage
```js
const { sync } = require("sheetsync");
await sync("SHEET_ID", "out.csv");
```
````

**Review findings (each with its evidence):**
1. The package is ESM-only (`"type": "module"` in `package.json`), so `require` fails
2. `sync()` is now `pull()`: `src/index.js` exports only `pull`
3. Node.js 20 or later is required (`engines` in `package.json`), and the README doesn't say so
4. The `sheetsync watch` command (`bin` in `package.json`) is undocumented

**After (applied once the user asked for the edits):**
````markdown
# sheetsync
Copy a Google Sheet to CSV once, or keep the file in sync as the sheet changes.

## Installation
Requires Node.js 20+

```bash
npm install sheetsync
```

## Usage

### Library
```js
import { pull } from "sheetsync";
await pull("SHEET_ID", "out.csv");
```

### CLI
```bash
npx sheetsync watch SHEET_ID out.csv
```
````

**Why better:** Every section matches the actual project state. Stale docs erode trust faster than no docs.
</example>

## References

| File | Read it when |
|------|--------------|
| `references/section-checklist.md` | Deciding which sections to keep or drop for the project type |
| `references/style-guide.md` | Writing or reviewing the prose: vague descriptions, buried prerequisites, filler |
| `references/art-of-readme.md` | Trimming a long README (move detail to linked pages), or arranging content from broad to specific (background; the template's order still wins) |
| `references/make-a-readme.md` | Deciding whether an optional section (Support, Roadmap, Visuals, Project Status) earns a place |
| `references/standard-readme-spec.md` | The user asks for a Standard Readme compliant README (see Step 3) |
| `references/standard-readme-example-minimal.md` | Same request, to see the smallest compliant layout |
| `references/standard-readme-example-maximal.md` | Same request, to see every optional section in place |
| `assets/templates/` | Step 3: oss, personal, internal, and xdg-config templates |
