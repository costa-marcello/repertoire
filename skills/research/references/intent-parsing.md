# Intent Parsing Reference

<!-- Query type definitions, detection patterns, and variable storage for the research skill -->

## Variables to Extract

Before doing anything, parse the user's input for these five variables:

1. **TOPIC**: What they want to learn about
2. **TARGET_TOOL** (if specified): Where they'll use the prompts (e.g., "Nano Banana Pro", "Midjourney")
3. **QUERY_TYPE**: One of the four types below
4. **DEPTH**: Controls the subagent count via flags
5. **MODEL_CHOICE** (if specified): A model or effort level the user names for the agents

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

- `[topic] for [tool]` -> "web mockups for Nano Banana Pro" -> TOOL IS SPECIFIED
- `[topic] prompts for [tool]` -> "UI design prompts for Midjourney" -> TOOL IS SPECIFIED
- Just `[topic]` -> "iOS design mockups" -> TOOL NOT SPECIFIED, that's OK
- "best [topic]" or "top [topic]" -> QUERY_TYPE = RECOMMENDATIONS

## Variable Storage

Store as: `TOPIC`, `TARGET_TOOL` (or "unknown"), `QUERY_TYPE`, `DEPTH`, `MODEL_CHOICE` (or "none").

If the tool is specified, use it. If not, run the research first; the invitation after the report decides whether to ask for one (see "Invitation" in `output-format.md`).
