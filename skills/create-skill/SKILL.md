---
name: create-skill
description: "Guides users through creating effective Claude Code skills with specialized knowledge, workflows, and tool integrations. Use when users want to create a new skill, update an existing skill, extract business logic into reusable packages, or ask about skill structure, frontmatter, or bundled resources."
license: MIT
context: fork
argument-hint: "[skill-name]"
---

# Create Skill

<context>

## About Skills

Skills extend Claude's capabilities with specialized workflows, tool integrations, domain expertise, and bundled resources. See `references/skill_anatomy.md` for detailed structure.

**Key structure:** `SKILL.md` (required) + optional `scripts/`, `references/`, `assets/` directories.

### YAML Frontmatter Reference

See `references/frontmatter_reference.md` for the complete field reference table. Key fields:

- **`name`**: Lowercase, hyphens only (max 64 chars). No reserved words (anthropic, claude). Noun or short-phrase form preferred (pdf, changelog, frontend-design).
- **`description`**: Third-person verb + triggers (max 1024 chars)
- **`context: fork`**: Set ONLY for Class A (autonomous) skills — those that run end-to-end without dispatching sub-agents, without pausing for the user, and without relying on the lead's reasoning context. See `references/frontmatter_reference.md` for the full four-class taxonomy. Class B (orchestrator), C (interactive), and D (mode-style reasoning) must run inline.

<example>
**Task-based skill with subagent execution:**
```yaml
---
name: deep-research
description: "Researches topics thoroughly using multiple sources. Use when the user needs in-depth analysis of code, architecture, or documentation."
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:
1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```
When invoked as `/deep-research authentication flow`, `$ARGUMENTS` becomes `authentication flow`.
</example>

<example>
**Side-effect skill requiring explicit invocation:**
```yaml
---
name: deploy-staging
description: "Deploys the current branch to the staging environment. Use when users request deployment or staging preview."
context: fork
disable-model-invocation: true
---
```
`disable-model-invocation: true` prevents auto-invocation. The user must run `/deploy-staging` explicitly.
</example>

See `references/frontmatter_reference.md` for additional examples (inline reference skills, medium-freedom skills with tool restrictions).

### Invocation Control

See `references/frontmatter_reference.md` for the full invocation control matrix and the four-class taxonomy. Key rule: add `context: fork` only to Class A autonomous skills; Class B (orchestrator), C (interactive), and D (mode-style reasoning) must run inline.

### Bundled Resources

See `references/bundled_resources.md` for guidance on `scripts/`, `references/`, and `assets/` directories. For public distribution, use relative paths only -- no absolute paths, personal info, or version numbers.

### Best Practices

Read `references/anthropic_best_practices_summary.md` before creating or updating skills. For complete official documentation: [Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

</context>

## Skill Creation Process

<instructions>

**Edit at the source location.** Do not edit skills in `~/.claude/plugins/cache/` -- changes are lost on cache refresh. Before any edit, confirm the file path does not contain `/cache/` or `/plugins/cache/`. Always edit the source repository copy.

**User input:** $ARGUMENTS

If `$ARGUMENTS` is non-empty, extract the skill name and purpose from it. Skip Step 1 and proceed to Step 2. Only ask clarifying questions if the skill's purpose is entirely unclear.

If `$ARGUMENTS` is empty, begin at Step 1.

To create a skill, follow the "Skill Creation Process" in order, skipping steps only if there is a clear reason why they are not applicable.

### Step 1: Understanding the Skill with Concrete Examples

**Skip this step when:** the user has already described what the skill should do (via arguments or prior context).

When the skill's usage patterns are not yet clear, gather concrete examples of how it will be used. Ask the questions below in order. Stop when the skill's functionality, trigger phrases, and example invocations are all clear:

- "What functionality should the skill support?"
- "Can you give examples of how it would be used?"
- "What would a user say that should trigger this skill?"

Conclude this step when there is a clear sense of the functionality the skill should support.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Determining the appropriate level of freedom for Claude
3. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

**Match specificity to task risk:**
- **High freedom (text instructions)**: Multiple valid approaches exist; context determines best path (e.g., code reviews, troubleshooting, content analysis)
- **Medium freedom (pseudocode with parameters)**: Preferred patterns exist with acceptable variation (e.g., API integration patterns, data processing workflows)
- **Low freedom (exact scripts)**: Operations are fragile, consistency critical, sequence matters (e.g., PDF rotation, database migrations, form validation)

See `references/planning_examples.md` for detailed examples (pdf-editor, frontend-webapp-builder, big-query skills).

Analyze each concrete example to create a list of reusable resources: scripts, references, and assets.

### Step 3: Initializing the Skill

At this point, it is time to actually create the skill.

Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.

When creating a new skill from scratch, run `init_skill.py` to generate a complete template:

```bash
python3 scripts/init_skill.py <skill-name> --path <output-directory>
```

The script creates a skill directory with SKILL.md, frontmatter, resource directories, and example files. Edit or delete any generated file that does not match the skill's scope decided in Step 2.

### Step 4: Edit the Skill

When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Claude to use. Include information that is non-obvious to Claude. Identify the procedural knowledge, domain-specific details, or reusable assets that would help another Claude instance execute these tasks more effectively, and write them into SKILL.md or the appropriate reference file.

#### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.

Also, delete any example files and directories not needed for the skill. The initialization script creates example files in `scripts/`, `references/`, and `assets/` to demonstrate structure, but most skills won't need all of them.

**When updating an existing skill**: Scan all existing reference files to check if they need corresponding updates. New features often require updates to architecture, workflow, or other existing documentation to maintain consistency.

#### Reference File Naming

Filenames must be self-explanatory without reading contents.

**Pattern**: `<content-type>_<specificity>.md`

**Examples**:
- Bad: `commands.md`, `cli_usage.md`, `reference.md`
- Good: `script_parameters.md`, `api_endpoints.md`, `database_schema.md`

**Test**: Can someone understand the file's contents from the name alone?

#### Update SKILL.md

**Before writing: load the review criteria as authoring rules.** Read `references/review_criteria_mirror.md`. It maps every rule `/review-skill` enforces to a concrete authoring instruction. Applying those rules while drafting — rather than patching afterwards — is what makes the skill Grade A on first review. Creation and review share the same checklists; author to them from the start.

**Writing Style:** Write the skill body in **imperative/infinitive form** (verb-first instructions), not second person. Use objective, instructional language (e.g., "To accomplish X, do Y" rather than "You should do X" or "If you need to do X"). The `description` field in frontmatter is the exception: it must be in **third-person verb form** ("Processes...", "Extracts...", "Reviews...") — see `references/frontmatter_reference.md`. Review-skill flags imperative descriptions as an M8 major issue.

To complete SKILL.md, answer the following questions:

1. What is the purpose of the skill, in a few sentences?
2. When should the skill be used?
3. In practice, how should Claude use the skill? All reusable skill contents developed above should be referenced so that Claude knows how to use them.

**Use `<example>` blocks** around concrete examples to help Claude distinguish examples from instructions.

#### Consistency Verification

Before finalizing, check for contradictions using Grep:

1. For each default value or rule in SKILL.md, grep the references/ folder for the same topic. Verify values match. Fix any mismatches by updating the stale copy.
2. For each term used more than twice, grep across all files to confirm the same word refers to the same concept throughout (e.g., do not mix "user" and "customer" for the same entity).
3. For each reference file mentioned in SKILL.md, open it and confirm the guidance aligns with what SKILL.md states. Delete stale cross-references.

### Step 5: Validation Checkpoint

Validation has two layers. The fast layer (a) catches frontmatter, line-count, and class-taxonomy mistakes cheaply. The authoritative layer (b) is `review-skill`, which applies the three full checklists and assigns a letter grade. Both must pass before packaging.

**(a) Fast pre-flight: `quick_validate.py`.**

```bash
python3 scripts/quick_validate.py <path/to/skill-folder>
```

Check the output for:
- Frontmatter errors (missing fields, naming violations, incorrect `context: fork` for the skill's class)
- Description errors (imperative/second-person voice) and warnings (missing trigger conditions)
- Line count warnings (under 400 recommended, 500 hard limit)
- Missing referenced files (paths in SKILL.md that do not exist on disk)
- `<example>` block count (3-5 target)

Fix all errors and warnings before continuing.

**(b) Authoritative gate: `review-skill` (required before packaging).**

```
/review-skill "<absolute/path/to/skill-folder>" report only
```

This runs the full deep review across all three checklists (structural, content quality, 6 research-backed criteria). The target is **Grade A** — 0 major issues, 0 minor issues. If the review returns any major (M1-M8) or minor (m1-m8) finding, fix it and re-run. Do not proceed to Step 6 until the report shows Grade A.

The pre-flight script cannot catch every review-skill rule (weak-verb density, defect taxonomy, anti-patterns, HELM clarity, diverse examples). `/review-skill` is the only gate that guarantees the skill will pass a subsequent independent audit — the "flying colours" outcome.

### Step 6: Sanitization Review (Optional)

**Ask the user before executing this step:** "This skill appears to be extracted from a business project. Would you like me to perform a sanitization review to remove business-specific content before public distribution?"

Skip this step if:
- The skill was created from scratch for public use
- The user explicitly declines sanitization
- The skill is intended for internal/private use only

**When to perform sanitization:**
- Skill was extracted from a business/internal project
- Skill contains domain-specific examples from real systems
- Skill will be distributed publicly or to other teams

**Sanitization process** (detailed in `references/sanitization_checklist.md`):

1. Run the automated grep scans from the checklist against the skill folder
2. Review each match and apply the category-specific replacements
3. Re-run all scan patterns to confirm no matches remain
4. Read through the skill to verify coherence and functionality

### Step 7: Security Review

Before packaging or distributing a skill, run the security scanner:

```bash
python3 scripts/security_scan.py <path/to/skill-folder>           # Quick scan (required)
python3 scripts/security_scan.py <path/to/skill-folder> --verbose  # Detailed review
```

Install gitleaks first if not present (`brew install gitleaks` on macOS). The script prints installation instructions and remediation guidance for any issues found.

### Step 8: Packaging a Skill

Package the skill into a distributable zip. The script validates before packaging:

```bash
python3 scripts/package_skill.py <path/to/skill-folder>            # Output to current dir
python3 scripts/package_skill.py <path/to/skill-folder> ./dist      # Output to ./dist
```

The packaging script will:

1. **Validate** the skill automatically, checking:
   - YAML frontmatter format and required fields
   - Skill naming conventions and directory structure
   - Description completeness and quality
   - **Path reference integrity** - all `scripts/`, `references/`, and `assets/` paths mentioned in SKILL.md must exist

2. **Package** the skill if validation passes, creating a zip file named after the skill (e.g., `my-skill.zip`) that includes all files and maintains the proper directory structure for distribution.

**Common validation failure:** If SKILL.md references `scripts/my_script.py` but the file doesn't exist, validation will fail with "Missing referenced files: scripts/my_script.py". Fix any validation errors and run the packaging command again.

### Step 9: Update Marketplace

After packaging, update the marketplace registry so the skill is discoverable. Read `references/marketplace_update.md` for the JSON template and semver versioning rules.

### Step 10: Iterate

After testing the skill, users request improvements based on observed failures.

**Iteration workflow:**
1. Run the skill on a real task. Record each point where Claude hesitates, asks an unnecessary question, or produces wrong output.
2. For each failure, grep SKILL.md and references/ to find the responsible section.
3. Apply the fix: add missing context, replace vague instructions with specific commands, or add an `<example>` block covering the failure case.
4. Run `python3 scripts/quick_validate.py <path/to/skill-folder>` to confirm no structural regressions.
5. Re-run the same task to verify the fix resolved the issue.

**Refinement filter:** Only add what solves observed problems. Do not duplicate content that best practices already cover.

</instructions>

## End-to-End Example

<example>
**User request:** `/create-skill brand-guidelines`

**Step 1:** Skipped -- purpose is clear from the name.

**Step 2 (Planning):** Brand guidelines are reference content (high freedom). Resources needed:
- `references/color_palette.md` -- hex codes, usage rules
- `references/typography.md` -- font families, sizes, hierarchy
- `assets/logo.png` -- brand logo file

**Step 3 (Init):**
```bash
python3 scripts/init_skill.py brand-guidelines --path skills/
```

**Step 4 (Edit):** Write SKILL.md with:
```yaml
---
name: brand-guidelines
description: "Applies brand identity standards to UI components, documents, and presentations. Use when creating user-facing output, choosing colours, or selecting typography."
license: MIT
---
```
Body references `references/color_palette.md` and `references/typography.md`. Asks user to provide the logo file for `assets/`.

**Step 5 (Validate):** Run `python3 scripts/quick_validate.py skills/brand-guidelines` -- passes.

**Step 6:** Skipped -- created from scratch for public use.

**Steps 7-9:** Run security scan, package, update marketplace.
</example>

<example>
**User request:** `/create-skill db-migrate`

**Step 1:** Skipped -- purpose clear from the name.

**Step 2 (Planning):** Database migrations are fragile, sequence-dependent operations (low freedom). Resources needed:
- `scripts/migrate.py` -- runs migrations with rollback on failure
- `references/migration_patterns.md` -- naming conventions, idempotency rules

**Step 3 (Init):**
```bash
python3 scripts/init_skill.py db-migrate --path skills/
```

**Step 4 (Edit):** Write SKILL.md with:
```yaml
---
name: db-migrate
description: "Generates and runs database migration scripts with rollback support. Use when creating schema changes, adding columns, or restructuring tables."
license: MIT
context: fork
agent: general-purpose
---
```
Body wraps the migration workflow in `<instructions>` tags with exact commands. Low freedom: each step specifies the exact script to run and the verification query to confirm success.

**Step 5 (Validate):** Run `python3 scripts/quick_validate.py skills/db-migrate` -- passes with no warnings.

**Steps 6-9:** Skip sanitization (created from scratch), run security scan, package, update marketplace.
</example>

<example>
**User request:** "The changelog skill sometimes misses merge commits. Can you improve it?"

**Step 1:** Skipped -- user described the problem.

**Step 2 (Planning):** This is an update, not a new skill. Identify the root cause: the skill's git log parsing likely filters merge commits.

**Step 3:** Skipped -- skill already exists.

**Step 4 (Edit):**
1. Read the existing SKILL.md and all reference files.
2. Locate the git log command pattern -- confirm it uses `--no-merges` flag.
3. Remove `--no-merges` and add a merge commit formatting section.
4. Update `references/commit_types.md` to include merge commit categorisation.
5. Run consistency verification: check that no other section contradicts the new merge handling.

**Step 5 (Validate):** Run `python3 scripts/quick_validate.py skills/changelog` -- passes.

**Step 10 (Iterate):** Test on a repository with merge commits. Confirm the changelog now includes them with correct formatting.
</example>
