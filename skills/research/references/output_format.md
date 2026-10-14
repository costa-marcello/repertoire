# Output Format

## Contents

1. [Report Template](#report-template)
2. [Official Section Template](#official-section-template)
3. [Cross-Reference Table](#cross-reference-table)
4. [Stats Footer](#stats-footer)
5. [Invitation](#invitation)
6. [Post-Prompt Footer](#post-prompt-footer)

<!-- Template for the two-sided research report produced by the research skill. -->

## Report Template

```
## Research Report: {TOPIC}

### What the Community Says

[Synthesis of Reddit/X engagement data + HN + forums + community discussions]

#### Reddit & X (with engagement metrics)
[From Python script — these have real upvotes, likes, reposts]

#### Broader Community (HN, forums, blogs)
[From community sub-agents C1-C5]
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

```
---
All agents reported back!
├─ Reddit: {n} threads | {upvotes} upvotes | {comments} comments
├─ X: {n} posts | {likes} likes | {reposts} reposts
├─ Community web: {n} sources (HN, forums, blogs)
├─ Official web: {n} sources (docs, papers, reports)
├─ Agents dispatched: {total} ({C}C + {O}O)
└─ Cross-reference: {agree} aligned, {disagree} divergent, {gaps} gaps
```

**Web-only mode** (no Reddit/X API keys):
```
---
All agents reported back!
├─ Community web: {n} sources (HN, forums, blogs)
├─ Official web: {n} sources (docs, papers, reports)
├─ Agents dispatched: {total} ({C}C + {O}O)
└─ Cross-reference: {agree} aligned, {disagree} divergent, {gaps} gaps

Unlock Reddit & X data: Add API keys to ~/.config/research/.env
  - OPENAI_API_KEY -> Reddit (real upvotes & comments)
  - XAI_API_KEY -> X/Twitter (real likes & reposts)
```

## Invitation

```
---
Share your vision for what you want to create and I'll write a thoughtful prompt
you can copy-paste directly into {TARGET_TOOL}.
```

## Post-Prompt Footer

After delivering a prompt:
```
---
Expert in: {TOPIC} for {TARGET_TOOL}
Based on: {reddit_n} Reddit threads ({upvotes} upvotes) + {x_n} X posts ({likes} likes) + {community_n} community sources + {official_n} official sources

Want another prompt? Just tell me what you're creating next.
```
