# Search setup

## Contents

1. [What you get](#what-you-get)
2. [Parallel Search](#parallel-search)
3. [Keenable](#keenable)
4. [Why the built-in search comes last](#why-the-built-in-search-comes-last)
5. [Check that it works](#check-that-it-works)
6. [Troubleshooting](#troubleshooting)

## What you get

The research skill's subagents search the web with the first of these that answers:

1. **Parallel Search**, a remote MCP server at `search.parallel.ai`. It needs no account.
2. **Keenable**, a remote MCP server at `api.keenable.ai`. It works without an account, and a free account raises its limits.
3. Claude's built-in **WebSearch** and **WebFetch**, which need no setup.

Parallel Search and Keenable are optional. Both run on their providers' servers, so they work in Claude Code, in Cowork, and in cloud sessions with no linked computer. Connect one or both: if the chosen backend runs out of credits or stays rate-limited mid-run, the subagents move to the next one in the chain. The report footer's `Search backend` line says which one a run used.

Keep any API key in your own user configuration. Never put one in a repository or in a shared project file such as `.mcp.json`.

## Parallel Search

The keyless URL is `https://search.parallel.ai/mcp`.

**In Claude (claude.ai, the desktop app, and Cowork):** open Customize > Connectors > Add custom connector, name it `Parallel Search`, enter `https://search.parallel.ai/mcp`, and add it without sign-in. In a chat, check that it is on under + > Connectors. A connector on your claude.ai account also loads in Claude Code when Claude Code is signed in with that claude.ai subscription.

**In Claude Code only:**

```bash
claude mcp add --scope user --transport http parallel-search https://search.parallel.ai/mcp
```

**Tools:** `web_search` takes `objective` (the goal in plain words) and `search_queries` (2-3 short queries). `web_fetch` takes `urls` (up to 20), an optional `objective`, and `full_content` (default false). Their full names depend on how you connected the server: `mcp__parallel-search__web_search` after the command above, or `mcp__claude_ai_Parallel_Search__web_search` for a claude.ai connector named Parallel Search. The skill finds them by keyword, so any name works.

**Limits** (from docs.parallel.ai/integrations/mcp/search-mcp, checked 2026-10-15):

- Anonymous use is free. It runs in Parallel's fast mode, at lower rate limits that Parallel does not publish. Parallel uses the `session_id` each call carries for free-tier rate limiting, so the skill sends one ID per run on every call.
- One call returns at most about 25,000 characters of excerpts. Full page content can exceed the client's output limit, so the skill asks for full pages only a few at a time.
- Higher limits need a Parallel account, through `https://search.parallel.ai/mcp-oauth` or an API key. Parallel's free monthly credit for an account needs a credit card on file (parallel.ai/blog/free-tier-parallel, checked 2026-10-15), so the skill recommends the keyless URL.

## Keenable

Keenable has two URLs:

- `https://api.keenable.ai/mcp`: the keyless public tier, or your account when you send an `X-API-Key` header;
- `https://api.keenable.ai/mcp-oauth`: sign in with a Keenable account.

**In Claude (claude.ai, the desktop app, and Cowork):**

- With an account (recommended): open Customize > Connectors > Add custom connector, name it `Keenable`, enter `https://api.keenable.ai/mcp-oauth`, then Connect and sign in to Keenable.
- Without an account: Customize > Connectors, +, search for "Keenable Web Search" in the directory, and Connect. It needs no sign-in.
- On Team and Enterprise plans, an owner adds a custom connector for the organization, and each member then signs in.

**In Claude Code only:**

```bash
claude mcp add --scope user --transport http keenable https://api.keenable.ai/mcp
```

To use your account's allowance, add `--header "X-API-Key: <your key>"` to that command. Claude Code keeps the key in your user configuration.

**Tools:** `search_web_pages` takes `query`, and optionally `site`, `published_after` (a date such as `2026-08-16`, or `60d`), and `max_results` (1-50, default 10). `fetch_page_content` takes `url`, and optionally `max_chars` (default 50,000), `live` (fetch from the source instead of Keenable's index), and `prompt` (return only what an instruction asks for). Their full names depend on the route, for example `mcp__keenable__search_web_pages` after the command above.

**Limits** (from docs.keenable.ai/rate-limits and docs.keenable.ai/credits, checked 2026-10-15):

- Without an account: 1,000 requests an hour and at most 10 a second, per IP address. These requests are not metered.
- With an account (sign-in or API key): no hourly cap, at most 10 requests a second per organization, and a free allowance of 100,000 requests a month that renews every month. A search and a fetch cost one credit each. Keenable's docs do not mention a card for the free allowance. When the month's allowance runs out, requests fail with HTTP 402 until it renews or you buy credits.

## Why the built-in search comes last

WebSearch and WebFetch need no setup, so they are always there, but they cover less:

- WebSearch uses a Brave-based index and returns about 10 links and a summary per call.
- They cannot reach Reddit: searches limited to reddit.com fail with HTTP 400, and WebFetch refuses Reddit pages. x.com returns HTTP 402. In Repertoire's tests (2026-10-15), Parallel Search's `web_fetch` and Keenable's `fetch_page_content` both read reddit.com threads.
- A session can run at most 200 WebSearch calls, shared by all subagents.

## Check that it works

- **Claude Code:** `claude mcp list` shows `parallel-search` and `keenable` as connected; `/mcp` shows the same inside a session.
- **Claude and Cowork:** the connector is listed under Customize > Connectors and is on under + > Connectors in the chat.
- Run `/repertoire:research <topic> --quick` and read the footer's `Search backend` line.

## Troubleshooting

| What the footer says | Cause and fix |
|----------------------|---------------|
| `skipped Parallel Search: not connected` (or Keenable) | No tool from that server reached this session. In Claude and Cowork, check that the connector is added and on in this chat. In Claude Code, run `claude mcp list`; a claude.ai connector loads there only when Claude Code is signed in with a claude.ai subscription, not with an API key. |
| `rate-limited` | The keyless tier's limit: a rate-limit reply again after a 5-second retry, or Keenable's hourly cap. Connect the other backend too, so the subagents have a fallback. For Keenable, sign in through `/mcp-oauth` or add an API key; for Parallel, connect through `/mcp-oauth` with a Parallel account. |
| `error`, with a sign-in or HTTP 401 message | The connector lost its sign-in. Reconnect it under Customize > Connectors, or run `/mcp` in Claude Code and sign in again. Parallel's `/mcp-oauth` URL refuses anonymous requests; use `/mcp` for keyless use. |
| Keenable `out of credits` (HTTP 402) | Your account's allowance for the month is used up. It renews next month; until then, connect Keenable without the key or sign-in to use the keyless tier. |
| `WebSearch + WebFetch`, with Reddit under Gaps | Expected with the built-in search, which cannot reach Reddit. Connect Parallel Search or Keenable. |
