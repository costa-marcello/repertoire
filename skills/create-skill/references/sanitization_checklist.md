# Skill Sanitization Checklist

When a skill extracted from a business project is going public, remove every business-specific detail so that the skill stays generic and reusable. Run this only after the user agrees to a sanitization pass.

## Contents

1. [Quick scan commands](#quick-scan-commands)
2. [Categories to sanitize](#categories-to-sanitize)
3. [Sanitization process](#sanitization-process)
4. [Common pitfalls](#common-pitfalls)
5. [Checklist before completion](#checklist-before-completion)

## Quick scan commands

First set the variables to the real names from the source project. Ask the user for company, product, and people names that the skill cannot know. Each variable is an extended-regex alternation, and the scans are case-insensitive unless noted.

```bash
SKILL_DIR="path/to/skill"
COMPANY="acme|acme corp|globex"          # company and department names
PRODUCT="mercury|reviewer portal"        # product names and project codenames
PEOPLE="oliver|priya|jianbin"            # real people's names
ENTITIES="REVIEW_RESULT|RISK_MODEL"      # business-specific entity and field names (case-sensitive)
HOSTS="wiki.corp|internal.example.com"   # internal hostnames and services

# Company, product, and project names
grep -rniE "$COMPANY|$PRODUCT" "$SKILL_DIR"

# People's names, as whole words only
grep -rniwE "$PEOPLE" "$SKILL_DIR"

# Business-specific entities and fields
grep -rnwE "$ENTITIES" "$SKILL_DIR"

# Internal hosts, APIs, and tools
grep -rniE "$HOSTS" "$SKILL_DIR"

# Absolute user paths and cloud-sync folders (the dot before and after Users matches either slash)
grep -rnE "/Users/|/home/|/mnt/[a-z]/Users/|[A-Za-z]:.Users.|OneDrive" "$SKILL_DIR"

# Non-ASCII text, such as Chinese phrases in an English skill (needs grep -P)
grep -rnP "[[:^ascii:]]" "$SKILL_DIR"

# Distribution markers
grep -rniE "internal[- ]only|confidential|do not distribute|proprietary" "$SKILL_DIR"
```

Generic placeholders such as `username`, `<user>`, and `your-company` are the intended replacements, so they are not scanned for.

## Categories to sanitize

### 1. Product and project names

**What to find:**
- Project codenames ("Mercury Prepared", "Project Phoenix")
- Internal product names ("Reviewer Portal", "Admin Dashboard")
- Tool names tied to one company's setup (an internal brand in front of a public product name)

**How to replace:**
- Generic terms: "the system", "the application", "the service"
- Placeholders: `<project-name>`, `<product-name>`
- Generic examples: "e-commerce platform", "user management system"

### 2. Person names

**What to find:**
- Real employee names in examples ("Oliver will handle...")
- Team member references in action items
- Author attributions that reveal identity

**How to replace:**
- Generic names: "Alice", "Bob", "the developer", "the reviewer"
- Role-based references: "the backend team", "the PM", "the designer"
- Remove author attributions, or replace them with placeholders

### 3. Entity and data model names

**What to find:**
- Business-specific entities: `REVIEW_RESULT`, `RISK_MODEL`, `INSPECTION_FACTOR`
- Domain-specific hierarchies: `Section > Area > Item > Evidence`
- Field names that reveal business logic: `risk_level`, `underwriting_status`

**How to replace:**
- Generic entities: `ORDER`, `ORDER_ITEM`, `USER`, `PRODUCT`
- Generic hierarchies: `Category > Subcategory > Item > Detail`
- Generic fields: `status`, `quantity`, `customer_name`

### 4. Folder structures and paths

**What to find:**
- Team-specific folders: `10-team-collaboration/Meeting Minutes`
- Project-specific paths: `reviewer-portal-api-design`
- Environment-specific absolute paths under a real user's home directory

**How to replace:**
- Generic paths: `project-docs/meeting-minutes`
- Placeholder paths: `<project-root>/docs/`
- The skill's own files: `${CLAUDE_SKILL_DIR}/...` (portable target: paths relative to the skill directory)

### 5. Internal terminology and jargon

**What to find:**
- Internal nicknames for systems or meetings ("the Vault", "Bluebird sync")
- Company-specific processes ("Mercury standup", "Portal review")
- Unexplained abbreviations ("MP", "RP", "UW")

**How to replace:**
- Industry-standard terms: "weekly standup", "design review"
- Expand or remove the abbreviations
- Generic process names

### 6. Language-specific content

**What to find:**
- Phrases in another language inside an English skill ("后面再说", "MVP 先不做")
- Mixed-language examples that assume a bilingual reader
- Culture-specific references

**How to replace:**
- Translate into the skill's primary language
- Use language-neutral examples
- Or support several languages explicitly, with clear labels

### 7. Business logic examples

**What to find:**
- Domain-specific workflows ("Underwriting system conflicts")
- Business rules ("Inspection Factor vs Risk Factor")
- Industry terms used without explanation

**How to replace:**
- Generic software examples ("the Note field conflicts with the Comment system")
- Universal patterns ("UserProfile vs Account naming conflict")
- If a domain term is needed, add one line of context

### 8. External service references

**What to find:**
- Internal APIs: `POST /evaluate (push to Risk Model)`
- Company-specific integrations ("Sync with the Underwriting system")
- Internal tool names ("the internal wiki", an enterprise search product by name)

**How to replace:**
- Generic services: `POST /process (send to External Service)`
- Placeholder APIs: `<external-api>/endpoint`
- Generic tool categories: "enterprise search", "knowledge base"

## Sanitization process

### Phase 1: Automated scan

Run every scan above. Save the matches to a file in the workspace, not in the skill directory, so the report is not packaged:

```bash
{
  grep -rniE "$COMPANY|$PRODUCT" "$SKILL_DIR"
  grep -rniwE "$PEOPLE" "$SKILL_DIR"
  grep -rnwE "$ENTITIES" "$SKILL_DIR"
  grep -rniE "$HOSTS" "$SKILL_DIR"
  grep -rnE "/Users/|/home/|/mnt/[a-z]/Users/|[A-Za-z]:.Users.|OneDrive" "$SKILL_DIR"
  grep -rnP "[[:^ascii:]]" "$SKILL_DIR"
  grep -rniE "internal[- ]only|confidential|do not distribute|proprietary" "$SKILL_DIR"
} > "<workspace>/sanitization_report.txt"
```

### Phase 2: Manual review

For each match:
1. Decide whether it is business-specific or generic. "Reviewer" as a role is generic; "Reviewer Portal" is not.
2. Pick the replacement from the matching category above.
3. Check that the sentence still means what it meant.
4. Grep for other references to the old name, and update them too.

### Phase 3: Verification

1. Re-run every scan. The only matches left should be ones you decided to keep, each with a reason.
2. Read the whole skill once, and check that the examples still make sense together.
3. Run create-skill's step 6 again (validation, at most 2 passes, as step 7 says), because the edits can break references or examples.
4. Ask someone unfamiliar with the original project to read the skill.

## Common pitfalls

| Pitfall | Solution |
|---------|----------|
| Over-sanitizing generic terms | Keep roles and industry terms ("reviewer", "API", "JSON", "MVP") |
| Breaking examples by removing context | Replace with an equivalent generic example |
| Leaving orphaned references | Grep for the old name after every rename |
| Inconsistent replacements | Use one replacement per original name, everywhere |
| Leaving the scan report in the skill | Write reports to the workspace |

## Checklist before completion

- [ ] No product or project codenames remain
- [ ] No real person names in examples
- [ ] No business-specific entity names
- [ ] No internal folder structures or absolute user paths
- [ ] No unexplained jargon or abbreviations
- [ ] No other-language content, unless intended
- [ ] No internal API, host, or service references
- [ ] All examples are generic and understandable without the source project
- [ ] Step 6 validation passes again after the changes
- [ ] Someone unfamiliar with the original project can follow the skill
