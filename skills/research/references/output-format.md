# Output Format

## Contents

1. [Source Weighting](#source-weighting)
2. [Report Template](#report-template)
3. [Official Section Template](#official-section-template)
4. [Cross-Reference Table](#cross-reference-table)
5. [Stats Footer](#stats-footer)
6. [Invitation](#invitation)

<!-- Template for the two-sided research report produced by the research skill.
     The footer after a generated prompt lives in prompt-generation.md. -->

## Source Weighting

Phase 4 of SKILL.md weights the sources this way in the synthesis:

| Source | Weight | Why |
|--------|--------|-----|
| Reddit (from script) | HIGHEST | Real upvotes + comments = proven engagement |
| X (from script) | HIGHEST | Real likes + reposts = proven engagement |
| HN / Lobsters | HIGH | Voting system = community curation |
| Official docs | HIGH | Authoritative, primary source |
| Academic papers | HIGH | Peer-reviewed |
| Industry publications | MEDIUM | Expert but potentially biased |
| Expert blogs | MEDIUM-LOW | Individual perspective |
| Misc community | MEDIUM-LOW | Volume varies |

Reddit threads that a subagent found, because the script did not cover Reddit, lack the script's verified metrics; weight them as misc community.

## Report Template

```
## Research Report: {TOPIC}

### What the Community Says

[Synthesis of Reddit/X engagement data + HN + forums + community discussions]

#### Reddit & X (with engagement metrics)
[From Python script — these have real upvotes, likes, reposts]

#### Broader Community (HN, forums, blogs)
[From community subagents C1-C5]
```

### Community Section by QUERY_TYPE

**RECOMMENDATIONS:**
```
Most Mentioned:
1. [Name] — mentioned {n}x (r/{sub}, HN, {forum}, @{handle})
2. [Name] — mentioned {n}x (sources)
3. [Name] — mentioned {n}x (sources)
...

Notable mentions: [items with 1-2 mentions]
```

**NEWS:**
```
Key developments the community is discussing:
- [Event/news] — sentiment: [positive/mixed/negative], discussed on [sources]
- [Event/news] — sentiment: [...], discussed on [sources]

Community temperature: [overall sentiment summary]
```

**PROMPTING:**
```
Techniques the community recommends:
1. [Technique] — shared by [n] sources, example: "[brief example]"
2. [Technique] — shared by [n] sources
3. [Technique] — shared by [n] sources

Prompt format consensus: [JSON / structured / natural language / keywords]
```

**GENERAL:**
```
Key themes in community discussion:
- [Theme 1]: [2-sentence synthesis with source attribution]
- [Theme 2]: [2-sentence synthesis]
- [Theme 3]: [2-sentence synthesis]
```

## Official Section Template

```
### What the Official Sources Say

[Synthesis of docs, papers, publications, institutional reports from O1-O5]
```

**All QUERY_TYPEs:**
```
Key findings from authoritative sources:

- **[Source/Organization]**: [key finding or position] ([authority level])
- **[Source/Organization]**: [key finding] ([authority level])
- **[Source/Organization]**: [key finding] ([authority level])

Recent official changes:
- [Change/update with date and source]
```

## Cross-Reference Table

```
### Where They Agree & Disagree

| Topic | Community View | Official Position | Status |
|-------|---------------|-------------------|--------|
| [aspect 1] | [what community says] | [what officials say] | Aligned / Divergent / Gap |
| [aspect 2] | [...] | [...] | [...] |
| [aspect 3] | [...] | [...] | [...] |
```

Status definitions:
- **Aligned**: Community sentiment matches official position
- **Divergent**: Community and official sources disagree
- **Gap**: One side has information the other lacks

## Stats Footer

Use real numbers from the research. The `Search backend` line is always present: it names `SEARCH_BACKEND` from SKILL.md, the backends skipped before it, and any agent that switched to a fallback mid-run.

```
---
{AGENTS_LINE}
├─ Reddit: {n} threads | {upvotes} upvotes | {comments} comments
├─ X: {n} posts | {likes} likes | {reposts} reposts
├─ Community web: {n} sources (HN, forums, blogs)
├─ Official web: {n} sources (docs, papers, reports)
├─ Agents dispatched: {total} ({C}C + {O}O)
├─ Search backend: {SEARCH_BACKEND}
└─ Cross-reference: {agree} aligned, {disagree} divergent, {gaps} gaps
```

`{AGENTS_LINE}` is `All agents reported back!` when every agent reported, else it counts the failures, as in `7 of 8 agents reported back; 1 agent failed (C4)`.

`{SEARCH_BACKEND}` reads `<backend> (skipped <backend>: <reason>, ...; fallback: <switches, or none>)`. The `skipped` part lists each earlier backend in the chain with its reason (`not connected`, `rate-limited`, `out of credits`, or `error`), and is left out when Parallel Search answered. For example:
- `Parallel Search (fallback: none)`
- `Parallel Search (fallback: C3 and O2 switched to Keenable after rate limits)`
- `Keenable (skipped Parallel Search: not connected; fallback: none)`
- `Keenable (skipped Parallel Search: rate-limited; fallback: O2 switched to WebSearch + WebFetch)`
- `WebSearch + WebFetch (skipped Parallel Search: rate-limited, Keenable: not connected; fallback: none)`

When the run used WebSearch + WebFetch, as the backend or as any agent's fallback, add one line under the footer: `Better search, Reddit included: connect Parallel Search or Keenable, see references/search-setup.md in the research skill.`

Drop the Reddit line when the script did not cover Reddit, and the X line when it did not cover X. **Web-only mode** (no Reddit/X API keys) drops both and adds:
```
Unlock Reddit & X data: set these environment variables
  - OPENAI_API_KEY -> Reddit (real upvotes & comments)
  - XAI_API_KEY -> X/Twitter (real likes & reposts)
  (In Claude Code, ~/.config/research/.env also works; Cowork has no such file.)
```

## Invitation

Pick the invitation by `QUERY_TYPE` and `TARGET_TOOL`. Only a prompting request, or a named tool, gets a prompt offer.

**PROMPTING, or any query type with a named TARGET_TOOL:**
```
---
Share your vision for what you want to create and I'll write a thoughtful prompt
you can copy-paste directly into {TARGET_TOOL}.
```

If QUERY_TYPE is PROMPTING and TARGET_TOOL is still unknown, ask instead:
```
What tool will you use these prompts with?

Options:
1. [Most relevant tool based on research]
2. [Second most relevant tool based on research]
3. Other (tell me)
```

**RECOMMENDATIONS, NEWS, or GENERAL with TARGET_TOOL unknown:** offer follow-ups, not a prompt:
```
---
Ask me anything about {TOPIC}: I can go deeper on a finding, compare two
options side by side, or check for anything newer. If you plan to use this
with an AI tool, name it and I'll write a prompt for it.
```
