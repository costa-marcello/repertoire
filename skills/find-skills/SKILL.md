---
name: find-skills
description: "Discovers and installs agent skills from the open ecosystem and CCPM registries. Use when users ask 'how do I do X', 'find a skill for X', 'is there a skill that can...', 'ccpm', 'claude code skill', 'installed skills', or want to extend capabilities."
license: MIT
---

# Find Skills

Search query: `$ARGUMENTS`

If `$ARGUMENTS` is empty, ask the user what skill they need.

<instructions>

## Step 1: Pick the Registry

| User Request | Registry | CLI |
|--------------|----------|-----|
| General coding (React, testing, DevOps, linting) | Open Ecosystem | `npx skills` |
| Claude Code features, document processing (PDF, DOCX, XLSX, PPTX) | CCPM | `ccpm` |
| "installed skills", "my skills", "what do I have" | Both | `ccpm list` + `npx skills check` |

**Tiebreaker:** When the request could match either registry, run both searches and present combined results. Let the user pick.

## Step 2: Search

**Open Ecosystem:**
```bash
npx skills find $ARGUMENTS
```

**CCPM:**
```bash
ccpm search $ARGUMENTS
```

If one registry returns no results, search the other before reporting "not found".

## Step 3: Present Results

Show matching skills with name, description, and install command. When both registries return results, group them by registry with clear labels.

## Step 4: Install

**Open Ecosystem:**
```bash
npx skills add <owner/repo@skill> -g -y
```

**CCPM:**
```bash
ccpm install <skill-name>
```

## Step 5: Verify Installation

**Open Ecosystem:**
```bash
npx skills check
```
Confirm the skill appears in the installed list.

**CCPM:**
```bash
ccpm list
```
Confirm the skill appears. Remind the user to restart Claude Code -- CCPM skills load at startup.

**If verification fails:**
1. Check the error message from the install command output.
2. Run the install command again with verbose output.
3. Check write permissions: `ls -la ~/.claude/skills/`
4. If the skill still does not appear, consult the Troubleshooting section below.

</instructions>

## When No Skills Are Found

1. Tell the user no matching skill exists in either registry.
2. Attempt the task directly using built-in capabilities.
3. If the user wants a reusable solution, offer to create a custom skill:
   - Open Ecosystem: `npx skills init my-skill`
   - CCPM: invoke `/create-skill`

<example>
**User asks: "how do I make my React app faster?"**

1. Registry: Open Ecosystem (general coding topic).
2. Search: `npx skills find react performance`
3. Results show `vercel-labs/agent-skills@vercel-react-best-practices`.
4. Install: `npx skills add vercel-labs/agent-skills@vercel-react-best-practices -g -y`
5. Verify: `npx skills check` -- confirm skill appears in list.
6. Run the installed skill to help with the React performance task.
</example>

<example>
**User asks: "is there a skill for PDF processing?"**

1. Registry: CCPM (document processing topic).
2. Search: `ccpm search pdf`
3. Check details: `ccpm info pdf`
4. Install: `ccpm install pdf`
5. Verify: `ccpm list` -- confirm `pdf` appears.
6. Remind user to restart Claude Code for CCPM skills to load.
</example>

<example>
**User asks: "what skills do I have installed?"**

1. Run both: `ccpm list` and `npx skills check`
2. Combine results into a single list grouped by registry.
3. Report total count and highlight any skills with available updates.
</example>

<example>
**User asks: "find me a skill for testing" (ambiguous -- exists in both registries)**

1. Registry unclear -- run both searches.
2. Search: `npx skills find testing` and `ccpm search testing`
3. Present combined results:
   - **Open Ecosystem:** `playwright-testing`, `jest-helpers`, `vitest-runner`
   - **CCPM:** (no results)
4. Recommend the best match based on the user's project context.
5. Install the chosen skill from the matching registry.
</example>

<example>
**User asks: "find a skill for Kubernetes autoscaling" (no results)**

1. Registry: Open Ecosystem (DevOps topic).
2. Search: `npx skills find kubernetes autoscaling` -- no results.
3. Broaden search: `npx skills find kubernetes` -- still no results.
4. Search CCPM as fallback: `ccpm search kubernetes` -- no results.
5. Tell the user: "No matching skill found in either registry."
6. Offer to help directly with Kubernetes autoscaling using built-in knowledge.
7. Offer to create a custom skill: `npx skills init kubernetes-autoscaling`
</example>

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ccpm: command not found` | Run `npm install -g @daymade/ccpm` |
| `npx skills` hangs or fails | Check Node.js version is 18+: `node --version` |
| Skill not available after CCPM install | Restart Claude Code -- skills load at startup |
| Permission errors on install | Check write permissions: `ls -la ~/.claude/skills/` and fix with `chmod -R u+rw ~/.claude/skills/` |
| Install succeeds but skill not in list | Run `npx skills check` or `ccpm list` again. If still missing, reinstall with `--force` flag |
| Search returns too many results | Add more specific keywords to narrow the query |

## References

| File | Purpose |
|------|---------|
| `references/registry-commands.md` | Full CLI command reference for both registries and common search categories |
