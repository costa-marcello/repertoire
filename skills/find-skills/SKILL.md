---
name: find-skills
description: "Finds and installs skills and plugins for Claude Code and Cowork from the skills.sh open ecosystem, the CCPM registry, and plugin marketplaces, choosing the install route that lasts in each product. Use when the user asks 'find a skill for X', 'is there a skill or plugin that can...', mentions skills.sh, npx skills or ccpm, asks which skills are installed, or wants to extend Claude's capabilities."
argument-hint: "[what the skill should do]"
license: MIT
---

# Find Skills

Search query: `$ARGUMENTS`

If that line is empty or still shows an unfilled placeholder, take the query from the user's message. If the message has none, ask what the skill should do.

<instructions>

## Step 1: Know Where the Skill Will Run

The install route depends on the product, because a skill only works where that product loads it.

| Product | Install route that lasts |
|---------|--------------------------|
| Claude Code | A plugin from a marketplace (`/plugin`), or a single skill with `npx skills add` or `ccpm install` |
| Cowork | A plugin only: Customize > Plugins > Add marketplace, or upload a plugin |

In Cowork, `npx skills add` and `ccpm install` write into the session's temporary VM, which is thrown away when the session ends, and Cowork never reads `~/.claude/skills` anyway. Searching with them still works there; installing with them does not. When your context does not say which product this is, give both routes.

## Step 2: Check What Is Already Available

Before searching, check the skills listed in your own context. That list already covers plugin, project, user, and built-in skills in both products.

- **Word, PDF, PowerPoint, and Excel files:** Anthropic ships docx, pdf, pptx, and xlsx skills built in to Claude Code and Cowork. Point the user to those instead of searching registries. They are not Repertoire skills.
- **Repertoire skills:** when the need matches one of these, name it by its plugin name first, then its single-skill name: `/repertoire:<name>` when the Repertoire plugin is installed, `/<name>` when the skill was added on its own.

| Skill | Use it for |
|-------|------------|
| changelog | Changelogs and tagged releases |
| claudia-md | Auditing, improving, and generating CLAUDE.md files |
| create-skill | Building and updating skills, with evals |
| frontend-design | Distinctive, production-grade frontend interfaces |
| mermaid-diagrams | Software diagrams in Mermaid |
| readme-md | Writing, updating, and reviewing READMEs |
| research | Researching a topic across many sources |
| review-skill | Grading and fixing skills |

This list can lag behind the repository; the README at https://github.com/costa-marcello/repertoire is current. To install Repertoire, see [Step 5](#step-5-install).

## Step 3: Search

| Request | Search with |
|---------|-------------|
| General coding (React, testing, DevOps, linting) | skills.sh: `npx skills find <query>` |
| Skills made for Claude Code | CCPM: `ccpm search <query>` |
| A plugin | Marketplaces the user already added: `/plugin` in Claude Code, Customize > Plugins in Cowork. Then search skills.sh and check whether each result's repository is a marketplace |

Replace `<query>` with the search query. When the request could match more than one source, run both searches and group the results by source. If one source returns nothing, search the other before reporting "not found".

Both CLIs send the query over the network (skills.sh, ccpm.dev, and GitHub). `npx skills` needs Node.js 18 or later; `ccpm` is a separate install (see Troubleshooting). If a search fails for lack of network access, which Cowork's egress rules can cause, say so and suggest the user browse https://skills.sh/ or https://ccpm.dev themselves.

## Step 4: Present Results

For each match, show its name, a one-line description, its source, and the install command for the user's product (Step 1). Recommend one and say why.

A GitHub repository is a plugin marketplace when it has `.claude-plugin/marketplace.json` at its root. Check before offering the marketplace route: fetch `https://raw.githubusercontent.com/<owner>/<repo>/HEAD/.claude-plugin/marketplace.json`. A 404 means it is not a marketplace. The file's `name` field is the marketplace name, and its `plugins` list holds the plugin names.

## Step 5: Install

Install only the skill the user picked.

**Claude Code, plugin** (preferred when the repository is a marketplace). These are commands the user types, so give them to the user:

```text
/plugin marketplace add <owner/repo>
/plugin install <plugin>@<marketplace>
```

For Repertoire: `/plugin marketplace add costa-marcello/repertoire`, then `/plugin install repertoire@repertoire`.

**Claude Code, single skill.** Run one of these:

```bash
npx skills add <owner/repo@skill> -g -y
ccpm install <skill-name>
```

`-g` installs for every project (`~/.claude/skills/`); leave it out to install into this project's `.claude/skills/`. For one Repertoire skill: `npx skills add costa-marcello/repertoire -s <name> -g -y`.

**Cowork:**
- The repository is a marketplace: tell the user to open Customize > Plugins > Add marketplace, enter `<owner/repo>` (for Repertoire, `costa-marcello/repertoire`), and install the plugin from it.
- The user has a plugin file: tell them to upload it in Customize > Plugins.
- Neither: say plainly that the skill cannot be installed in Cowork from inside the session, because the install would be lost when the session ends. Offer to do the task directly, or to install it in Claude Code.

## Step 6: Verify Installation

- **Plugin in Claude Code:** ask the user to open `/plugin` and confirm it is listed. Its skills run as `/<plugin>:<skill>`. If they do not appear, ask the user to restart Claude Code.
- **npx skills:** run `npx skills list -g` (without `-g` for a project install) and confirm the skill appears.
- **CCPM:** run `ccpm list`, confirm the skill appears, and remind the user to restart Claude Code, because CCPM skills load at startup.
- **Cowork:** ask the user to start a new session and check that the plugin's skills are listed.

If verification fails, read the install command's output, run the install once more, and then use Troubleshooting.

</instructions>

## When No Skills Are Found

1. Tell the user no matching skill exists in the sources searched.
2. Do the task directly with built-in capabilities.
3. If the user wants a reusable solution, offer to build one with Repertoire's create-skill (`/repertoire:create-skill`, or `/create-skill` when installed on its own), or scaffold one with `npx skills init <name>`.

<example>
**User asks in Claude Code: "how do I make my React app faster? is there a skill for that?"**

1. Source: skills.sh (general coding topic).
2. Search: `npx skills find react performance`
3. Results include `vercel-labs/agent-skills@react-best-practices`. Present it with its description and source.
4. After the user picks it: `npx skills add vercel-labs/agent-skills@react-best-practices -g -y`
5. Verify: `npx skills list -g` shows the skill.
6. Use the installed skill for the React performance task.
</example>

<example>
**User asks in Cowork: "find me a skill that writes changelogs and install it"**

1. Repertoire's changelog matches: `/repertoire:changelog` with the plugin, or `/changelog` on its own.
2. Do not run `npx skills add` or `ccpm install`: the install would vanish with the session.
3. Tell the user: Customize > Plugins > Add marketplace, enter `costa-marcello/repertoire`, and install the `repertoire` plugin.
4. Verify: in a new session, the user checks that `changelog` is listed.
</example>

<example>
**User asks: "is there a skill for filling in PDF forms?"**

1. Anthropic's built-in pdf skill covers this in Claude Code and Cowork; check that it is listed in your context.
2. Use it, or point the user to it. Do not search the registries, and do not describe it as a Repertoire skill.
</example>

<example>
**User asks: "what skills do I have installed?"**

1. List the skills in your context, grouped by where they come from (plugin, project, user, built-in).
2. In Claude Code, add what `npx skills list -g` and `ccpm list` report, and suggest `/plugin` to see installed plugins.
3. Report the total.
</example>

<example>
**User asks: "find a skill for Kubernetes autoscaling" (no results)**

1. Search: `npx skills find kubernetes autoscaling`, then the broader `npx skills find kubernetes`. No results.
2. Search CCPM as a fallback: `ccpm search kubernetes`. No results.
3. Tell the user no matching skill was found.
4. Help with Kubernetes autoscaling directly, and offer to build a custom skill.
</example>

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ccpm: command not found` | Ask before installing it globally: `npm install -g @daymade/ccpm` |
| `npx skills` hangs or fails | Check that Node.js is 18 or later: `node --version` |
| Skill not available after a CCPM install | Restart Claude Code; CCPM skills load at startup |
| Permission errors on install (Claude Code) | Check write access to `~/.claude/skills/` and fix it, or install into the project without `-g` |
| Install succeeds but the skill is not listed | Run `npx skills list -g` or `ccpm list` again; if it is still missing, reinstall |
| Installed in Cowork with `npx skills` or `ccpm`, then gone | Expected: the session VM was discarded. Install as a plugin instead (Step 5) |
| Search returns too many results | Add more specific keywords to the query |

## References

| File | Purpose |
|------|---------|
| `references/registry-commands.md` | Full command reference for skills.sh, CCPM, and plugin marketplaces, plus common search terms |
