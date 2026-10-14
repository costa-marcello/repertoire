# Registry Commands Reference

Command reference for the skill sources find-skills searches. Check a CLI's `--help` when a flag behaves differently; these tools change between releases.

---

## Open Ecosystem (`npx skills`)

```bash
npx skills find [query]                     # Search for skills (add --owner <owner> to search one owner's repositories)
npx skills add <owner/repo@skill> -g -y     # Install one skill globally, without prompts
npx skills add <owner/repo> -s <skill>      # Same, naming the skill with --skill
npx skills list                             # List installed skills (alias: ls; add -g for global)
npx skills update                           # Update installed skills
npx skills remove <skill>                   # Remove an installed skill (alias: rm)
npx skills init <name>                      # Create a new SKILL.md scaffold
```

**Install locations for Claude Code:** `.claude/skills/` in the project by default, `~/.claude/skills/` with `-g`.

**Cowork:** search works, but an install lands in the session's temporary VM and is lost when the session ends. Install a plugin instead (see below).

**Browse:** https://skills.sh/

---

## CCPM (`ccpm`)

Install the CLI with `npm install -g @daymade/ccpm` (Node.js 18 or later).

```bash
ccpm search <query>                  # Search for skills
ccpm install <skill-name>            # Install for the user
ccpm install <skill-name> --project  # Install to the current project only
ccpm info <skill-name>               # Show skill details before installing
ccpm list                            # List installed skills
ccpm uninstall <skill-name>          # Remove a skill
ccpm update                          # Update installed skills
```

**Browse:** https://ccpm.dev

**Post-install:** restart Claude Code; CCPM skills load at startup. In Cowork, a CCPM install is lost with the session, like `npx skills`.

---

## Plugin Marketplaces

A GitHub repository is a marketplace when it has `.claude-plugin/marketplace.json` at its root. That file's `name` is the marketplace name, and its `plugins` list names the plugins.

**Claude Code** (the user types these):

```text
/plugin                                  # Browse, install, and manage plugins
/plugin marketplace add <owner/repo>     # Add a marketplace
/plugin install <plugin>@<marketplace>   # Install a plugin from it
/plugin marketplace update <marketplace> # Pull the marketplace's latest version
```

**Cowork:** Customize > Plugins > Add marketplace, enter `<owner/repo>`, then install the plugin. A plugin file can be uploaded in the same place.

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
