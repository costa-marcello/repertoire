# Sources

The guidance and research behind `rules.md` and the lenses. Cite these in reports.

## Contents

1. [Anthropic and Claude Code](#anthropic-and-claude-code)
2. [Agent Skills specification](#agent-skills-specification)
3. [Security](#security)
4. [Academic papers](#academic-papers)
5. [Benchmarks and frameworks](#benchmarks-and-frameworks)
6. [How to cite](#how-to-cite)

## Anthropic and Claude Code

| Resource | URL | Used for |
|----------|-----|----------|
| Skill authoring best practices | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | Most M and m rules: description, conciseness, degrees of freedom, feedback loops, scripts, evaluations (M12), anti-patterns |
| Agent Skills overview | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | Progressive disclosure, where skills run, security |
| Claude Code skills | https://code.claude.com/docs/en/skills | Frontmatter fields, `context: fork`, substitutions, and compaction (M2, M9, m12); dynamic context injection and `${CLAUDE_SKILL_DIR}` (M11) |
| Claude Code subagents | https://code.claude.com/docs/en/sub-agents | What a forked skill's subagent can and cannot do (M2); the fresh subagents of a regression run (M12) |
| Claude Code plugins | https://code.claude.com/docs/en/plugins | How plugins ship skills to Claude Code and Cowork, the default `claude-code` target (M11) |
| Prompting best practices | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | XML tags and examples (S1, S2), emphasis (m15), reasoning extraction (M10) |
| Equipping agents for the real world with Agent Skills | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills | Design rationale for skills and progressive disclosure |

## Agent Skills specification

| Resource | URL | Used for |
|----------|-----|----------|
| Specification | https://agentskills.io/specification | Name and description limits, portable keys, script expectations (M9, M6) |

## Security

| Resource | URL |
|----------|-----|
| OWASP Top 10 for LLM applications (2025) | https://genai.owasp.org/llm-top-10/ |
| OWASP LLM prompt injection prevention cheat sheet | https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html |

## Academic papers

### Foundational

| Paper | Citation | Key finding |
|-------|----------|-------------|
| Chain-of-Thought Prompting | Wei et al., NeurIPS 2022 | Intermediate reasoning steps improve complex tasks |
| Large Language Models are Zero-Shot Reasoners | Kojima et al., NeurIPS 2022 | "Let's think step by step" improves reasoning accuracy |
| Rethinking the Role of Demonstrations | Min et al., EMNLP 2022 | Example format matters more than label correctness |
| Fantastically Ordered Prompts | Lu et al., ACL 2022 | Example order changes performance substantially |

### arXiv

| Paper | arXiv ID | Key finding |
|-------|----------|-------------|
| The Prompt Report | 2406.06608 | Catalogues 58 text prompting techniques |
| Does Prompt Formatting Have Any Impact on LLM Performance? | 2411.10541 | GPT-3.5-turbo varied by up to 40% across templates on code translation; GPT-4 was less sensitive |
| "Should I Give Up Now?" Investigating LLM Pitfalls in Software Engineering | 2411.09916 | Unhelpful responses make developers far more likely to abandon the tool |
| A Taxonomy of Prompt Defects in LLM Systems | 2509.14404 | Six defect dimensions, from specification to maintainability |
| The Few-shot Dilemma: Over-prompting Large Language Models | 2509.13196 | More examples can lower performance; a smaller chosen set can do better |
| You Don't Need Prompt Engineering Anymore: The Prompting Inversion | 2510.22251 | Elaborate prompting that helps one model can hurt a stronger one |
| Many-Shot In-Context Learning | 2404.11018 | Hundreds of examples improve some generative and discriminative tasks |

## Benchmarks and frameworks

| Resource | Location | Use |
|----------|----------|-----|
| Stanford HELM | https://crfm.stanford.edu/helm/ | Multi-metric evaluation; the source of the HELM-inspired questions |
| IFEval | arXiv:2311.07911 | Instruction-following benchmark |
| InFoBench | arXiv:2401.03601 | Decomposed requirement following |

## How to cite

Link the page and, for research, give the arXiv ID with the finding:

```markdown
**Source:** [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

**Research:** arXiv:2411.10541, prompt format changed GPT-3.5-turbo results by up to 40% on one task.
```
