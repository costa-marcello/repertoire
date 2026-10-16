# Intent Parsing Reference

<!-- Query type definitions, detection patterns, and variable storage for the research skill -->

## Variables to Extract

Before doing anything, parse the user's input for these four variables:

1. **TOPIC**: What they want to learn about
2. **QUERY_TYPE**: One of the four types below
3. **DEPTH**: Controls the subagent count via flags
4. **MODEL_CHOICE** (if specified): A model or effort level the user names for the agents

## Query Type Definitions

| Type | Trigger Patterns | Example |
|------|-----------------|---------|
| **PROMPTING** | "X prompts", "prompting for X", "X best practices" | "photorealistic people prompts" |
| **RECOMMENDATIONS** | "best X", "top X", "what X should I use" | "best Claude Code skills" |
| **NEWS** | "what's happening with X", "X news", "latest on X" | "what's new with OpenAI" |
| **GENERAL** | Anything that doesn't match above | "how does RAG work" |

When two types match, PROMPTING wins over RECOMMENDATIONS: "best practices for React prompts" is PROMPTING, not RECOMMENDATIONS.

## Depth Flags

`--quick`, no flag (default), or `--deep`. Strip the flag from TOPIC. The same flag is passed to the script in Phase 1; the subagent count for each depth is in SKILL.md, Phase 2.

## Model Choice

Store a request to run the agents on a named model or effort level ("run all the agents on Opus", "use high effort") as MODEL_CHOICE, and strip it from TOPIC, as with the depth flag. "The user's choice wins" in `model-routing.md` says how the dispatch uses it, Fable included.

## Common Detection Patterns

- `[topic] prompts for [tool]` -> "UI design prompts for Midjourney" -> QUERY_TYPE = PROMPTING, and the tool stays in TOPIC
- "best [topic]" or "top [topic]" -> QUERY_TYPE = RECOMMENDATIONS
- A period in the request ("in the last 30 days", "since August") -> keep it as `PERIOD_DAYS` (`clarifying-questions.md` then skips the period question), and strip it from TOPIC

## Variable Storage

Store as: `TOPIC`, `QUERY_TYPE`, `DEPTH`, `MODEL_CHOICE` (or "none"). The clarify step in SKILL.md then adds `PERIOD_DAYS` and `BRIEF` from the user's answers (see `clarifying-questions.md`).
