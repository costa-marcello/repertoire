# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed
- Refocused the project from a coding-agent skill kit into a smaller general-purpose collection of 13 skills
- Rewrote the README intro, quick start, and category descriptions for the 13 skills and renamed the "AI and Research" category to "Research"
- Aligned create-skill with review-skill criteria by adding a review-criteria mirror reference, a two-layer validation gate before packaging, and expanded `quick_validate.py` checks for fork class, weak verbs, bare excepts, and path references
- Extended the review-skill evaluation checklist with a four-class `context: fork` taxonomy (autonomous, orchestrator, interactive, mode-style reasoning)
- Dropped the research skill's `agent_allocation.md` reference and expanded its sub-agent prompts reference
- Polished wording and examples across the changelog, claude-md, docx, frontend-design, pdf, pptx, readme-md, and xlsx skills, including sharper changelog filter rules and one `<example>` tag per xlsx example
- Replaced the smart-merge example with frontend-design in the skill naming guidance of create-skill and review-skill

### Removed
- **BREAKING**: Removed 10 skills that fall outside the new scope: ci-cd, smart-merge, shadcn-ui, debug, review-code, codex, gemini, ultrathink, cc-hooks, and production-audit

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

[Unreleased]: https://github.com/costa-marcello/skillkit/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/costa-marcello/skillkit/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/costa-marcello/skillkit/compare/v0.6.1...v0.7.0
[0.6.1]: https://github.com/costa-marcello/skillkit/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/costa-marcello/skillkit/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/costa-marcello/skillkit/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/costa-marcello/skillkit/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/costa-marcello/skillkit/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/costa-marcello/skillkit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/costa-marcello/skillkit/releases/tag/v0.1.0
