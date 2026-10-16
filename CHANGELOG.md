# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed
- The research skill's community agents now cover social posts and more communities. C2 searches Reddit and forums, including product user communities such as HubSpot Community and Spiceworks. C3 searches X, Bluesky, Threads and LinkedIn. C4 covers buyer reviews (TrustRadius, Gartner Peer Insights, G2, Capterra) and YouTube, and C5 covers non-English communities (Habr, Qiita, V2EX). X needs no API key: Parallel Search and Keenable results carry the text of public posts. LinkedIn posts and articles come through Keenable, because Parallel Search's LinkedIn filter returns other sites. For sales, marketing, CRM and market topics, the agents swap tech sources for sales communities (Pavilion, Revenue Operations Alliance, sales subreddits), business press and analysts (Harvard Business Review, Gartner, Forrester, diginomica, ComputerWeekly) and institutions (national statistics, regulators, professional bodies such as the Institute of Sales Professionals). The report footer no longer shows the "Unlock Reddit & X data" hint
- The research skill now picks a model and effort level for each subagent instead of copying your session's: Sonnet 5.5 at medium for `--quick`, at high by default and at xhigh for `--deep`, where Opus 5.5 at xhigh then writes the report from the subagents' findings. A model you name in the request ("run all the agents on Opus") takes precedence, except Fable: the skill runs Opus 5.5 instead, which matches Fable on research for less than half the price. Each subagent says which model it ran on, and the report footer gains a `Models` line. Before, a session at max effort ran every subagent on Opus at max. The research skill's `references/model-routing.md` explains each setting and the benchmarks behind it

## [0.12.0] - 2026-10-15

### Added
- Added Parallel Search and Keenable to the research skill: it searches with Parallel Search first, then Keenable, then Claude's built-in web search, tests a backend with one call before choosing it, retries once after a rate limit and moves a subagent to the next backend when the limit persists or the credits run out, and names the backend in the report footer. Both are remote connectors you add yourself (Customize > Connectors in Claude and Cowork, or `claude mcp add` in Claude Code), so they also work in cloud sessions, and unlike the built-in search they can read Reddit threads. The research skill's `references/search-setup.md` explains how to connect them and their limits

### Changed
- **BREAKING**: Removed the `repertoire-searxng` plugin and the research skill's SearXNG support, because Cowork could not install the plugin. If you installed it, uninstall it from `/plugin` in Claude Code or from Customize > Plugins in Cowork, and connect Parallel Search or Keenable instead; without either, research uses the built-in web search
- create-skill now tells authors to add a "skill folder" step to every skill that bundles files, and review-skill notes a missing one as advisory under M11, with no grade change
- create-skill's marketplace guide no longer suggests a `strict: false` entry for a second plugin next to a `"./"` plugin: claude.ai and Cowork don't offer such an entry when it only defines an MCP server. It suggests a separate repository, or a folder for each plugin instead of `"./"`

### Fixed
- Fixed skills failing in Cowork when a skill is loaded before the chat moves to a cloud session (for example `/repertoire:research` as the first message): the session hands the skill a folder that doesn't exist, so it couldn't run its scripts or read its references. Every Repertoire skill now finds its own folder, and says what it skipped when it can't
- Fixed review-skill not finding create-skill's validator, and create-skill not finding review-skill, in those sessions

## [0.11.0] - 2026-10-15

### Changed
- **BREAKING**: The `repertoire-searxng` plugin no longer has a SearXNG URL setting and always connects to `http://localhost:8888`, because desktop Cowork drops a plugin MCP server that uses plugin settings; in Claude Code, a SearXNG at another address works through the user-scope `mcp-searxng` server from the research skill's SearXNG guide, while Cowork needs SearXNG at `http://localhost:8888`
- The SearXNG docs now say plainly that the plugin starts only the connector, and that SearXNG itself must already be running

### Fixed
- Fixed desktop Cowork not starting the SearXNG server: it dropped the server because the server used the URL setting
- Fixed Cowork listing a `csv-summary` skill: it was a create-skill test fixture, and create-skill's test fixtures are now generated when the tests run

## [0.10.1] - 2026-10-15

### Changed
- The `repertoire-searxng` plugin is now defined in its marketplace entry instead of its own `plugin.json`; Claude Code users who installed it pick this up with `/plugin marketplace update repertoire`, and the saved SearXNG URL is kept
- create-skill's marketplace guide warns that a `"./"` plugin must not contain another `.claude-plugin/plugin.json`

### Fixed
- Fixed Cowork and claude.ai listing only `repertoire-searxng` from the marketplace: the main `repertoire` plugin was skipped because its folder, the whole repository, held two other `plugin.json` files (the SearXNG plugin's and a create-skill test fixture's, which is now generated when the test runs)
- Fixed the SearXNG docs telling desktop Cowork users to change `searxng_url`; Cowork doesn't ask for plugin settings and always uses `http://localhost:8888`

## [0.10.0] - 2026-10-14

### Added
- Added plugin distribution: the repository is now a plugin marketplace whose `repertoire` plugin carries every skill to both Claude Code (`/plugin marketplace add costa-marcello/repertoire`, then `/plugin install repertoire@repertoire`) and Cowork (Customize > Plugins > Add marketplace), with the full Claude Code frontmatter kept in both
- Added the optional `repertoire-searxng` plugin, which connects the research skill to your own SearXNG instance through the `mcp-searxng` MCP server (desktop Cowork and Claude Code)
- Added rule M11 "Breaks in Cowork": dynamic context injection (moved from M9, now a definitive Major) and paths that reach a skill's own files through `~/.claude/skills/` are flagged by the validator, and reviews also check for steps that need a display, local services without a fallback, `claude -p`, and secrets kept only in a home-folder dotfile
- Added rule M12 "Fails its own evals" and review-skill's `regression` mode, which re-runs a skill's eval cases in isolated subagents (when you ask, after Auto-Fix in your own repository, or from create-skill's update flow) and reports any case that fails twice
- Added `scripts/link_user_skills.py`, which links a local checkout into Claude Code as a plugin through a directory junction, so edits apply without reinstalling and without admin rights
- Added eval cases and trigger queries to every skill, and plugin tests (`python -B -m unittest discover -s tests/plugin`)
- Added SearXNG-first search to the research skill: it finds either the Claude Code `searxng` server or the plugin's, checks that the instance answers, falls back to the built-in web search, and names the backend it used in the report

### Changed
- **BREAKING**: Plugin installs run skills as `/repertoire:<skill>`, for example `/repertoire:changelog`; `npx skills add costa-marcello/repertoire -s <skill>` still installs a single skill under its bare name
- **BREAKING**: Removed the docx, pdf, pptx, and xlsx skills; use Anthropic's versions, which are built in to Cowork and come to Claude Code with a claude.ai sign-in or the `document-skills` plugin
- **BREAKING**: Removed the context intelligence hooks (`context-intelligence-hooks/`, the Qdrant and Voyage hooks)
- **BREAKING**: Removed review-skill's External Review and Auto-PR modes; review-skill now reviews and fixes skills in your own repository
- **BREAKING**: Renamed the project from skillkit to Repertoire (GitHub redirects the old repository URL); single skills install with `npx skills add costa-marcello/repertoire -s <skill>`
- Redefined the default review target `claude-code` as Claude Code and Cowork; `portable` now covers only single-skill uploads to claude.ai and the API, and `package_skill.py` validates against it
- Rewrote the README around the plugin: install steps for Claude Code and Cowork, optional SearXNG search, and local development through the link script
- create-skill writes new skills into `skills/` in a plugin repository and into the connected folder in Cowork, adds a Cowork check to validation, and asks review-skill for a regression run after updating an existing skill
- review-skill adds a Cowork lens to every review and finds create-skill's validator inside the plugin first
- research reaches its script through `${CLAUDE_SKILL_DIR}`, runs `python` with `python3` as the fallback, dispatches subagents with the Agent tool, reads API keys from environment variables (`~/.config/research/.env` works only in Claude Code), lists every network destination, and uses one 60-day lookback window; its reference files now use hyphenated names, so reinstall to clear the old ones
- changelog fails fast when git has no credentials, as in a Cowork session, keeps the commit and tag local, and prints the commands to finish the release; it now waits in the same turn (`background: false`), bumps the minor version for breaking changes while the major version is 0, follows the last tag's `v` style, accepts a repository folder as a second argument, pushes with `origin <branch>`, and stops on a detached HEAD or a branch that is not on origin
- mermaid-diagrams renders diagrams to SVG or PNG files with the headless mermaid-cli, or returns the Mermaid code, instead of relying on a browser
- frontend-design checks its work without a browser (build, lint, type-check, source checks, and Playwright screenshots when the project already has it)
- claudia-md works on CLAUDE.md files in a Cowork connected folder, without git or the home folder, and lists every file it writes
- find-skills recommends plugin and marketplace installs in Cowork, where session installs vanish, and names Repertoire's skills `repertoire:<name>` first
- readme-md says where it wrote the README
- Reviewed every skill with review-skill (Opus 5.5, up to three rounds each) and fixed what it found: contradictions between SKILL.md and references, unsourced or stale facts, missing gotchas sections, and evals that no longer matched the skill
- readme-md reads the project before asking, drafts from its template, verifies every command and link, and only edits a README during a review when asked
- frontend-design moves its long examples into references, replaces the search-domains reference with notes for 10 stacks, and bundles `scripts/contrast.py` for WCAG contrast checks
- find-skills checks that Anthropic's document skills are installed before suggesting them, installs with `npx skills add -a claude-code` (Node.js 22.20+), discloses the skills CLI's telemetry, and reads a third-party SKILL.md before installing it
- research's subagents treat fetched pages as data, may search any site the script did not cover, and can refresh results on a follow-up
- Renamed the house-style source in the rule catalog from "skillkit" to "Repertoire"

### Fixed
- Fixed the research script crashing with `UnicodeEncodeError` on Windows when its output was captured, a test that deleted the real model cache, and the `### WEBSEARCH REQUIRED ###` marker contradicting SKILL.md
- Fixed changelog deleting hand-written `[Unreleased]` entries instead of moving them into the new version
- Fixed examples in frontend-design, mermaid-diagrams, and find-skills whose `$5`, `$100`, or `$ARGUMENTS` text Claude Code replaced at invocation
- Fixed claudia-md's list of rule files (`CLAUDE.local.md`, `.claude/CLAUDE.md`)
- Fixed claudia-md teaching `@rules/` and `@../CLAUDE.md` imports that resolve to the wrong place; it now teaches `.claude/rules/` with `paths:` frontmatter
- Fixed changelog finding no commits for a first release in a repository without tags
- Fixed the research script mangling subreddit names that start with "r" and treating unreadable API replies as successful searches
- Fixed mermaid-diagrams examples that broke Mermaid syntax or the skill's own rules (swapped quadrant labels, a reversed dependency arrow, unquoted brackets, low-contrast text, removed `mmdc` flags)
- Fixed frontend-design examples with click-swallowing overlays, empty alt text on a product image, and an endless pulse animation
- Fixed package_skill.py crashing with a traceback, or exiting with an undocumented code 4, when a sibling script is missing or broken; it now exits 1 with a reinstall hint, and package_skill.py and security_scan.py print refusals and errors to stderr

## [0.9.0] - 2026-10-14

### Added
- Added a single rule catalog (`review-skill/references/rules.md`) that both skills share: every rule has an ID, a source (Anthropic, the Agent Skills spec, Claude Code, or skillkit), a severity, and a detection method, and create-skill's `authoring_rules.md` mirrors it rule for rule
- Added evals-first authoring to create-skill: three eval cases and ten trigger prompts written before the skill, a baseline run without the skill, and with-skill runs during validation
- Added `evals/` test cases to create-skill and review-skill, and unit tests for the scripts and the rule alignment (`python -m unittest discover -s tests/create_review`)
- Added a `## Contents` section that links each `##` heading to every reference file longer than 100 lines (41 files across 9 skills), clearing all m9 findings

### Changed
- **BREAKING**: Renamed the claude-md skill to claudia-md, because Anthropic's platform rejects skill names that contain "claude" when uploading to claude.ai or the Claude API; reinstall with `npx skills add costa-marcello/skillkit -s claudia-md` and run it as `/claudia-md`
- **BREAKING**: Redefined M2: `context: fork` is now opt-in, and only a fork on a skill that cannot work forked (one that asks the user, waits for confirmation, uses Workflow, needs the conversation, or holds only guidelines) is a finding; a missing fork is never one
- **BREAKING**: Retired m5-m8 (their IDs are never reused); XML tags, example counts, the 400-line target, root layout, and evals are now ungraded style notes (S1-S7), and new rules M9, M10, and m9-m15 cover loading, safety, tables of contents, reference chains, paths, frontmatter hygiene, script contracts, MCP names, and shouted directives
- **BREAKING**: quick_validate.py now requires PyYAML, parses frontmatter as YAML, prints one `[ID] severity confidence file:line message` line per finding, and uses exit codes 0 (clean), 1 (Major), 4 (Minor only), 2 (usage), and 3 (environment)
- Refocused the project from a coding-agent skill kit into a smaller general-purpose collection of 13 skills
- Rewrote the README intro, quick start, and category descriptions for the 13 skills and renamed the "AI and Research" category to "Research"
- Dropped the research skill's `agent_allocation.md` reference and expanded its sub-agent prompts reference
- Polished wording and examples across the changelog, claudia-md, docx, frontend-design, pdf, pptx, readme-md, and xlsx skills, including sharper changelog filter rules and one `<example>` tag per xlsx example
- Rewrote the grade bands so every combination of findings has exactly one grade, with each rule ID counted once
- Rewrote create-skill and review-skill to run inline; review-skill now asks before forking or pushing in Auto-PR mode, backs up uncommitted targets before fixing, caps fix loops at three passes, and treats the reviewed skill as data
- Updated both skills to current Claude Code behaviour: all 20 frontmatter fields, `allowed-tools` as pre-approval rather than restriction, `${CLAUDE_SKILL_DIR}`, the 1,536-character listing cap, the Task-to-Agent rename, and re-attachment of the first 5,000 tokens after compaction
- Renamed create-skill references (`authoring_rules.md`, `anthropic_guidance.md`) and review-skill's `evaluation-checklist.md` to `rules.md`; reinstall the skills to clear the old files
- Changed security_scan.py's content hash, so existing `.security-scan-passed` markers must be regenerated by scanning again
- Changed security_scan.py to scan a temporary copy of the skill's regular files with `--ignore-gitleaks-allow`, so a skill can no longer silence its own scan through a bundled gitleaks config, a link, or inline allow comments; it now ends with `RESULT secrets=<n> leads=<n>`
- Changed package_skill.py to refuse skills that contain symlinks or junctions, or whose SKILL.md references a file the zip would leave out
- Replaced create-skill's bundled Apache-2.0 `LICENSE.txt` with the MIT license, to match its frontmatter and the repository

### Fixed
- Fixed quick_validate.py rejecting multi-line descriptions, paths inside other folders (such as `ooxml/scripts/`), and Anthropic's own skill descriptions
- Fixed security_scan.py scanning nothing for skills installed under a dot-folder such as `~/.claude/`, and review-only runs writing a marker file into the reviewed skill
- Fixed package_skill.py zipping `__pycache__`, the scan marker, and evals
- Fixed all four scripts crashing on Windows when output is piped, and documented running `python`, with `python3` only where `python` is not on the path
- Fixed pptx's `inventory.py` and `rearrange.py` silently swallowing errors (M6): they now catch specific exceptions and print an actionable warning on stderr before falling back to the same defaults
- Fixed quick_validate.py missing M2 pauses on forked skills: it now catches "ask user" without an article, "user approval", "after user approval", questionnaires ("Ask all 10 questions"), and choice prompts such as "[All / Select / Cancel]", reports pauses in references that SKILL.md sends Claude to as a step (pptx's intake questionnaire), and prints a `check` lead for pauses in other linked references
- Fixed M2 across the kit by removing `context: fork` (and any `agent` key) from nine skills that cannot work forked: find-skills and readme-md ask the user, claudia-md waits for approval, pptx runs an intake questionnaire, and docx, frontend-design, mermaid-diagrams, pdf, and xlsx are guidelines or toolkits whose task comes from the conversation. changelog stays forked
- Fixed the README's changelog description, which still listed the push and update modes removed in 0.7.0, a broken Contents link in pptx's content-workflow WORKFLOW.md, and pptx warnings that did not name the slide or layout

### Removed
- **BREAKING**: Removed 10 skills that fall outside the new scope: ci-cd, smart-merge, shadcn-ui, debug, review-code, codex, gemini, ultrathink, cc-hooks, and production-audit
- Removed review-skill's marketplace template; marketplace updates live in create-skill's `marketplace_update.md`

## [0.8.0] - 2026-02-13

### Added
- Added Update mode to claude-md skill that scans the codebase and syncs CLAUDE.md with current project state

### Removed
- Removed 9 non-execution reference files across skills (changelogs, version history, research background, development test cases, internal tracking)

## [0.7.0] - 2026-02-13

### Added
- Added review-code skill for PR-level code review with SOLID, security, and quality checks graded P0-P3

### Changed
- Rewrote changelog skill as single-flow release tool, removing three-mode branching that caused mode-skipping failures

## [0.6.1] - 2026-02-13

### Changed
- Restructured changelog skill into self-contained mode flows, eliminating cross-reference jumps that caused mode skipping
- Improved production-audit skill to Grade A with consistent checkpoint fields and corrected agent counts
- Improved review-skill to Grade A with edge-case decision examples and corrected fork signal detection
- Expanded research skill MCP tool detection from Brave-only to 10 search providers (SearXNG, Exa, Tavily, Firecrawl, and others)
- Added "How to use" column with concrete examples to all skill tables in README

### Fixed
- Fixed production-audit orchestrator fork conflict where `context: fork` silently blocked sub-agent dispatch via Task/TeamCreate
- Added definitive mechanical check to review-skill: `context: fork` combined with team/task tools now triggers M2 violation

## [0.6.0] - 2026-02-12

### Changed
- Restructured changelog skill to three-mode workflow (update, push, release) with explicit push separation
- Broadened research skill description triggers for better auto-invocation
- Updated README with revised changelog and research skill descriptions

### Fixed
- Fixed research skill unable to dispatch sub-agents by removing incorrect `context: fork` and inlining agent allocation table
- Fixed review-skill fork detection to distinguish orchestrator skills (no fork) from autonomous skills (add fork)

## [0.5.0] - 2026-02-12

### Added
- Added Debug skill with four-phase root-cause methodology, tracing references, and test pressure scenarios
- Added comprehensive reference docs for cc-hooks skill (input-output schemas, command-vs-prompt guide, tool-names list, troubleshooting, five hook templates)

### Changed
- **BREAKING**: Renamed `hooks/` to `context-intelligence-hooks/` (update paths in `.claude/settings.json`)
- Improved 11 skills to Grade A compliance (cc-hooks, claude-md, create-skill, find-skills, frontend-design, mermaid-diagrams, production-audit, readme-md, smart-merge, ultrathink)
- Hardened review-skill with pre-flight validation, post-fix re-evaluation loop, and actionable fix instructions
- Improved changelog skill examples with concrete output snippets showing exact format
- Refined review-skill references with hyphenated filenames and expanded mode descriptions
- Updated README for 22 skills (added debug and cc-hooks, removed orla3-production)

### Removed
- Removed orla3-production skill (replaced by production-audit)

### Fixed
- Fixed 8 hook defects: ERROR_PATTERNS regex, DOCS_COLLECTION default mismatch, loadMcpConfig diagnostic mode, guard file TOCTOU race, input sanitisation in searchMemory, path traversal validation, connection churn, and incomplete documentation

### Security
- Added input sanitisation to searchMemory hook function
- Strengthened path traversal validation in hooks

## [0.4.0] - 2026-02-12

### Added
- Added animation patterns reference with spring, fade, and stagger recipes to frontend-design skill
- Added UI improvement triggers to frontend-design skill for detecting enhancement opportunities
- Added design variation and convergence anti-pattern to frontend-design skill
- Added `argument-hint` and `$ARGUMENTS` support to readme-md and review-skill for direct slash command input
- Added argument usage examples to README showing how skills accept inline parameters

### Changed
- Relaxed `prefers-reduced-motion` from strict enforcement to a recommended guideline in frontend-design skill
- Standardised Inter font usage across frontend-design references for consistency
- Removed redundant `.gitignore` from frontend-design skill directory

## [0.3.0] - 2026-02-10

### Added
- Added `$ARGUMENTS` support to research skill for passing user input directly to research queries
- Added version auto-detection to changelog skill so releases no longer require a manual version number
- Added push-state detection to changelog skill to choose between Unreleased and versioned release automatically
- Added validation loop and platform-specific rendering guidance to mermaid-diagrams skill
- Added `agent` field to mermaid-diagrams skill for subagent context support
- Added install docs reference to research skill for clearer onboarding

### Changed
- Broadened README and project language from Claude Code-only to support all AI coding agents
- Hardened research skill internals with named constants, rationale comments, and debug logging
- Replaced weak verbs with direct action verbs across mermaid-diagrams reference docs
- Updated changelog skill examples and reordered automation tools to recommend git-cliff as the default
- Softened directive tone in mermaid-diagrams skill for better readability

### Fixed
- Fixed 13 Mermaid syntax errors across 10 reference files including flowchart labels, ERD constraints, and deprecated directives
- Fixed install commands across README and review-skill to use documented `-s` flag format
- Fixed missing `license` field in mermaid-diagrams SKILL.md frontmatter
- Fixed invalid YAML in research skill `argument-hint` that broke frontmatter parsing in the skill installer
- Fixed missing `license: MIT` field in 9 skills (changelog, ci-cd, codex, frontend-design, gemini, orla3-production, production-audit, research, smart-merge)
- Fixed research skill unable to dispatch parallel subagents by removing `context: fork` that blocked nested Task tool access

## [0.2.0] - 2026-02-09

### Changed
- Updated README to reflect 21 skills and added orla3-production skill entry to the skills table
- Improved changelog skill with restructured SKILL.md
- Improved docx skill with restructured SKILL.md and references
- Improved ultrathink skill with domain-specific examples
- Improved review-skill with updated research-backed criteria
- Improved research skill with refined prompt generation and references

## [0.1.0] - 2026-02-09

### Added
- Initial release with 19 skills for Claude Code
- Document and data skills: docx, pdf, pptx, xlsx
- Development skills: ci-cd, changelog, smart-merge, shadcn-ui, frontend-design, mermaid-diagrams
- AI and research skills: codex, gemini, research, ultrathink
- Meta skills: claude-md, readme-md, create-skill, review-skill, find-skills
- Production-audit skill for codebase readiness checks across six dimensions
- Orla3-production skill for project-specific production audits
- Lifecycle hooks for Qdrant vector store and claude-mem persistent context
- Logo and README with skill categories, badges, and contributing guide
- Skill symlinks under `.claude/skills` and `.agents/skills`
- `.gitattributes` to mark OOXML schemas as vendored

### Changed
- Renamed skill-creator and skill-reviewer to create-skill and review-skill
- Aligned create-skill and review-skill with task-based `context:fork` detection
- Updated codex skill model from gpt-5.2-codex to gpt-5.3-codex
- Improved gemini and shadcn-ui skills with better structure
- Improved production-audit with architecture, complexity, and deeper security checks
- Improved production-audit skill structure and conciseness
- Improved review-skill with actionable steps, examples, and self-consistency checks
- Improved pptx skill with extracted template workflow and XML tags
- Improved pdf skill with XML structure, examples, and error handling
- Improved xlsx skill with XML tags, examples, and extracted references
- Improved create-skill with reduced duplication and end-to-end workflow
- Improved claude-md skill with extracted content to references and consolidated structure
- Improved research skill with corrected agent type and tighter exception handling
- Improved find-skills with XML structure, examples, and verification step
- Improved readme-md skill with restructured templates and trimmed references
- Rewrote README with detailed skill descriptions

### Fixed
- Fixed codex skill contradictions and removed stale data
- Fixed skill-creator `$ARGUMENTS` routing and cross-file inconsistencies
- Fixed production-audit review findings: consistent labels, Grep tool syntax, architecture split
- Removed hardcoded completion percentages from production-audit skill
- Fixed script invocations and variable names after skill rename
- Fixed review-skill over-specification and deduplicated steps

[Unreleased]: https://github.com/costa-marcello/repertoire/compare/v0.12.0...HEAD
[0.12.0]: https://github.com/costa-marcello/repertoire/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/costa-marcello/repertoire/compare/v0.10.1...v0.11.0
[0.10.1]: https://github.com/costa-marcello/repertoire/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/costa-marcello/repertoire/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/costa-marcello/repertoire/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/costa-marcello/repertoire/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/costa-marcello/repertoire/compare/v0.6.1...v0.7.0
[0.6.1]: https://github.com/costa-marcello/repertoire/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/costa-marcello/repertoire/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/costa-marcello/repertoire/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/costa-marcello/repertoire/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/costa-marcello/repertoire/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/costa-marcello/repertoire/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/costa-marcello/repertoire/releases/tag/v0.1.0
