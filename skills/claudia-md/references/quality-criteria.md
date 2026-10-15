# CLAUDE.md Quality Criteria

## Contents

1. [Scoring Rubric (100 points total)](#scoring-rubric-100-points-total)
2. [Rule Quality Dimensions (Quick Assessment)](#rule-quality-dimensions-quick-assessment)
3. [Assessment Process](#assessment-process)
4. [Red Flags](#red-flags)

## Scoring Rubric (100 points total)

### 1. Commands/Workflows (12 points)

**12 points**: All essential commands documented with context
- Build, test, lint, deploy commands present
- Development workflow clear
- Common operations documented

**9 points**: Most commands present, some missing context

**6 points**: Basic commands only, no workflow

**3 points**: Few commands, many missing

**0 points**: No commands documented

### 2. Architecture Clarity (12 points)

**12 points**: Clear codebase map
- Key directories explained
- Module relationships documented
- Entry points identified
- Data flow described where relevant

**9 points**: Good structure overview, minor gaps

**6 points**: Basic directory listing only

**3 points**: Vague or incomplete

**0 points**: No architecture info

### 3. Non-Obvious Patterns (10 points)

**10 points**: Gotchas and quirks captured
- Known issues documented
- Workarounds explained
- Edge cases noted
- "Why we do it this way" for unusual patterns

**7 points**: Some patterns documented

**4 points**: Minimal pattern documentation

**0 points**: No patterns or gotchas

### 4. Conciseness (8 points)

**8 points**: Dense, valuable content
- No filler or obvious info
- Each line adds value
- No redundancy with code comments

**6 points**: Mostly concise, some padding

**3 points**: Verbose in places

**0 points**: Mostly filler or restates obvious code

### 5. Currency (8 points)

**8 points**: Reflects current codebase
- Commands work as documented
- File references accurate
- Tech stack current

**6 points**: Mostly current, minor staleness

**3 points**: Several outdated references

**0 points**: Severely outdated

### 6. Content Quality (50 points)

Evaluates how well rules communicate intent and guide AI behavior effectively.

#### 6a. Reasoning Presence (15 points)

**Applies to:** Rules, Patterns, Conventions sections only. NOT to factual content (Context, Key Files, Architecture, Commands).

**15 points**: Rules and patterns explain "why" not just "what"
- Hybrid directive style: "Prefer X—it provides Y benefit"
- Rationale helps AI make judgment calls in edge cases
- Avoids both bare directives and verbose explanations

**10 points**: Most rules have reasoning, some bare directives

**5 points**: Occasional reasoning, mostly "do X" without why

**0 points**: Pure directives with no rationale

| Quality | Example |
|---------|---------|
| Bad | "Always use TypeScript" |
| Good | "Use TypeScript—catches errors at compile time and improves IDE support" |

**Do NOT penalize for missing reasoning in:**
- Context sections: "Stripe integration for subscriptions" — factual, no "why" needed
- Key Files: "`stripe.ts` - Stripe client" — file purpose is sufficient
- Architecture: Directory structure descriptions — factual
- Commands: "`pnpm test`" — executable, self-explanatory

#### 6b. Actionability (10 points)

**10 points**: Instructions are executable without interpretation
- Commands can be copy-pasted
- No vague language ("consider", "as needed", "be careful") without defaults
- Concrete steps, real paths, specific values

**7 points**: Mostly actionable, occasional vague guidance

**4 points**: Mix of concrete and vague instructions

**0 points**: Vague or theoretical ("be mindful of performance")

| Quality | Example |
|---------|---------|
| Bad | "Consider caching as needed" |
| Good | "Cache API responses >1KB for 5 min. Skip for user-specific data." |

#### 6c. Degrees of Freedom (10 points)

**10 points**: Strictness matches consequence
- Rigid rules for safety/irreversible actions (hard rules)
- Flexible guidance for style preferences
- Clear distinction between "must" vs "prefer"

**7 points**: Generally appropriate strictness

**4 points**: Over-rigid on style OR too loose on safety

**0 points**: Uniform strictness regardless of consequence

| Quality | Example |
|---------|---------|
| Bad | "ALWAYS use 2-space indentation" (rigid for style) |
| Bad | "Consider not force-pushing main" (loose for safety) |
| Good | "Prefer 2-space indent. NEVER force-push main—rewrites shared history." |

#### 6d. Options Discipline (5 points)

**5 points**: Clear recommendations with escape hatches
- Default + escape hatch pattern when alternatives exist
- Max 3 alternatives for any choice
- No buffet of options without recommendation

**3 points**: Usually has defaults, occasional option overload

**1 point**: Often presents options without guidance

**0 points**: Lists choices without recommendation

| Quality | Example |
|---------|---------|
| Bad | "For state: Redux, Zustand, Jotai, MobX, or Context" |
| Good | "Use Zustand for state. Redux if team requires it. Context for ≤3 consumers." |

#### 6e. AI-Optimized Format (10 points)

**10 points**: Structure aids AI parsing and recall
- Tables for comparisons and multi-column data
- Examples for patterns (good/bad contrasts)
- Code blocks for commands
- Scannable structure over prose paragraphs

**7 points**: Good structure, some prose walls

**4 points**: Mix of structured and unstructured

**0 points**: Dense prose, no formatting aids

| Quality | Example |
|---------|---------|
| Bad | "When testing, prefer integration tests over unit tests because they have higher ROI, but use E2E sparingly for critical paths only." |
| Good | Table with Test Type / When to Use / Example columns |

---

## Rule Quality Dimensions (Quick Assessment)

For rapid rule-by-rule review. **Only evaluate rules/patterns sections**, not factual content.

| Dimension | Score | Criteria | Applies To |
|-----------|-------|----------|------------|
| **Reasoning** | 0-3 | 0=no why, 1=some, 2=most, 3=all have reasoning | Rules, Patterns |
| **Specificity** | 0-3 | 0=vague, 1=mixed, 2=mostly specific, 3=all actionable | Rules, Patterns, Gotchas |
| **Positive framing** | 0-3 | 0=all negative, 1=mostly negative, 2=mixed, 3=mostly positive | Rules only |
| **Examples** | 0-2 | 0=none, 1=some, 2=good/bad examples | Complex rules |
| **Structure** | 0-2 | 0=prose wall, 1=basic headers, 2=tables/hierarchy | All content |
| **Conflicts** | 0/-3 | 0=none, -1 per conflict found | All content |

**"Patterns" scope clarification:**
- `.claude/rules/*.md` files: Patterns sections need reasoning
- Generated subdirectory CLAUDE.md: Patterns sections need reasoning
- Root CLAUDE.md: Patterns/Conventions sections need reasoning
- Hand-crafted subdirectory CLAUDE.md: Conventions sections should have reasoning

**Total: /13** (with potential negatives for conflicts)

| Score | Quality Rating |
|-------|----------------|
| 11-13 | Excellent — minor suggestions only |
| 8-10 | Good — some improvements needed |
| 5-7 | Fair — significant improvements recommended |
| <5 | Poor — major restructuring needed |

---

## Assessment Process

1. Read the CLAUDE.md file completely
2. Cross-reference with actual codebase:
   - Check that each documented command exists in `package.json` scripts, the Makefile, `pyproject.toml`, or the matching config. Run nothing in Audit or Review, because a command such as `npm start` can start a server or change files
   - Check if referenced files exist
   - Check that each `@path` import resolves from the file that contains it
   - Verify architecture descriptions
3. Score each criterion. In a `.claude/rules/` file or a subdirectory CLAUDE.md, mark Commands/workflows or Architecture clarity N/A when the file's scope has none, and rescale the rest to 100 (points earned / points available x 100)
4. Calculate total and assign grade
5. List specific issues found
6. Propose concrete improvements

---

## Red Flags

- Commands that would fail (wrong paths, missing deps)
- References to deleted files or directories
- `@` imports that do not resolve from the importing file, or that import a file Claude Code loads anyway (a `.claude/rules/` file, a parent CLAUDE.md)
- A file over 200 lines (the Claude Code docs' target)
- Outdated tech versions
- Copy-paste from templates without customization
- Generic advice not specific to the project
- "TODO" items never completed
- Duplicate info across multiple CLAUDE.md files
- Rules without reasoning
- Vague language without defaults
- Negative-only framing
- Conflicting instructions
