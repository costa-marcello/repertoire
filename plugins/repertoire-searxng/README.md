# repertoire-searxng

An opt-in companion to the `repertoire` plugin. It adds the [SearXNG](https://docs.searxng.org/) MCP server ([mcp-searxng](https://www.npmjs.com/package/mcp-searxng), pinned to 2.5.1), so the research skill can search the web through your own SearXNG instance instead of only the built-in web search.

## What it adds

One MCP server, `searxng`, started with `npx -y mcp-searxng@2.5.1`. Its tools show up as `mcp__plugin_repertoire-searxng_searxng__<tool>`:

| Tool | What it does |
|------|--------------|
| `searxng_web_search` | Runs a search on your SearXNG instance |
| `web_url_read` | Reads a web page and returns its text |
| `searxng_instance_info` | Reports the instance's settings |
| `searxng_search_suggestions` | Returns search suggestions for a query |

The plugin has no skills, hooks or scripts of its own. Its manifest is the `repertoire-searxng` entry in the repository's `.claude-plugin/marketplace.json` (`"strict": false`), so this folder holds only this README. A `.claude-plugin/` folder here would make Cowork skip the main `repertoire` plugin, whose folder is the whole repository.

## What you need

- A running SearXNG instance with the JSON output format enabled (`json` listed under `search.formats` in its `settings.yml`). Without it, every search fails. The research skill's `references/searxng-setup.md` has the Docker steps.
- Node.js 22 or later on the machine that runs the server, because the server starts through `npx` and `mcp-searxng` 2.5.1 requires Node.js 22.

## Install

In Claude Code, after adding the marketplace with `/plugin marketplace add costa-marcello/repertoire`:

```text
/plugin install repertoire-searxng@repertoire
```

In Cowork, open Customize > Plugins and add `repertoire-searxng` from the `repertoire` marketplace.

The plugin always connects to `http://localhost:8888`, a SearXNG instance on the same computer on port 8888, and has no settings: desktop Cowork drops a plugin MCP server that uses plugin settings. If your SearXNG runs somewhere else, skip this plugin and add the user-scope server from `references/searxng-setup.md`, which takes any `SEARXNG_URL`. The plugin starts only the connector; it doesn't install or run SearXNG.

## Where it works

| Where | Works? |
|-------|--------|
| Claude Code | Yes |
| Desktop Cowork | Yes |
| Cloud Cowork sessions | No: they run no local stdio MCP servers and cannot reach `localhost` on your computer |

Without the server, the research skill still runs and falls back to the built-in web search tools.

## You may not need it

If your Claude Code already has a user-scope MCP server named `searxng` (for example one added with `claude mcp add --scope user searxng ...`), skip this plugin: the research skill finds either server. Installing both starts two copies of the same server.
