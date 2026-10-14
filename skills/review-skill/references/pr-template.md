# PR Template for Skill Contributions

The title and body format for Auto-PR. Write the title (one line) and the body to two files in the temporary folder that holds the clone. Show both to the user with the staged summary (`git diff --cached --stat`), and use them with `git commit -F` and `gh pr create --body-file` only after the user says yes. `mode-auto-pr.md` has the commands.

## Contents

1. [Title](#title)
2. [Body](#body)
3. [Filling it in](#filling-it-in)

## Title

Use a conventional-commit prefix and name the outcome:

```text
refactor: align <skill-name> with Anthropic's skill guidance
```

For a narrower PR:

```text
docs: add trigger conditions to the <skill-name> description
fix: report script errors instead of swallowing them in <skill-name>
```

## Body

```markdown
## Summary

This PR improves the <skill-name> skill against [Anthropic's skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). Review grade before: <letter>. After: <letter>. Based on upstream commit <short-hash> of <ref>.

### What this PR does

- <change 1, with its rule ID>
- <change 2, with its rule ID>

### What this PR does not change

- No files are deleted, renamed, or moved.
- <preserved item: the workflow, the language, the scripts' behavior, the author's structure>

## Changes

### 1. <change title> (<rule ID>)

**Before:** <current state, with file:line>

**After:** <the new state>

**Why:** <how this helps users or triggering, citing the guidance>

### 2. <change title> (<rule ID>)

...

## Deferred suggestions

These would need deletes, renames, moves, or Style changes, which this PR avoids. Each is ready to apply:

- <rule ID>: <the exact change>

<If a deferred Major fix leaves a Major finding open, say so and give the grade after the deferred fixes.>

## Files changed

| File | Change | Description |
|------|--------|-------------|
| SKILL.md | Modified | <summary> |
| <new reference file> | Added | <summary> |

## Test plan

- [ ] Invoke the skill with <a prompt from the trigger review> and confirm it triggers.
- [ ] Run <the skill's main workflow> on <an input> and compare the result with the previous version.
- [ ] <check that each moved section is still linked from SKILL.md>

## References

- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Claude Code skills](https://code.claude.com/docs/en/skills)

---

Generated with [Claude Code](https://claude.com/claude-code)
```

## Filling it in

- **Summary:** two or three sentences, the before and after grade, a link to the guidance, and the upstream commit the branch started from, shortened to 7 characters (the hash printed in step 3 of the commands in `mode-auto-pr.md`).
- **What this PR does not change:** always present. Name what was kept on purpose, so the author can see the review respected their design.
- **Changes:** one entry per rule ID, in the order Major, then Minor. Quote the guidance in a sentence or less where it explains the change.
- **Deferred suggestions:** every fix the Auto-PR limits ruled out, with the exact change. Write "None." when there are none.
- **Test plan:** steps a maintainer can run in a few minutes, using prompts from the trigger review.
- **Tone:** follow the tone table in `mode-auto-pr.md`. Describe benefits, not mistakes.
