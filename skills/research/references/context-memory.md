# Context Memory Protocol

<!-- Context retention after the research skill completes -->

## Variables to Retain

For the rest of the conversation, remember:

- **TOPIC**: {topic}
- **TARGET_TOOL**: {tool}
- **KEY COMMUNITY PATTERNS**: {top 3-5 from community sources}
- **KEY OFFICIAL FINDINGS**: {top 3-5 from official sources}
- **CROSS-REFERENCES**: {where they agree/disagree}
- **SCRIPT DATA**: Reddit/X engagement metrics
- **SEARCH_BACKEND**: SearXNG or the WebSearch + WebFetch fallback, so a later answer can say where its sources came from

## Post-Research Behavior

After research is complete, you are now an **EXPERT** on this topic.

When the user asks follow-up questions:

- **Do not run new searches** -- you already have the research from both sides
- **Answer from what you learned** — cite community AND official sources
- **If they ask for a prompt** — write one using your combined expertise
- **If they ask a question** — answer from your research findings

Only do new research if the user explicitly asks about a DIFFERENT topic.
