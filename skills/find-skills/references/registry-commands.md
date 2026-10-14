# Registry Commands Reference

Command reference for the skill sources find-skills searches. Check a CLI's `--help` when a flag behaves differently; these tools change between releases. Node.js requirements are in SKILL.md's Troubleshooting table.

---

## Open Ecosystem (`npx skills`)

```bash
npx skills find [query]                         # Search (add --owner <owner> to search one owner's repositories)
npx skills add <owner/repo@skill> -a claude-code -g -y  # Install one skill for Claude Code, globally, without prompts
npx skills add <owner/repo> -s <skill>          # Name the skill with --skill (add -a claude-code -g -y as above)
npx skills add <owner/repo> --list              # List a repository's skills without installing
npx skills list                                 # List installed skills (alias: ls; add -g for global)
npx skills update                               # Update installed skills (alias: check)
npx skills remove <skill>                       # Remove an installed skill (alias: rm)
npx skills init <name>                          # Create a new SKILL.md scaffold
```

`npx skills find <query>` prints each result as `owner/repo@skill`, followed by its `https://skills.sh/...` page.

**Install locations for Claude Code:** `.claude/skills/` in the project by default, `~/.claude/skills/` with `-g`. With `-y` and no `-a`, the CLI installs into every coding agent it detects, or into every agent it supports when it detects none.

**Telemetry:** the CLI sends anonymous usage data, including search queries. `DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1` turns it off.

**Cowork:** search works, but an install lands in the session's temporary VM and is lost when the session ends. Install a plugin, or upload the skill as a ZIP (SKILL.md, Step 5).

**Browse:** https://skills.sh/

---

## CCPM (`ccpm`)

Run it without installing: `npx @daymade/ccpm <command>`. To install the CLI, ask the user first, then run `npm install -g @daymade/ccpm`.

```bash
ccpm search <query>                  # Search for skills
ccpm info <skill-name>               # Show skill details before installing
ccpm install <skill-name>            # Install for every project (~/.claude/skills/)
ccpm install <skill-name> --project  # Install to the current project only (.claude/skills/)
ccpm list                            # List installed skills (alias: ls)
ccpm update <skill-name>             # Update a skill to its latest version
ccpm uninstall <skill-name>          # Remove a skill (alias: remove)
```

**Browse:** https://ccpm.dev

**Cowork:** a CCPM install is lost with the session, like `npx skills`.

---

## Plugin Marketplaces

A GitHub repository is a marketplace when it has `.claude-plugin/marketplace.json` at its root. That file's `name` is the marketplace name, and its `plugins` list names the plugins.

**Claude Code** (the user types these):

```text
/plugin                                  # Browse, install, and manage plugins
/plugin marketplace add <owner/repo>     # Add a marketplace
/plugin install <plugin>@<marketplace>   # Open the plugin's details to pick a scope and install
/plugin marketplace update <marketplace> # Pull the marketplace's latest version
/reload-plugins                          # Load newly installed plugins without a restart
```

Anthropic's document skills (docx, pdf, pptx, xlsx) install this way: marketplace `anthropics/skills`, plugin `document-skills@anthropic-agent-skills`.

**Cowork:** Customize > Plugins, then Add > Add marketplace > Add from a repository. Enter `<owner/repo>` for GitHub, or a repository URL (public gitlab.com and bitbucket.org repositories work too), then install the plugin. A plugin file can be uploaded in the same place. Plugins added there are saved to the claude.ai account, so they also sync to Claude Code sessions signed in with that account, listed as `<plugin>@synced`.

**Repertoire:** marketplace `costa-marcello/repertoire`, plugin `repertoire@repertoire`. Its skills run as `/repertoire:<name>`; a single skill installed with `npx skills add costa-marcello/repertoire -s <name>` runs as `/<name>`.

---

## Common Search Terms

Use these keywords when searching:

| Category | Search Terms |
|----------|-------------|
| Web Development | react, nextjs, typescript, css, tailwind, vue, svelte |
| Testing | testing, jest, playwright, e2e, vitest, cypress |
| DevOps | deploy, docker, kubernetes, ci-cd, terraform, aws |
| Documentation | docs, readme, changelog, api-docs, jsdoc |
| Code Quality | review, lint, refactor, best-practices, eslint |
| Design | ui, ux, design-system, accessibility, shadcn |
| Productivity | workflow, automation, git, monorepo |
| Data & AI | data, ml, embeddings, vector, analysis |
