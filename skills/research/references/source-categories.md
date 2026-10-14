# Source Categories

<!-- Used when filling {FOCUS} and {QUERIES}, so subagents know WHERE to search. -->

## Community Sources (Human Discussions)

Subagents searching community sources look for real human opinions, recommendations, debates, and experience reports.

**Exclude** the sites the Python script covered (`SCRIPT_SOURCES`: reddit.com, x.com and twitter.com when both API keys work). The script has real engagement metrics (upvotes, likes, reposts) for them, so do not duplicate that work. When it covered none (web-only mode), Reddit threads are in scope for community subagents.

### Tier 1 — High Signal (has voting/engagement)
- Hacker News (news.ycombinator.com)
- Stack Overflow / Stack Exchange
- Dev.to
- Lobsters (lobste.rs)

### Tier 2 — Moderate Signal (community-curated)
- Product Hunt (producthunt.com)
- GitHub Discussions
- Discourse forums (*.discourse.org, community.* domains)
- Discord archives (indexed by search engines)
- Slack community archives (when publicly indexed)

### Tier 3 — Individual Signal (personal perspectives)
- Personal developer blogs
- YouTube comments and community posts
- User review platforms (G2, Capterra, TrustRadius)
- Medium articles by individual authors
- Substack newsletters

## Official Sources (Authoritative/Institutional)

Subagents searching official sources look for verified facts, announcements, documentation, and expert analysis.

### Tier 1 — Primary Authority
- Official project documentation and websites
- GitHub repos: READMEs, changelogs, release notes, issues
- Company engineering blogs (e.g., engineering.fb.com, blog.google)
- Government domains (.gov, .gov.uk, .europa.eu)

### Tier 2 — Peer-Reviewed / Institutional
- Academic papers (arXiv, Google Scholar, Semantic Scholar)
- Industry reports (Gartner, Forrester, McKinsey, Deloitte)
- Conference proceedings (NeurIPS, ICML, ACL, IEEE, ACM)
- Standards bodies (W3C, IETF, ISO)

### Tier 3 — Expert / Publication
- Expert blogs with established authority
- Reputable tech publications (Ars Technica, Wired, MIT Tech Review, The Verge)
- Industry-specific publications (InfoQ, The New Stack, Protocol)
- Curated newsletters by recognized experts

## Query Adaptation by QUERY_TYPE

| QUERY_TYPE | Community Focus | Official Focus |
|------------|----------------|----------------|
| RECOMMENDATIONS | "best {TOPIC}" on HN, forums, review sites; comparison threads; "what do you use for {TOPIC}" | Official feature comparisons, benchmark reports, analyst recommendations |
| NEWS | Community reactions and discussion threads; "thoughts on {TOPIC}" | Press releases, official announcements, changelog entries |
| PROMPTING | Technique sharing threads, prompt galleries, community tips | Official prompting guides, documentation, research papers on prompting |
| GENERAL | Broad discussion threads, experience reports, debates | Documentation, whitepapers, industry analysis |

## Domain Quality Signals

When evaluating sources, prefer:
- **Recency**: Content published inside the lookback window (`{DATE_FROM}` to today; the default is set once in SKILL.md, "Lookback window")
- **Specificity**: Sources that discuss the exact topic, not tangentially related
- **Engagement**: Community sources with replies/votes > silent posts
- **Authority**: Official sources from the actual project/org, not third-party summaries
