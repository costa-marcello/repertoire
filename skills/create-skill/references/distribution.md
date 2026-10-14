# Distribution

Where a new skill goes, how Claude Code and Cowork load it, and when a zip is the right package. Read it in step 1 when the skill goes into a plugin repository or the session runs in Cowork, and in step 9.

## Contents

1. [How each product loads skills](#how-each-product-loads-skills)
2. [Where a new skill goes](#where-a-new-skill-goes)
3. [Shipping a change](#shipping-a-change)
4. [Calling another skill in the plugin](#calling-another-skill-in-the-plugin)
5. [Packaging a zip](#packaging-a-zip)

## How each product loads skills

| Route | Loaded by | Frontmatter | Package |
|-------|-----------|-------------|---------|
| Plugin (a repository with `.claude-plugin/`) | Claude Code and Cowork | All 20 Claude Code fields | None: the plugin installs from the repository |
| Skills folder (`.claude/skills/`, `~/.claude/skills/`) | Claude Code only | All 20 Claude Code fields | None |
| Single-skill upload | claude.ai and the Claude API | The six portable fields | A zip from `package_skill.py` |

- **Cowork** runs the Claude Code engine. It loads installed plugins, skills enabled on the claude.ai account, and skills the organisation provides. It never reads `~/.claude/skills`.
- **Plugin skills may use every field in Cowork.** A standalone upload accepts only the six portable fields, which is why Cowork gets skills through the plugin. Never strip `argument-hint` or any other field to make a skill fit Cowork. `frontmatter_reference.md` says which fields Cowork may ignore, so the body has to work without them (for example, take the input from the request when no arguments arrive).
- **Default target:** `claude-code` covers both rows that load through Claude Code's engine. Use `portable` only for the upload row.

## Where a new skill goes

Take the first case that applies.

1. **Cowork.** Write the skill into the connected folder, at `skills/<skill-name>/`. Cowork reads a repository's skills only through the installed plugin, so tell the user to push the commit and update the plugin. When the connected folder is not a plugin repository (no `.claude-plugin/`), say that the skill reaches Cowork only once it is part of an installed plugin.
2. **A plugin repository** (`.claude-plugin/` at its root, as in Repertoire): `skills/<skill-name>/`. The plugin finds skills in `skills/` by default; when `plugin.json` or the marketplace entry lists skills explicitly, add the new path there too (`marketplace_update.md`).
   - **On the user's own machine,** check two things: the repository has `scripts/link_user_skills.py`, and `~/.claude/skills/<plugin-name>` (the `name` in `.claude-plugin/plugin.json`) does not exist yet. When both hold, tell the user to run `python -B scripts/link_user_skills.py` once from the repository root. The script changes the user's `~/.claude/skills/`, so the user runs it, not you.
   - It links the whole repository as `~/.claude/skills/<plugin-name>`, and Claude Code loads the live checkout as the plugin `<plugin-name>@skills-dir`. Later skills then appear at the next session start, or after `/reload-plugins`, without running the script again.
3. **Otherwise:** `.claude/skills/<skill-name>/` in the current project, shared through the project's repository, or `~/.claude/skills/<skill-name>/` for a personal skill. Both load in Claude Code only. To reach Cowork as well, the skill has to move into a plugin repository.

## Shipping a change

- **Plugin users** get a pushed change when the plugin updates: `/plugin marketplace update <marketplace>` in Claude Code, while Cowork picks up the pushed commit.
- **A linked checkout** (`<plugin-name>@skills-dir`) is live: edits load at the next session start or after `/reload-plugins`.
- **A plugin added to the claude.ai account** also appears in Claude Code as `<plugin-name>@synced`; a linked checkout of the same name outranks it.
- **Versions:** follow `marketplace_update.md`. When the plugin's entries carry no `version`, do not add one.

## Calling another skill in the plugin

- **Invocation names.** A plugin skill runs as `/<plugin-name>:<skill-name>`; a skill installed into a skills folder runs as `/<skill-name>`. When one skill calls another, try `<plugin-name>:<skill-name>` first, then `<skill-name>`.
- **Files of a sibling skill.** `${CLAUDE_SKILL_DIR}/../<other-skill>/` reaches a sibling inside the same plugin, through a link or the plugin cache alike. The sibling may be missing when skills are installed one at a time, so give a fallback.

## Packaging a zip

Package only for a single-skill upload to claude.ai or the Claude API. Run `python scripts/package_skill.py <skill-dir> [output-dir]`, as step 9 of SKILL.md describes.

- **Portable rules.** It validates against the portable target and prints "This zip is for uploads to claude.ai and the Claude API, not for Cowork, which installs the plugin." A Claude Code-only field such as `argument-hint` is a definitive Major there, so it refuses such a skill, which ships through the plugin instead.
- **Left out of the zip:** the top-level `evals/`, `.git/`, `__pycache__/`, `node_modules/`, `.venv/`, `venv/`, `.env` files and folders except `.env.example`, `*.pyc`, `*.zip`, OS junk files, and the scan marker.
- **Refusals:** a definitive Major, a symlink or junction inside the skill, an output folder inside the skill, a missing or stale `.security-scan-passed` marker, and a SKILL.md reference to a bundled file the zip leaves out. Only a clean gitleaks scan writes the marker, so without gitleaks there is no zip.
