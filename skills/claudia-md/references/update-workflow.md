# Update Mode: Codebase Scanning & Sync Workflow

## Contents

1. [Phase U1: Codebase Scan](#phase-u1-codebase-scan)
2. [Phase U2: Existing CLAUDE.md Read](#phase-u2-existing-claudemd-read)
3. [Phase U3: Drift Detection](#phase-u3-drift-detection)
4. [Phase U4: Change Preview](#phase-u4-change-preview)
5. [Phase U5: User Approval](#phase-u5-user-approval)
6. [Phase U6: Apply Updates](#phase-u6-apply-updates)
7. [Greenfield Mode (No Existing CLAUDE.md)](#greenfield-mode-no-existing-claudemd)
8. [Monorepo Handling](#monorepo-handling)

<!-- v1.0.0 | 2026-02-13 -->

Detailed algorithm for the Update mode. The SKILL.md contains the compact summary; this reference provides the full scanning heuristics.

---

## Phase U1: Codebase Scan

Scan the project to build a picture of the current state. Check each source in order.

### Package Manager & Commands

| File | Package Manager | Command Source |
|------|----------------|----------------|
| `package.json` | npm/yarn/pnpm (check lockfile) | `scripts` object |
| `Cargo.toml` | cargo | `[package]` metadata |
| `go.mod` | go modules | N/A (use `go` commands) |
| `pyproject.toml` | pip/poetry/uv | `[tool.poetry.scripts]` or `[project.scripts]` |
| `Makefile` | make | Target names |
| `Justfile` | just | Recipe names |
| `Taskfile.yml` | task | Task names |
| `deno.json` | deno | `tasks` object |
| `bun.lockb` | bun | Uses package.json scripts |

**Lockfile detection** (determines which package manager to recommend):

| Lockfile | Manager |
|----------|---------|
| `package-lock.json` | npm |
| `yarn.lock` | yarn |
| `pnpm-lock.yaml` | pnpm |
| `bun.lockb` | bun |

**Priority commands to extract:**

| Category | Scripts to look for |
|----------|-------------------|
| Install | `install`, `setup`, `bootstrap` |
| Dev | `dev`, `start`, `serve` |
| Build | `build`, `compile`, `bundle` |
| Test | `test`, `test:unit`, `test:e2e`, `test:integration` |
| Lint | `lint`, `format`, `check`, `typecheck` |
| Deploy | `deploy`, `release`, `publish` |

### Directory Structure

Scan top-level directories. Skip: `node_modules`, `dist`, `build`, `.git`, `.next`, `__pycache__`, `.venv`, `target`, `vendor`, `.cache`, `coverage`.

For each visible directory, record:
- Name and apparent purpose (from naming convention)
- Approximate file count
- Whether it contains an `index` or entry point file

### Framework & Tech Stack Detection

| Signal | Framework/Tech |
|--------|---------------|
| `next.config.*` | Next.js |
| `vite.config.*` | Vite |
| `astro.config.*` | Astro |
| `svelte.config.*` | SvelteKit |
| `nuxt.config.*` | Nuxt |
| `angular.json` | Angular |
| `remix.config.*` | Remix |
| `tailwind.config.*` | Tailwind CSS |
| `tsconfig.json` | TypeScript |
| `prisma/schema.prisma` | Prisma ORM |
| `drizzle.config.*` | Drizzle ORM |
| `docker-compose.yml` | Docker Compose |
| `Dockerfile` | Docker |
| `.github/workflows/` | GitHub Actions CI |
| `vitest.config.*` | Vitest |
| `jest.config.*` | Jest |
| `playwright.config.*` | Playwright |
| `cypress.config.*` | Cypress |
| `.eslintrc*` / `eslint.config.*` | ESLint |
| `biome.json` | Biome |
| `.prettierrc*` | Prettier |

### Environment & Config

Check for:
- `.env.example` or `.env.local.example` — extract variable names (not values)
- `docker-compose.yml` — extract service names
- CI config (`.github/workflows/`, `.gitlab-ci.yml`, etc.)

### Key Files

Identify entry points and important files:
- `src/index.*`, `src/main.*`, `src/app.*` — application entry
- `src/lib/*`, `src/utils/*` — shared utilities
- Config files at root level
- README, CONTRIBUTING, LICENSE

---

## Phase U2: Existing CLAUDE.md Read

Read the current `./CLAUDE.md` if it exists. Parse into sections by heading level.

**Section classification:**

| Section Type | Examples | User-authored? |
|-------------|---------|----------------|
| Factual | Commands, Architecture, Key Files, Environment | Partially (commands discovered, but user may have added context) |
| Authored | Hard Rules, Core Principles, Code Style, Gotchas, Workflow | Yes — never overwrite without asking |
| Generated | Sections with `<!-- auto-updated -->` comment | No — safe to refresh |

If no CLAUDE.md exists, skip to Phase U4 and generate a complete file from scan results.

---

## Phase U3: Drift Detection

Compare each discoverable section against what the CLAUDE.md documents.

### Commands Drift

| Drift Type | Detection | Action |
|-----------|-----------|--------|
| Missing command | Script exists in package.json but not in CLAUDE.md | Propose addition |
| Stale command | CLAUDE.md references script that no longer exists | Propose removal or update |
| Wrong package manager | CLAUDE.md says `npm` but lockfile is `pnpm` | Propose correction |

### Structure Drift

| Drift Type | Detection | Action |
|-----------|-----------|--------|
| New directory | Directory exists but not in Architecture section | Propose addition |
| Removed directory | Architecture lists directory that no longer exists | Propose removal |
| Renamed file | Key Files references path that moved | Propose path update |

### Tech Stack Drift

| Drift Type | Detection | Action |
|-----------|-----------|--------|
| New framework | Config file detected but not mentioned | Propose mention |
| Removed framework | CLAUDE.md mentions framework but config missing | Flag for review (might be intentional) |

### Preservation Rules

**Never auto-remove or overwrite:**
- Hard Rules and their reasoning
- Core Principles
- Code Style conventions
- Gotchas (unless they reference deleted files)
- Workflow preferences
- Any section with user reasoning ("because", "since", "to prevent")

**Safe to update:**
- Commands table (factual, verifiable)
- Architecture tree (factual, verifiable)
- Key Files list (factual, verifiable)
- Framework/tech mentions (factual, verifiable)

---

## Phase U4: Change Preview

Present all changes grouped by type:

```
### Additions (new content)
+ [section/content being added]

### Updates (changed content)
~ [what changed and why]

### Removals (stale content)
- [what would be removed and why]

### Unchanged (user-authored, preserved)
= [sections left untouched]
```

Always show what stays unchanged to reassure the user their authored content is safe.

---

## Phase U5: User Approval

Present three options:
1. **Apply all** — Write all proposed changes
2. **Select specific** — User picks which changes to apply
3. **Cancel** — No changes made

---

## Phase U6: Apply Updates

Apply approved changes using the Edit tool. Preserve:
- Existing heading structure and order
- User-authored reasoning and rules
- Comments and formatting conventions

If creating a new CLAUDE.md from scratch, use the root template from `references/templates.md` as the base structure.

---

## Greenfield Mode (No Existing CLAUDE.md)

When no CLAUDE.md exists, Update mode acts as an init:

1. Run full codebase scan (Phase U1)
2. Generate a complete CLAUDE.md using the root template
3. Include: project description (from README or package.json), commands, architecture, key files
4. Add placeholder sections: `## Hard Rules`, `## Gotchas` with a comment `<!-- Add project-specific rules here -->`
5. Preview the full file for approval before writing

---

## Monorepo Handling

For monorepos (detected by `packages/`, `apps/`, or workspaces config):

1. Scan root-level package.json for workspace commands
2. List each workspace package with its purpose
3. Note shared dependencies or build ordering
4. Suggest running Generate mode afterwards for package-level CLAUDE.md files
