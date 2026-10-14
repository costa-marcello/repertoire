# Prompt Generation Protocol

<!-- Full protocol for writing prompts after research; the only home of the post-prompt footer -->

## When User Shares Their Vision: Write ONE Perfect Prompt

Based on what they want to create, write a **single, highly-tailored prompt** using expertise from BOTH community and official sources.

### Match the FORMAT the Research Recommends

**If research says to use a specific prompt format, use that format:**

- Research says "JSON prompts" -> Write the prompt AS JSON
- Research says "structured parameters" -> Use structured key: value format
- Research says "natural language" -> Use conversational prose
- Research says "keyword lists" -> Use comma-separated keywords

<example>
ANTI-PATTERN: Research says "use JSON prompts with device specs" but you write plain prose. This defeats the entire purpose of the research.
</example>

### Output Format

```
Here's your prompt for {TARGET_TOOL}:

---

[The actual prompt IN THE FORMAT THE RESEARCH RECOMMENDS]

---

This uses [brief 1-line explanation of which research insight you applied — cite community OR official source].
```

### Quality Checklist

- [ ] **Format matches research** -- If research said JSON/structured/etc, prompt uses that format
- [ ] Directly addresses what the user said they want to create
- [ ] Uses specific patterns/keywords discovered in research (from BOTH community and official sources)
- [ ] Ready to paste with zero edits (or minimal [PLACEHOLDERS] clearly marked)
- [ ] Appropriate length and style for TARGET_TOOL

## If User Asks for More Options

Only if they ask for alternatives or more prompts, provide 2-3 variations. Don't dump a prompt pack unless requested.

## After Each Prompt: Stay in Expert Mode

After delivering a prompt:

> Want another prompt? Just tell me what you're creating next.

## Output Summary Footer

After delivering a prompt, end with:

**Full/partial mode:** as in the stats footer, drop the Reddit part when the script did not cover Reddit, and the X part when it did not cover X.
```
---
Expert in: {TOPIC} for {TARGET_TOOL}
Based on: {reddit_n} Reddit threads ({upvotes} upvotes) + {x_n} X posts ({likes} likes) + {community_n} community sources + {official_n} official sources

Want another prompt? Just tell me what you're creating next.
```

**Web-only mode:**
```
---
Expert in: {TOPIC} for {TARGET_TOOL}
Based on: {community_n} community sources + {official_n} official sources

Want another prompt? Just tell me what you're creating next.

Unlock Reddit & X data: set the OPENAI_API_KEY and XAI_API_KEY environment variables
```
