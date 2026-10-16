# Output Format

## Contents

1. [Source Weighting](#source-weighting)
2. [Report Template](#report-template)
3. [Official Section Template](#official-section-template)
4. [Cross-Reference Table](#cross-reference-table)
5. [Stats Footer](#stats-footer)
6. [Invitation](#invitation)
7. [Saving the Report](#saving-the-report)

<!-- Template for the two-sided research report produced by the research skill,
     its closing invitation, and how to save it as a file -->

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

Reddit threads and X, Bluesky, Threads or LinkedIn posts that a subagent found, because the script did not cover them, lack the script's verified metrics: weight them as misc community. Weight YouTube reviews and buyer reviews (TrustRadius, Gartner Peer Insights, G2, Capterra) as misc community too.

## Report Template

```
## Research Report: {TOPIC}

**Answer:** [two or three sentences that answer the brief's purpose: the strongest evidence and its main caveat]

### What the Community Says

[Synthesis of Reddit/X engagement data + HN + forums + community discussions]

#### Reddit & X (with engagement metrics)
[From Python script — these have real upvotes, likes, reposts]

#### Broader Community (Reddit, social posts, HN, forums, reviews, video)
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

Use real numbers from the research. The `Models` and `Search backend` lines are always present. The `Search backend` line names `SEARCH_BACKEND` from SKILL.md, the backends skipped before it, and any agent that switched to a fallback mid-run.

```
---
{AGENTS_LINE}
├─ Reddit: {n} threads | {upvotes} upvotes | {comments} comments
├─ X: {n} posts | {likes} likes | {reposts} reposts
├─ Community web: {n} sources (Reddit, social posts, HN, forums, reviews, video)
├─ Official web: {n} sources (docs, papers, reports)
├─ Agents dispatched: {total} ({C}C + {O}O)
├─ Models: {MODELS}
├─ Search backend: {SEARCH_BACKEND}
└─ Cross-reference: {agree} aligned, {disagree} divergent, {gaps} gaps
```

`{AGENTS_LINE}` is `All agents reported back!` when every agent reported, else it counts the failures, as in `7 of 8 agents reported back; 1 agent failed (C4)`.

`{MODELS}` names the model each agent reported on its "Model" line, with the effort level passed in its Agent call, then who wrote the synthesis, as set in `model-routing.md`. When a report says `not stated`, name the model passed instead. Write effort levels as the names passed (`medium`, `high`, `xhigh`), never as a number an agent's environment shows. Add `user's choice` when the user picked the setting, or `Fable asked for, Opus ran` when `MODEL_CHOICE` named Fable, and name any agent that ran on another model. For example:
- `agents Sonnet 5.5 (high); synthesis by the lead, Opus 5.5`
- `agents Sonnet 5.5 (xhigh); synthesis Opus 5.5 (xhigh)`
- `agents Opus 5.5 (medium, user's choice); synthesis by the lead, Opus 5.5`
- `agents Opus 5.5 (medium, Fable asked for, Opus ran); synthesis by the lead, Sonnet 5.5`
- `agents Sonnet 5.5 (high), except O2 on Haiku 5.5; synthesis by the lead, Sonnet 5.5`
- `agents Sonnet 5.5 (high, requested model could not be applied); synthesis by the lead, Opus 5.5`
- `the session's model for all (the Agent tool here takes no model or effort); synthesis by the lead`

`{SEARCH_BACKEND}` reads `<backend> (skipped <backend>: <reason>, ...; fallback: <switches, or none>)`. The `skipped` part lists each earlier backend in the chain with its reason (`not connected`, `rate-limited`, `out of credits`, or `error`), and is left out when Parallel Search answered. For example:
- `Parallel Search (fallback: none)`
- `Parallel Search (fallback: C3 and O2 switched to Keenable after rate limits)`
- `Keenable (skipped Parallel Search: not connected; fallback: none)`
- `Keenable (skipped Parallel Search: rate-limited; fallback: O2 switched to WebSearch + WebFetch)`
- `WebSearch + WebFetch (skipped Parallel Search: rate-limited, Keenable: not connected; fallback: none)`

When the run used WebSearch + WebFetch, as the backend or as any agent's fallback, add one line under the footer: `Better search, Reddit and X included: connect Parallel Search or Keenable, see references/search-setup.md in the research skill.`

Drop the Reddit line when the script did not cover Reddit, and the X line when it did not cover X. In web-only mode (no API keys) both lines go, and the agents' Reddit and X findings stay in the community section.

## Invitation

Every query type ends with the same invitation:
```
---
Want to go further? I can dig deeper on a finding, compare two options, or
check for anything newer on {TOPIC}. Or I can save this report as a file:
Markdown, Word, PowerPoint, Excel (the sources and the cross-reference table),
or a web page.
```

Then wait for the user. A request for a prompt, like any other follow-up, is answered from the research (see `context-memory.md`).

## Saving the Report

Write a file only in the format the user picks, and say where it went: in Cowork, the outputs folder; elsewhere, the current working folder. Name it `research-<topic slug>-<YYYY-MM-DD>` with the format's extension, adding `-2`, `-3` and so on if that name exists. Change the layout, never the findings.

| Format | How |
|--------|-----|
| Markdown | Write the report as displayed to a `.md` file |
| Word | Use the host's Word document skill (`.docx`), with the report's sections as headings |
| PowerPoint | Use the host's PowerPoint skill (`.pptx`): one slide for the answer, one per section, one for the cross-reference table |
| Excel | Use the host's spreadsheet skill (`.xlsx`): one sheet listing each source the agents reported (title, URL, date, community or official, agent, tier), one with the cross-reference table |
| Web page | Use the Artifact tool when the session has it, else write an `.html` file |

The Word, PowerPoint and Excel skills are Anthropic's document skills, which Cowork includes and Claude Code has when signed in with a claude.ai account. When the one a format needs is not available, say so and offer Markdown instead, or a `.csv` file for the Excel content.
