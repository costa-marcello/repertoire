# Source Categories

<!-- Used when filling {FOCUS} and {QUERIES}, so subagents know WHERE to search. -->

## Community Sources (Human Discussions)

Subagents searching community sources look for real human opinions, recommendations, debates, and experience reports.

**Exclude** the sites the Python script covered (`SCRIPT_SOURCES`: reddit.com, x.com and twitter.com when both API keys work). The script has real engagement metrics (upvotes, likes, reposts) for them, so do not duplicate that work. Every site not in `SCRIPT_SOURCES` is in scope: when `reddit.com` or `x.com` is missing from it (web-only, one key only, or a script error), those sites are in scope for the community subagents. Parallel Search and Keenable read Reddit threads, and both return the text of public X posts: Parallel's results often show view and like counts, and Keenable's also cover Bluesky and Threads (checked 16 October 2026). The built-in WebSearch and WebFetch reach neither Reddit nor X, so with that backend both go under Gaps.

Each group below is the main ground of one community agent (the roles are in SKILL.md, Phase 2).

### Tech forums (C1)
- Hacker News (news.ycombinator.com), Lobsters (lobste.rs)
- Stack Overflow and Stack Exchange
- GitHub Discussions and issues, Dev.to
- For a non-technical topic: that field's own communities (for a business topic, see [Business and sales topics](#business-and-sales-topics))

### Reddit and forums (C2)
- Reddit: the topic's subreddits
- The product's own user community, such as HubSpot Community, Dynamics Community or Salesforce Trailblazer Community: user posts, not the vendor's own blog posts
- Spiceworks: IT buyers and admins
- Discourse forums (*.discourse.org, community.* domains)
- Indie Hackers, for founder and SaaS topics (many posts promote the author's product)

### Social posts (C3)
- X, Bluesky and Threads: post text from search results, with engagement counts only where a result shows them. Never fetch an x.com page, which needs a login.
- LinkedIn: Keenable returns posts and articles (`linkedin.com/pulse`) with dates. Parallel's `site:linkedin.com` returns pages from other sites, so LinkedIn needs Keenable (checked 16 October 2026).

### Reviews and video (C4)
- TrustRadius, and Gartner Peer Insights (each review gives the reviewer's role and company size)
- G2 and Capterra, whose pages often refuse automated reads
- Product Hunt: launch reactions
- YouTube: video pages with transcript snippets, mostly hands-on reviews and tests

### Non-English communities (C5)
- Habr (Russian), Qiita (Japanese), V2EX (Chinese, skip reseller posts marked 推广)
- Regional forums for the topic's main markets

### Also useful (any agent, when a result turns up)
- Personal blogs, Medium articles and Substack newsletters
- Discord and Slack archives, when publicly indexed

## Business and Sales Topics

For a sales, marketing, CRM or market topic, the agents swap tech sources for these (all checked 16 October 2026):

- **C1 (communities):** Pavilion (joinpavilion.com) and Revenue Operations Alliance (practitioner articles by sales and RevOps leaders), and the sales subreddits (r/sales, r/salesforce, r/CRM, r/SaaS) when the backend can read Reddit and `reddit.com` is not in `SCRIPT_SOURCES`. C2 keeps the rest of Reddit
- **C2 and C4 as listed above:** product user communities (HubSpot Community, Dynamics Community) and buyer reviews (TrustRadius, Gartner Peer Insights) matter most here. At `--quick`, where C4 does not run, C2 searches TrustRadius and Gartner Peer Insights too
- **O2 (publications and analysts):** Harvard Business Review, Gartner's newsroom (survey-based press releases), Forrester's blogs, diginomica and ComputerWeekly (enterprise software and UK coverage). Vendor research reports, such as a CRM vendor's "state of sales" survey, count as industry reports from an interested party
- **O4 (institutions):** national statistics (in the UK, ONS business surveys), regulators (in the UK, the ICO on PECR and GDPR for outreach) and professional bodies (in the UK, the Institute of Sales Professionals)

## Official Sources (Authoritative/Institutional)

Subagents searching official sources look for verified facts, announcements, documentation, and expert analysis.

### Primary authority
- Official project documentation and websites
- GitHub repos: READMEs, changelogs, release notes, issues
- Company engineering blogs (e.g., engineering.fb.com, blog.google), and vendor blogs hosted on community sites (e.g., Microsoft Tech Community)
- Government domains (.gov, .gov.uk, .europa.eu)

### Peer-reviewed / institutional
- Academic papers (arXiv, Google Scholar, Semantic Scholar)
- Industry reports (Gartner, Forrester, McKinsey, Deloitte)
- Conference proceedings (NeurIPS, ICML, ACL, IEEE, ACM)
- Standards bodies (W3C, IETF, ISO)

### Expert / publication
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
