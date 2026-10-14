<div align="center">
  <img src="assets/logo.svg" alt="skillkit" width="80" />
  <h1>skillkit</h1>
  <p><strong>Skills for AI coding agents</strong></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Skills](https://img.shields.io/badge/Skills-24-8B5CF6)](skills/)
  [![Context Intelligence Hooks](https://img.shields.io/badge/Context_Intelligence_Hooks-3-3B82F6)](context-intelligence-hooks/)
</div>

---

## The problem with AI coding agents

AI coding agents are powerful out of the box. But ask one to create a Word document with tracked changes, build a CI/CD pipeline, generate a PowerPoint deck from a topic, or audit your codebase for production readiness, and you hit the same wall: the agent has general knowledge about these tasks but lacks the deep, step-by-step workflows that produce professional results.

You end up writing long prompts, correcting mistakes, and re-doing work. Every session starts from zero.

**Skillkit fixes this.** It gives your agent 24 specialist skills, each containing the exact workflows, decision trees, reference materials, and quality checks needed to do one job well. Instead of hoping the agent figures out the right approach, you give it a battle-tested playbook. Works with Claude Code, Cursor, Windsurf, and any agent that supports the skills protocol.

## Why these skills are different

Most agent skills are thin wrappers around a single prompt. Skillkit skills are structured knowledge packages built to a strict quality standard:

| What makes them different | Why it matters |
|--------------------------|----------------|
| **Decision trees, not just prompts** | Each skill contains branching workflows that adapt to what you actually need. The docx skill alone has five different workflows depending on whether you are reading, creating, editing, redlining, or converting. |
| **Bundled reference materials** | Skills carry their own documentation. The frontend-design skill includes 99 UX rules, 25+ chart types, style guides by industry, and 10 tech stack references. The pptx skill bundles a 9-stage content workflow with intake forms, rubrics, and design templates. This knowledge loads on demand without bloating your context window. |
| **Enforced quality gates** | Every skill is graded by review-skill against one rule catalog built from Anthropic's skill guidance and the Agent Skills spec, with house conventions reported separately and never graded. SKILL.md files stay under 500 lines. Descriptions say what the skill does and when to use it, so Claude picks the right skill at the right time. |
| **Fork only when it helps** | A skill runs inline, where it can use your conversation and ask you questions, or in a forked subagent (`context: fork`) that works in isolation and returns only its result. review-skill checks that forked skills are self-contained tasks that never need your input or the conversation's history. |
| **Multi-agent orchestration** | The research skill dispatches 6-10 parallel sub-agents across Reddit, X, Hacker News, official docs, and academic papers. The production-audit skill spawns 4 specialist agents to cover security, scalability, API completeness, and architecture simultaneously. These are not single-prompt tools. |
| **Self-improving ecosystem** | The create-skill and review-skill form a feedback loop around the same rule catalog. Create a new skill with test cases written first, review it against the catalog, fix issues automatically. The find-skills skill discovers and installs more skills from the open ecosystem. |

## Quick start

```bash
# Install a single skill
npx skills add costa-marcello/skillkit -s changelog

# Install several at once
npx skills add costa-marcello/skillkit -s pdf -s docx -s ci-cd

# Use it in your agent
/changelog
/pdf
/ci-cd
```

That is the full setup. No configuration files, no environment variables, no build step. Install and use.

---

## All 24 skills

### Documents and Data

These four skills turn your agent into a document processing engine. They handle the Office formats that most AI tools struggle with, going beyond simple text extraction into full creation, editing, and format-aware manipulation.

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
<td><code>npx skills add costa-marcello/skillkit -s docx</code></td>
</tr>
<tr>
<td><strong>pdf</strong></td>
<td>

Extracts text and tables from PDFs, creates new documents, merges, splits, rotates, watermarks, password-protects, and fills forms. Handles scanned documents through OCR with pytesseract. Converts markdown to PDF with professional typography including Chinese font support. Covers both Python libraries (pypdf, pdfplumber, reportlab) and command-line tools (pdftotext, qpdf, pdftk). Includes advanced reference material for pypdfium2 and JavaScript pdf-lib workflows.

</td>
<td><code>/pdf</code> + describe task<br/>"extract tables from report.pdf"<br/>"merge invoice1.pdf and invoice2.pdf"<br/>"convert README.md to a styled PDF"</td>
<td><code>npx skills add costa-marcello/skillkit -s pdf</code></td>
</tr>
<tr>
<td><strong>pptx</strong></td>
<td>

Creates, edits, and analyses PowerPoint presentations. The standout feature is its content-first workflow: a 9-stage process that starts with an intake questionnaire, applies the Pyramid Principle (conclusion first, then reasons, then evidence), and scores output against a rubric requiring 75% or higher before delivery. Bundles reference files for slide templates, colour palettes, design elements, data chart orchestration, a visual guide, and a style guide. Also supports direct OOXML editing for precise slide manipulation.

</td>
<td><code>/pptx</code> + describe task<br/>"create a 10-slide deck on Q3 results"<br/>"add speaker notes to slides 3-5"<br/>"update the chart on slide 8"</td>
<td><code>npx skills add costa-marcello/skillkit -s pptx</code></td>
</tr>
<tr>
<td><strong>xlsx</strong></td>
<td>

Creates, edits, and analyses spreadsheets with a focus on getting formulas right. Enforces a zero-formula-error standard: every model must be delivered without #REF!, #DIV/0!, #VALUE!, or #NAME? errors. Follows investment banking colour conventions (blue for inputs, black for formulas, green for cross-sheet links). Requires proper Excel formulas instead of hardcoded Python calculations, so spreadsheets stay dynamic. Includes a LibreOffice-powered recalculation script and a formula verification reference for debugging.

</td>
<td><code>/xlsx</code> + describe task<br/>"create a financial model with projections"<br/>"analyse sales.xlsx and add a summary"<br/>"fix broken formulas in budget.xlsx"</td>
<td><code>npx skills add costa-marcello/skillkit -s xlsx</code></td>
</tr>
</table>

### Development

Nine skills that cover the development lifecycle from CI/CD setup through to branch management, UI implementation, visual documentation, video, and systematic debugging.

<table>
<tr>
<th>Skill</th>
<th>What it does</th>
<th>How to use</th>
<th>Install</th>
</tr>
<tr>
<td><strong>ci-cd</strong></td>
<td>

Creates production-ready GitHub Actions workflows. Covers test workflows, matrix builds across multiple OS and language versions, Docker image builds with registry pushes, security vulnerability scanning, deployment pipelines with approval gates, and reusable workflow patterns for monorepos. Includes reference YAML templates you can use as starting points and an anti-patterns guide that flags common mistakes. Scoped to GitHub Actions only, with clear guidance on when not to use it (GitLab, CircleCI, Jenkins, or one-off deployments).

</td>
<td><code>/ci-cd</code> + describe task<br/>"test workflow with Node 18 and 20 matrix"<br/>"Docker build and push to ECR"<br/>"deployment pipeline with staging gate"</td>
<td><code>npx skills add costa-marcello/skillkit -s ci-cd</code></td>
</tr>
<tr>
<td><strong>changelog</strong></td>
<td>

Generates changelogs and manages the full release lifecycle. Three modes: `/changelog` updates the changelog and commits automatically, `/changelog push` completes the Unreleased section and pushes to remote, `/changelog release` creates a versioned entry, commits, tags, and pushes. Auto-detects the next semantic version from commit types (breaking, feat, fix) or accepts an explicit version (`/changelog release v2.0.0`). Translates developer commit messages into user-friendly descriptions. Runs pre-flight checks (clean working directory, branch sync, no duplicate tags) before git operations. Follows Keep a Changelog format and Conventional Commits conventions.

</td>
<td><code>/changelog</code> — update + commit<br/><code>/changelog push</code> — also push<br/><code>/changelog release</code> — version, tag, push<br/><code>/changelog release v2.0.0</code> — explicit ver</td>
<td><code>npx skills add costa-marcello/skillkit -s changelog</code></td>
</tr>
<tr>
<td><strong>smart-merge</strong></td>
<td>

Merges branches with comprehensive pre-merge validation. Runs tests, lint, CI checks, and reviews PR comments before merging. Supports two modes: sync (pull main into your feature branch) and PR merge (merge feature into main via GitHub PR). The key behaviour is that it never deletes your feature branch and always returns you to your working branch. A safety-first approach that prevents the "I accidentally deleted my branch" problem.

</td>
<td><code>/smart-merge</code> from feature branch<br/>Auto-detects mode: sync main into branch, or merge via PR. Runs tests and lint first. Never deletes your branch.</td>
<td><code>npx skills add costa-marcello/skillkit -s smart-merge</code></td>
</tr>
<tr>
<td><strong>shadcn-ui</strong></td>
<td>

Installs, configures, and implements shadcn/ui components with full accessibility support. Integrates with the shadcn MCP tools for component discovery and installation as the preferred workflow, falling back to CLI commands when MCP is unavailable. Covers React Hook Form with Zod validation for forms, Tailwind CSS variable theming, and advanced patterns. Bundled references include Next.js integration specifics, extended component patterns, CLI reference, configuration guide, and a learning path.

</td>
<td><code>/shadcn-ui</code> + describe task<br/>"add a data table with sorting"<br/>"login form with Zod validation"<br/>"set up custom theme with dark mode"</td>
<td><code>npx skills add costa-marcello/skillkit -s shadcn-ui</code></td>
</tr>
<tr>
<td><strong>frontend-design</strong></td>
<td>

Creates distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. This is not a component library. It is a design intelligence system with 99 UX rules, 25+ chart type references, style and colour guides organised by industry, typography pairing recommendations, and 10 tech stack code snippets. Every build starts with a design thinking checklist (purpose, tone, differentiator, constraints) and ends with a polish verification. Explicitly bans Inter, Roboto, purple gradients on white, and predictable layouts. Adapts to whatever framework you use (React, Vue, vanilla HTML/CSS) and respects existing UI libraries in your project.

</td>
<td><code>/frontend-design</code> + describe interface<br/>"design a dashboard for a fintech app"<br/>"build a landing page that feels premium"<br/>"improve the visual design of this component"</td>
<td><code>npx skills add costa-marcello/skillkit -s frontend-design</code></td>
</tr>
<tr>
<td><strong>mermaid-diagrams</strong></td>
<td>

Creates professional software diagrams using Mermaid syntax. Covers class diagrams, sequence diagrams, flowcharts (basic and advanced), entity-relationship diagrams, C4 architecture diagrams, state machines, git graphs, and Gantt charts. Each diagram type has its own reference file with syntax patterns and examples. Also includes theming and advanced feature references. Useful for documenting architecture, database schemas, API flows, and deployment pipelines as code.

</td>
<td><code>/mermaid-diagrams</code> + describe diagram<br/>"sequence diagram for the auth flow"<br/>"ERD for user and orders tables"<br/>"flowchart of the deployment pipeline"</td>
<td><code>npx skills add costa-marcello/skillkit -s mermaid-diagrams</code></td>
</tr>
<tr>
<td><strong>debug</strong></td>
<td>

Guides systematic root-cause debugging through four phases: observe (gather evidence without assumptions), hypothesise (form testable theories ranked by likelihood), test (run the cheapest decisive experiment first), and fix (address the root cause, not the symptom). Enforces an iron law: no fixes without root cause investigation first. Works for any technical issue including test failures, runtime errors, performance regressions, integration failures, and deployment problems. Prevents the common anti-pattern of random fixes that waste time and mask underlying issues.

</td>
<td><code>/debug</code> + describe symptom<br/>"tests pass locally but fail in CI"<br/>"getting a 500 on the /users endpoint"<br/>"memory usage spikes after 10 minutes"</td>
<td><code>npx skills add costa-marcello/skillkit -s debug</code></td>
</tr>
<tr>
<td><strong>review-code</strong></td>
<td>

Reviews git changes with a senior engineer lens across six dimensions: SOLID principles, engineering best practices (YAGNI, DRY, KISS, Law of Demeter, composition over inheritance, fail fast), removal candidates, security vulnerabilities, and code quality (error handling, performance, boundary conditions). Grades every finding by severity (P0 critical through P3 low) and asks before implementing any fixes. Handles large diffs by batching reviews by module. Bundles five reference checklists for SOLID smells, best practices, security risks, code quality, and removal planning.

</td>
<td><code>/review-code</code><br/>"review my changes before I push"<br/>"check this PR for security issues"<br/>"audit the diff for SOLID violations"</td>
<td><code>npx skills add costa-marcello/skillkit -s review-code</code></td>
</tr>
<tr>
<td><strong>remotion-video</strong></td>
<td>

Guides programmatic video creation with Remotion in React: compositions, sequencing, timing and easing, animations, audio and voiceover, captions and subtitles, fonts, 3D, charts, maps, and transitions, through to rendering locally, in Docker, or on Lambda. Organised as focused rule files that load only for the part of the video you are working on, with ready-made components for bar charts and text animations.

</td>
<td><code>/remotion-video</code> + describe task<br/>"animate this chart for a 30s explainer"<br/>"add captions from this SRT"<br/>"render the composition on Lambda"</td>
<td><code>npx skills add costa-marcello/skillkit -s remotion-video</code></td>
</tr>
</table>

### AI and Research

Four skills that connect your agent to other AI models and deep research workflows. These turn your agent into an orchestrator that delegates to the best tool for each job.

<table>
<tr>
<th>Skill</th>
<th>What it does</th>
<th>How to use</th>
<th>Install</th>
</tr>
<tr>
<td><strong>codex</strong></td>
<td>

Invokes OpenAI's Codex CLI for tasks where Codex excels: tricky debugging (race conditions, edge cases), security analysis and vulnerability discovery, comprehensive code reviews, and large-scale refactoring. Runs as a forked subagent so Codex operates in its own sandbox. Supports configurable reasoning effort (xhigh, high, medium, low), three sandbox modes (read-only, workspace-write, full access), and session resumption for multi-turn tasks. Suppresses thinking tokens by default for clean output.

</td>
<td><code>/codex</code> + describe task<br/>"find the race condition in payment handler"<br/>"security review the auth module"<br/>Requires Codex CLI: <code>npm i -g @openai/codex</code></td>
<td><code>npx skills add costa-marcello/skillkit -s codex</code></td>
</tr>
<tr>
<td><strong>gemini</strong></td>
<td>

Invokes Google's Gemini CLI for tasks that benefit from Gemini's 1M-token context window. Best for frontend development (Gemini 3 Pro produces high-quality UI code), code reviews spanning many files, architectural plan analysis, and processing entire codebases or documentation sets in a single pass. When the frontend-design skill is also installed, its guidelines are automatically passed to Gemini for design-driven results. Supports multiple approval modes for different execution contexts.

</td>
<td><code>/gemini</code> + describe task<br/>"review entire src/ for code quality"<br/>"build a settings page with tabs and forms"<br/>Requires Gemini CLI installed separately.</td>
<td><code>npx skills add costa-marcello/skillkit -s gemini</code></td>
</tr>
<tr>
<td><strong>research</strong></td>
<td>

Dispatches 6-10 parallel sub-agents to research any topic from the last 30 days. Covers community sources (Reddit, X, Hacker News, Lobsters, developer forums, blogs) and official sources (documentation, academic papers, industry publications) in a single run. Produces a two-sided report with community findings, official findings, a cross-reference table showing where they agree and disagree, and real engagement statistics. Supports three depth levels (quick, default, deep) and four query types (prompting, recommendations, news, general). After research, it generates tailored prompts in whatever format the research recommends.

</td>
<td><code>/research</code> + topic<br/><code>/research best practices for RAG pipelines</code><br/><code>/research what's new with React 19</code><br/><code>/research Claude Code tips and tricks</code></td>
<td><code>npx skills add costa-marcello/skillkit -s research</code></td>
</tr>
<tr>
<td><strong>ultrathink</strong></td>
<td>

Performs exhaustive multi-lens analysis through four universal perspectives: human, structural, inclusivity, and sustainability. Detects the domain of your question (software engineering, strategy, legal, ethics, research, design, data, learning, writing, problem-solving) and loads domain-specific reference material to augment the universal framework. Suspends brevity constraints so depth takes priority over conciseness. Every conclusion follows explicitly from stated premises. Use it for complex decisions where getting the reasoning chain right matters more than getting a quick answer.

</td>
<td><code>/ultrathink</code> + question<br/><code>/ultrathink should we migrate to GraphQL?</code><br/><code>/ultrathink evaluate microservices split</code><br/>Or type <code>ULTRATHINK</code> before any question.</td>
<td><code>npx skills add costa-marcello/skillkit -s ultrathink</code></td>
</tr>
</table>

### Meta (Skills about Skills)

Seven skills that manage the skillkit ecosystem itself: creating, reviewing, discovering, auditing, documenting, and automating hooks.

<table>
<tr>
<th>Skill</th>
<th>What it does</th>
<th>How to use</th>
<th>Install</th>
</tr>
<tr>
<td><strong>claude-md</strong></td>
<td>

The complete CLAUDE.md management tool. Six modes: audit (discover and score all rule files), review (detailed quality report against research-backed criteria), improve (targeted updates with diffs), refactor (restructure using progressive disclosure), update (scan the codebase and sync CLAUDE.md with current project state, or create one from scratch), and generate (create CLAUDE.md files for subdirectories that need context). Built on the insight that rules with reasoning outperform bare rules because models generalise from "why" explanations. Bundles references for quality criteria, anti-patterns, templates, update guidelines, and real examples.

</td>
<td><code>/claude-md</code> + mode<br/><code>/claude-md audit</code> — scan and score rules<br/><code>/claude-md review</code> — quality report<br/><code>/claude-md improve</code> — apply targeted fixes<br/><code>/claude-md refactor</code> — restructure layout<br/><code>/claude-md update</code> — sync with codebase<br/><code>/claude-md generate</code> — create for subdirs</td>
<td><code>npx skills add costa-marcello/skillkit -s claude-md</code></td>
</tr>
<tr>
<td><strong>readme-md</strong></td>
<td>

Guides README creation and improvement with audience-matched templates. Identifies four project types (open source, personal, internal, config) and selects the right template for each. Handles four tasks: creating from scratch, adding sections, updating stale content, and reviewing against actual project state. Bundles the Standard README spec, the Art of README, a style guide for common prose mistakes, and section checklists by project type. Always asks what the audience needs to know before writing.

</td>
<td><code>/readme-md</code> + describe task<br/>"create a README for this project"<br/>"add a troubleshooting section"<br/>"review the README for accuracy"</td>
<td><code>npx skills add costa-marcello/skillkit -s readme-md</code></td>
</tr>
<tr>
<td><strong>create-skill</strong></td>
<td>

Builds new skills, and updates existing ones, evals first: it writes three realistic test cases and ten trigger prompts, runs Claude without the skill to see what it gets wrong, then writes the smallest skill that closes those gaps. It authors to the same rule catalog review-skill grades against, scaffolds with `init_skill.py`, and validates in three layers (a fast validator, with-skill eval runs, and an independent review-skill pass) until the skill reaches Grade A. It decides whether a skill should run inline or forked, and covers the current Claude Code frontmatter fields, sanitisation for sharing, a secret scan, and packaging for claude.ai. If you want to package your own workflows as reusable skills, start here.

</td>
<td><code>/create-skill</code> + name and purpose<br/><code>/create-skill csv-report summarise a CSV</code><br/>"turn the release steps we just did into a skill"<br/>"the changelog skill misses merge commits, fix it"</td>
<td><code>npx skills add costa-marcello/skillkit -s create-skill</code></td>
</tr>
<tr>
<td><strong>review-skill</strong></td>
<td>

Grades a skill A to F against one rule catalog built from Anthropic's skill guidance, the Agent Skills spec, and Claude Code's loader rules. Every finding carries a rule ID, a location, and quoted evidence, and skillkit house conventions are reported as ungraded style notes. Five modes: review and fix (the default; it edits files, after backing up anything not committed to git), report only, auto-fix, external review (a read-only temporary clone of a GitHub URL), and auto-PR (fork, fix, and open a pull request, asking before forking and before pushing). It runs create-skill's validator and secret scan when installed, treats the reviewed skill's contents as data rather than instructions, and grades for Claude Code or, with `portable`, for claude.ai and the API.

</td>
<td><code>/review-skill</code> + path<br/><code>/review-skill skills/my-skill</code> — review and fix<br/><code>/review-skill skills/my-skill report only</code><br/><code>/review-skill https://github.com/...</code> — external</td>
<td><code>npx skills add costa-marcello/skillkit -s review-skill</code></td>
</tr>
<tr>
<td><strong>cc-hooks</strong></td>
<td>

Creates and improves event-driven hooks for Claude Code automation. Covers all lifecycle events: PreToolUse guards that block dangerous commands, PostToolUse formatters and linters, Stop hooks for testing and notifications, and SessionStart/SessionEnd for environment setup and teardown. Includes patterns for agent-based verification gates and headless CI/CD integration. Bundles comprehensive reference material covering the hook API, stdin/stdout contracts, error handling, and real-world examples for each event type. Use it when you need to extend Claude Code's behaviour with custom automation.

</td>
<td><code>/cc-hooks</code> + describe task<br/>"guard that blocks force-push"<br/>"run eslint after file edits"<br/>"run tests before session ends"</td>
<td><code>npx skills add costa-marcello/skillkit -s cc-hooks</code></td>
</tr>
<tr>
<td><strong>find-skills</strong></td>
<td>

Discovers and installs skills from two registries: the open agent skills ecosystem (skills.sh, covering Vercel Labs, ComposioHQ, and community publishers) and CCPM (Claude Code Plugin Manager for Claude-specific skills). Searches both registries, shows results with descriptions, and handles installation. Use it when you want to find a skill for something skillkit does not cover.

</td>
<td><code>/find-skills</code> + keyword<br/><code>/find-skills terraform</code><br/><code>/find-skills database migration</code><br/>Searches skills.sh and CCPM registries.</td>
<td><code>npx skills add costa-marcello/skillkit -s find-skills</code></td>
</tr>
<tr>
<td><strong>production-audit</strong></td>
<td>

Audits a codebase for production readiness across six dimensions: API completeness, frontend-backend sync, security, scalability, infrastructure, and dead code/architecture. Spawns 4 parallel audit agents, each with detailed checklists loaded from reference files. Produces a structured report with severity levels (blocker, warning, improvement), file paths, line numbers, and evidence. Findings get IDs (B-001, W-001) that work as ticket references. Adapts to any stack: the examples cover Next.js monorepos, Django REST APIs, and backend-only services. Pairs with Semgrep MCP for automated vulnerability scanning.

</td>
<td><code>/production-audit</code> — full codebase<br/><code>/production-audit src/api</code> — scoped<br/>Spawns 4 parallel agents. Report has severity levels and file refs you can use as tickets.</td>
<td><code>npx skills add costa-marcello/skillkit -s production-audit</code></td>
</tr>
</table>

---

## Context Intelligence Hooks: persistent memory across sessions

Skills give your agent expertise. Hooks give it memory.

The three hooks in this repository connect your agent to a Qdrant vector store and claude-mem so that every prompt benefits from prior knowledge and every commit keeps the index current. Without hooks, each session starts from zero. With hooks, your agent remembers your codebase, past decisions, and patterns across sessions.

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

When you install a skill with `npx skills add`, it copies into your project's skills directory. Your agent loads installed skills automatically and makes each one available as a slash command matching its name.

Some skills accept arguments directly after the slash command. For example:

```bash
/research quantum computing        # Researches quantum computing
/changelog push                    # Complete unreleased, commit, push
/changelog release                 # Versioned release, commit, tag, push
/review-skill skills/my-skill      # Review and fix a specific skill
```

The `references/` pattern is what keeps skills fast. The SKILL.md stays under 500 lines (the enforced limit), while deep reference materials load only when the skill needs them. The frontend-design skill, for example, has 99 UX rules and 25+ chart types available, but they only enter the context window when the skill reaches for them.

---

## Prerequisites

- **An AI coding agent** that supports the skills protocol (Claude Code, Cursor, Windsurf, etc.)
- **Node.js 18+**
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
