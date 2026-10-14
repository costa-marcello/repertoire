<div align="center">
  <img src="assets/logo.svg" alt="Repertoire" width="80" />
  <h1>Repertoire</h1>
  <p><strong>Skills for Claude Code and Cowork</strong></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Skills](https://img.shields.io/badge/Skills-13-8B5CF6)](skills/)
  [![Context Intelligence Hooks](https://img.shields.io/badge/Context_Intelligence_Hooks-3-3B82F6)](context-intelligence-hooks/)
</div>

---

## The problem

Claude is powerful out of the box. But ask it to create a Word document with tracked changes, generate a PowerPoint deck from a topic, build a financial model that recalculates without errors, or research a topic across community and official sources, and you hit the same wall: Claude has general knowledge about these tasks but lacks the deep, step-by-step workflows that produce professional results.

You end up writing long prompts, correcting mistakes, and re-doing work. Every session starts from zero.

**Repertoire fixes this.** It gives Claude 13 specialist skills, each containing the exact workflows, decision trees, reference materials, and quality checks needed to do one job well. Instead of hoping Claude figures out the right approach, you give it a battle-tested playbook. Repertoire is built for Claude Code, and most of its skills also run in Cowork and on claude.ai (see [Where each skill runs](#where-each-skill-runs)).

## Why these skills are different

Most skills are thin wrappers around a single prompt. Repertoire skills are structured knowledge packages built to a strict quality standard:

| What makes them different | Why it matters |
|--------------------------|----------------|
| **Decision trees, not just prompts** | Each skill contains branching workflows that adapt to what you actually need. The docx skill alone has five different workflows depending on whether you are reading, creating, editing, redlining, or converting. |
| **Bundled reference materials** | Skills carry their own documentation. The frontend-design skill includes 99 UX rules, 25+ chart types, style guides by industry, and 10 tech stack references. The pptx skill bundles a 9-stage content workflow with intake forms, rubrics, and design templates. This knowledge loads on demand without bloating your context window. |
| **Enforced quality gates** | Every skill is graded by review-skill against one rule catalog built from Anthropic's skill guidance and the Agent Skills spec, with house conventions reported separately and never graded. SKILL.md files stay under 500 lines. Descriptions say what the skill does and when to use it, so Claude picks the right skill at the right time. |
| **Fork only when it helps** | A skill runs inline, where it can use your conversation and ask you questions, or in a forked subagent (`context: fork`) that works in isolation and returns only its result. review-skill checks that forked skills are self-contained tasks that never need your input or the conversation's history. |
| **Multi-agent orchestration** | The research skill dispatches 6-10 parallel subagents across Reddit, X, Hacker News, official docs, and academic papers. It then cross-references what they find. This is not a single-prompt tool. |
| **Self-improving ecosystem** | The create-skill and review-skill form a feedback loop around the same rule catalog. Create a new skill with test cases written first, review it against the catalog, fix issues automatically. The find-skills skill discovers and installs more skills from the open ecosystem. |

## Quick start

### Claude Code

```bash
# Install a single skill
npx skills add costa-marcello/repertoire -s changelog

# Install several at once
npx skills add costa-marcello/repertoire -s pdf -s docx -s xlsx

# Use them in Claude Code
/changelog
/pdf
/research
```

That is the full setup. No configuration files, no environment variables, no build step. Install and use.

### Cowork and claude.ai

Upload a skill as a zip whose top folder is the skill itself, so the archive contains `pdf/SKILL.md`, then add it as a custom skill in Claude's settings. From a clone of this repository:

```bash
cd skills && zip -r ../pdf.zip pdf                                  # macOS and Linux
Compress-Archive -Path skills/pdf -DestinationPath pdf.zip          # Windows PowerShell
```

Check the table below first: three skills need their `argument-hint` line removed before upload, and four rely on Claude Code tools.

## Where each skill runs

| Skill | Claude Code | Cowork and claude.ai |
|-------|-------------|----------------------|
| docx | Yes | Yes |
| pdf | Yes | Yes |
| pptx | Yes | Yes |
| xlsx | Yes | Yes |
| frontend-design | Yes | Yes |
| mermaid-diagrams | Yes | Yes |
| readme-md | Yes | Yes, after removing the `argument-hint` line from its SKILL.md |
| create-skill | Yes | Yes, after removing the `argument-hint` line; it runs its evals one at a time, without subagents |
| review-skill | Yes | Yes, after removing the `argument-hint` line; Auto-PR mode needs Claude Code and `gh` |
| changelog | Yes | No: it commits, tags, and pushes with git |
| research | Yes | No: it dispatches parallel subagents and calls external search APIs |
| find-skills | Yes | No: it installs skills with the `npx skills` command |
| claudia-md | Yes | No: it manages the CLAUDE.md files of a Claude Code project |

Cowork and claude.ai accept only the portable frontmatter fields (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`). Check a skill with `python skills/create-skill/scripts/quick_validate.py skills/<skill> --portable` before uploading.

---

## All 13 skills

### Documents and Data

These four skills turn Claude into a document processing engine. They handle the Office formats that most AI tools struggle with, going beyond simple text extraction into full creation, editing, and format-aware manipulation.

<table>
<tr>
<th>Skill</th>
<th>What it does</th>
<th>How to use</th>
<th>Install</th>
</tr>
<tr>
<td><strong>docx</strong></td>
<td>

Creates, edits, and analyses Word documents. Five distinct workflows cover the full lifecycle: text extraction via pandoc, raw XML access for metadata and comments, new document creation with docx-js, OOXML editing for existing files, and a professional redlining workflow for tracked changes. The redlining workflow is particularly valuable for legal and business documents, where it implements minimal, precise edits that only mark changed text rather than replacing entire paragraphs. Bundles scripts for packing and unpacking OOXML archives and guides for DOM manipulation.

</td>
<td><code>/docx</code> + describe task<br/>"extract text from contract.docx"<br/>"create a report with these sections"<br/>"redline this legal doc with tracked changes"</td>
<td><code>npx skills add costa-marcello/repertoire -s docx</code></td>
</tr>
<tr>
<td><strong>pdf</strong></td>
<td>

Extracts text and tables from PDFs, creates new documents, merges, splits, rotates, watermarks, password-protects, and fills forms. Handles scanned documents through OCR with pytesseract. Converts markdown to PDF with professional typography including Chinese font support. Covers both Python libraries (pypdf, pdfplumber, reportlab) and command-line tools (pdftotext, qpdf, pdftk). Includes advanced reference material for pypdfium2 and JavaScript pdf-lib workflows.

</td>
<td><code>/pdf</code> + describe task<br/>"extract tables from report.pdf"<br/>"merge invoice1.pdf and invoice2.pdf"<br/>"convert README.md to a styled PDF"</td>
<td><code>npx skills add costa-marcello/repertoire -s pdf</code></td>
</tr>
<tr>
<td><strong>pptx</strong></td>
<td>

Creates, edits, and analyses PowerPoint presentations. The standout feature is its content-first workflow: a 9-stage process that starts with an intake questionnaire, applies the Pyramid Principle (conclusion first, then reasons, then evidence), and scores output against a rubric requiring 75% or higher before delivery. Bundles reference files for slide templates, colour palettes, design elements, data chart orchestration, a visual guide, and a style guide. Also supports direct OOXML editing for precise slide manipulation.

</td>
<td><code>/pptx</code> + describe task<br/>"create a 10-slide deck on Q3 results"<br/>"add speaker notes to slides 3-5"<br/>"update the chart on slide 8"</td>
<td><code>npx skills add costa-marcello/repertoire -s pptx</code></td>
</tr>
<tr>
<td><strong>xlsx</strong></td>
<td>

Creates, edits, and analyses spreadsheets with a focus on getting formulas right. Enforces a zero-formula-error standard: every model must be delivered without #REF!, #DIV/0!, #VALUE!, or #NAME? errors. Follows investment banking colour conventions (blue for inputs, black for formulas, green for cross-sheet links). Requires proper Excel formulas instead of hardcoded Python calculations, so spreadsheets stay dynamic. Includes a LibreOffice-powered recalculation script and a formula verification reference for debugging.

</td>
<td><code>/xlsx</code> + describe task<br/>"create a financial model with projections"<br/>"analyse sales.xlsx and add a summary"<br/>"fix broken formulas in budget.xlsx"</td>
<td><code>npx skills add costa-marcello/repertoire -s xlsx</code></td>
</tr>
</table>

### Development

Three skills that cover releases, UI implementation, and visual documentation.

<table>
<tr>
<th>Skill</th>
<th>What it does</th>
<th>How to use</th>
<th>Install</th>
</tr>
<tr>
<td><strong>changelog</strong></td>
<td>

Creates a versioned release in one flow: gathers the commits since the last tag, writes a dated Keep a Changelog entry, then commits, tags, and pushes. Every invocation is a release. Auto-detects the next semantic version from commit types (breaking, feat, fix) or accepts an explicit one (`/changelog v2.0.0`), and stops with "No release needed" when only docs, test, ci, or chore commits landed. Translates developer commit messages into user-friendly descriptions. Runs pre-flight checks (clean working directory, branch sync, no duplicate tags) before git operations. Follows Keep a Changelog format and Conventional Commits conventions.

</td>
<td><code>/changelog</code> — release with the auto-detected version<br/><code>/changelog v2.0.0</code> — release with an explicit version<br/>Commits, tags, and pushes after pre-flight checks.</td>
<td><code>npx skills add costa-marcello/repertoire -s changelog</code></td>
</tr>
<tr>
<td><strong>frontend-design</strong></td>
<td>

Creates distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. This is not a component library. It is a design intelligence system with 99 UX rules, 25+ chart type references, style and colour guides organised by industry, typography pairing recommendations, and 10 tech stack code snippets. Every build starts with a design thinking checklist (purpose, tone, differentiator, constraints) and ends with a polish verification. Explicitly bans Inter, Roboto, purple gradients on white, and predictable layouts. Adapts to whatever framework you use (React, Vue, vanilla HTML/CSS) and respects existing UI libraries in your project.

</td>
<td><code>/frontend-design</code> + describe interface<br/>"design a dashboard for a fintech app"<br/>"build a landing page that feels premium"<br/>"improve the visual design of this component"</td>
<td><code>npx skills add costa-marcello/repertoire -s frontend-design</code></td>
</tr>
<tr>
<td><strong>mermaid-diagrams</strong></td>
<td>

Creates professional software diagrams using Mermaid syntax. Covers class diagrams, sequence diagrams, flowcharts (basic and advanced), entity-relationship diagrams, C4 architecture diagrams, state machines, git graphs, and Gantt charts. Each diagram type has its own reference file with syntax patterns and examples. Also includes theming and advanced feature references. Useful for documenting architecture, database schemas, API flows, and deployment pipelines as code.

</td>
<td><code>/mermaid-diagrams</code> + describe diagram<br/>"sequence diagram for the auth flow"<br/>"ERD for user and orders tables"<br/>"flowchart of the deployment pipeline"</td>
<td><code>npx skills add costa-marcello/repertoire -s mermaid-diagrams</code></td>
</tr>
</table>

### Research

A single skill that turns Claude into a research orchestrator: it fans out parallel subagents across community and official sources, then reports where they agree and disagree.

<table>
<tr>
<th>Skill</th>
<th>What it does</th>
<th>How to use</th>
<th>Install</th>
</tr>
<tr>
<td><strong>research</strong></td>
<td>

Dispatches 6-10 parallel subagents to research any topic from the last 30 days. Covers community sources (Reddit, X, Hacker News, Lobsters, developer forums, blogs) and official sources (documentation, academic papers, industry publications) in a single run. Produces a two-sided report with community findings, official findings, a cross-reference table showing where they agree and disagree, and real engagement statistics. Supports three depth levels (quick, default, deep) and four query types (prompting, recommendations, news, general). After research, it generates tailored prompts in whatever format the research recommends.

</td>
<td><code>/research</code> + topic<br/><code>/research best practices for RAG pipelines</code><br/><code>/research what's new with React 19</code><br/><code>/research Claude Code tips and tricks</code></td>
<td><code>npx skills add costa-marcello/repertoire -s research</code></td>
</tr>
</table>

### Meta (Skills about Skills)

Five skills that manage the files and skills around your project: creating, reviewing, and discovering skills, and keeping CLAUDE.md and README files accurate.

<table>
<tr>
<th>Skill</th>
<th>What it does</th>
<th>How to use</th>
<th>Install</th>
</tr>
<tr>
<td><strong>claudia-md</strong></td>
<td>

The complete CLAUDE.md management tool. Six modes: audit (discover and score all rule files), review (detailed quality report against research-backed criteria), improve (targeted updates with diffs), refactor (restructure using progressive disclosure), update (scan the codebase and sync CLAUDE.md with current project state, or create one from scratch), and generate (create CLAUDE.md files for subdirectories that need context). Built on the insight that rules with reasoning outperform bare rules because models generalise from "why" explanations. Bundles references for quality criteria, anti-patterns, templates, update guidelines, and real examples.

</td>
<td><code>/claudia-md</code> + mode<br/><code>/claudia-md audit</code> — scan and score rules<br/><code>/claudia-md review</code> — quality report<br/><code>/claudia-md improve</code> — apply targeted fixes<br/><code>/claudia-md refactor</code> — restructure layout<br/><code>/claudia-md update</code> — sync with codebase<br/><code>/claudia-md generate</code> — create for subdirs</td>
<td><code>npx skills add costa-marcello/repertoire -s claudia-md</code></td>
</tr>
<tr>
<td><strong>readme-md</strong></td>
<td>

Guides README creation and improvement with audience-matched templates. Identifies four project types (open source, personal, internal, config) and selects the right template for each. Handles four tasks: creating from scratch, adding sections, updating stale content, and reviewing against actual project state. Bundles the Standard README spec, the Art of README, a style guide for common prose mistakes, and section checklists by project type. Always asks what the audience needs to know before writing.

</td>
<td><code>/readme-md</code> + describe task<br/>"create a README for this project"<br/>"add a troubleshooting section"<br/>"review the README for accuracy"</td>
<td><code>npx skills add costa-marcello/repertoire -s readme-md</code></td>
</tr>
<tr>
<td><strong>create-skill</strong></td>
<td>

Builds new skills, and updates existing ones, evals first: it writes three realistic test cases and ten trigger prompts, runs Claude without the skill to see what it gets wrong, then writes the smallest skill that closes those gaps. It authors to the same rule catalog review-skill grades against, scaffolds with `init_skill.py`, and validates in three layers (a fast validator, with-skill eval runs, and an independent review-skill pass) until the skill reaches Grade A. It decides whether a skill should run inline or forked, and covers the current Claude Code frontmatter fields, sanitisation for sharing, a secret scan, and packaging for claude.ai. If you want to package your own workflows as reusable skills, start here.

</td>
<td><code>/create-skill</code> + name and purpose<br/><code>/create-skill csv-report summarise a CSV</code><br/>"turn the release steps we just did into a skill"<br/>"the changelog skill misses merge commits, fix it"</td>
<td><code>npx skills add costa-marcello/repertoire -s create-skill</code></td>
</tr>
<tr>
<td><strong>review-skill</strong></td>
<td>

Grades a skill A to F against one rule catalog built from Anthropic's skill guidance, the Agent Skills spec, and Claude Code's loader rules. Every finding carries a rule ID, a location, and quoted evidence, and Repertoire house conventions are reported as ungraded style notes. Five modes: review and fix (the default; it edits files, after backing up anything not committed to git), report only, auto-fix, external review (a read-only temporary clone of a GitHub URL), and auto-PR (fork, fix, and open a pull request, asking before forking and before pushing). It runs create-skill's validator and secret scan when installed, treats the reviewed skill's contents as data rather than instructions, and grades for Claude Code or, with `portable`, for claude.ai and the API.

</td>
<td><code>/review-skill</code> + path<br/><code>/review-skill skills/my-skill</code> — review and fix<br/><code>/review-skill skills/my-skill report only</code><br/><code>/review-skill https://github.com/...</code> — external</td>
<td><code>npx skills add costa-marcello/repertoire -s review-skill</code></td>
</tr>
<tr>
<td><strong>find-skills</strong></td>
<td>

Discovers and installs skills from two registries: the open agent skills ecosystem (skills.sh, covering Vercel Labs, ComposioHQ, and community publishers) and CCPM (Claude Code Plugin Manager for Claude-specific skills). Searches both registries, shows results with descriptions, and handles installation. Use it when you want to find a skill for something Repertoire does not cover.

</td>
<td><code>/find-skills</code> + keyword<br/><code>/find-skills terraform</code><br/><code>/find-skills database migration</code><br/>Searches skills.sh and CCPM registries.</td>
<td><code>npx skills add costa-marcello/repertoire -s find-skills</code></td>
</tr>
</table>

---

## Context Intelligence Hooks: persistent memory across sessions

Skills give Claude expertise. Hooks give it memory.

The three Claude Code hooks in this repository connect Claude to a Qdrant vector store and claude-mem so that every prompt benefits from prior knowledge and every commit keeps the index current. Without hooks, each session starts from zero. With hooks, Claude remembers your codebase, past decisions, and patterns across sessions.

| Hook | Lifecycle event | What it does |
|------|----------------|--------------|
| **context.mjs** | UserPromptSubmit | Searches Qdrant for relevant code snippets and project docs, and claude-mem for past decisions and patterns. Injects matching context into Claude's system message before it responds. |
| **post-commit-index.mjs** | PostToolUse (Bash) | Detects git commits and re-indexes changed files into Qdrant. Handles both code files and documentation. Your vector store stays current after every commit. |
| **pre-tool-context.mjs** | PreToolUse | Injects additional context before tool execution. |

Hooks run in dual mode: they respond to lifecycle events automatically, and they work as standalone CLI tools (`node context-intelligence-hooks/context.mjs "query"`) for manual searches.

**Prerequisites:** A Qdrant Cloud account (free tier works) and a Voyage AI API key for embeddings (also free tier). See [context-intelligence-hooks/README.md](context-intelligence-hooks/README.md) for full setup instructions.

---

## How skills work

```
skills/
  changelog/
    SKILL.md             # Frontmatter + prompt (the skill itself)
  pdf/
    SKILL.md
    references/          # Deep reference docs, loaded on demand
      forms.md
      advanced-features.md
    scripts/             # Helper scripts bundled with the skill
  frontend-design/
    SKILL.md
    references/
      style-guide.md     # Styles, colours, typography by industry
      ui-rules.md        # 99 UX guidelines
      chart-types.md     # 25+ chart types
      checklist.md       # Pre-delivery verification
      search-domains.md  # 10 tech stacks with code
```

Each skill lives in its own directory under `skills/`. The `SKILL.md` file contains YAML frontmatter (name, description, licence, and optional fields such as argument-hint) followed by the prompt content. Supporting materials go in `references/`, scripts in `scripts/`, and templates in `assets/`.

When you install a skill with `npx skills add`, it copies into your project's skills directory. Claude Code loads installed skills automatically and makes each one available as a slash command matching its name. In Cowork and on claude.ai, Claude picks up an uploaded skill from its description.

Some skills accept arguments directly after the slash command. For example:

```bash
/research quantum computing        # Researches quantum computing
/changelog                         # Versioned release: entry, commit, tag, push
/changelog v2.0.0                  # Same, with an explicit version
/review-skill skills/my-skill      # Review and fix a specific skill
```

The `references/` pattern is what keeps skills fast. The SKILL.md stays under 500 lines (the enforced limit), while deep reference materials load only when the skill needs them. The frontend-design skill, for example, has 99 UX rules and 25+ chart types available, but they only enter the context window when the skill reaches for them.

---

## Prerequisites

- **Claude Code** for every skill, or **Cowork or claude.ai** for the skills marked as running there
- **Node.js 18+** for `npx skills add`
- **Python 3** for the skills that bundle scripts (docx, pdf, pptx, xlsx, research, create-skill)
- For hooks: a **Qdrant Cloud** account and a **Voyage AI** API key

---

## Contributing

Contributions are welcome. To add or improve a skill:

1. Fork the repository.
2. Create a new directory under `skills/<name>/` or edit an existing one.
3. Each skill needs a `SKILL.md` with frontmatter (name, description, licence) and prompt content.
4. Supporting docs go in `references/`, scripts in `scripts/`, templates in `assets/`.
5. Run the review-skill on your changes: `/review-skill`
6. Open a pull request.

For automated validation (requires PyYAML; use `python3` instead of `python` where that is how Python is installed):

```bash
python skills/create-skill/scripts/quick_validate.py skills/<your-skill>
python skills/create-skill/scripts/security_scan.py skills/<your-skill> --verbose --no-marker
```

---

## Licence

[MIT](LICENSE)
