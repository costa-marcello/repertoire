# SearXNG setup

## Contents

1. [What you get](#what-you-get)
2. [Run SearXNG in Docker](#run-searxng-in-docker)
3. [Check the JSON API](#check-the-json-api)
4. [Connect Claude Code](#connect-claude-code)
5. [Or install the repertoire-searxng plugin](#or-install-the-repertoire-searxng-plugin)
6. [Troubleshooting](#troubleshooting)

## What you get

The research skill's subagents search with your own SearXNG instance when one answers, and fall back to the built-in WebSearch and WebFetch tools when none does. SearXNG is optional: it adds a private metasearch engine with categories (news, science, IT) and a page reader, and the report footer says which backend a run used.

Three pieces are involved:

- a SearXNG instance with its JSON output turned on, listening on port 8888 on your computer (Docker, below, or a native install);
- the `mcp-searxng` MCP server (github.com/ihor-sokoliuk/mcp-searxng), which finds the instance through the `SEARXNG_URL` environment variable;
- one way to run that server: a user-scope server in Claude Code, or the opt-in `repertoire-searxng` plugin, which also works in desktop Cowork.

## Run SearXNG in Docker

Docker is the simplest route, and it needs Docker (Docker Desktop on Windows and macOS). A native install from source, as described in the SearXNG documentation (docs.searxng.org, "Installation"), works just as well: what matters is that `settings.yml` turns the JSON format on and the instance answers on the URL you give `SEARXNG_URL`.

1. Create a folder for the configuration, such as `~/searxng`, and put this `settings.yml` in it:

   ```yaml
   use_default_settings: true
   server:
     secret_key: "replace-with-a-random-string"
     limiter: false
   search:
     formats:
       - html
       - json
   ```

   `formats` must include `json`: `mcp-searxng` asks for `/search?format=json`, and SearXNG refuses that format unless it is listed. Make the secret with `python -c "import secrets; print(secrets.token_hex(32))"`. `limiter: false` is fine for an instance only you use.

2. Start the container. Host port 8888 maps to the container's port 8080, and the folder is mounted as `/etc/searxng`:

   ```bash
   docker run -d --name searxng --restart unless-stopped -p 8888:8080 -v "$HOME/searxng:/etc/searxng" searxng/searxng
   ```

   ```powershell
   docker run -d --name searxng --restart unless-stopped -p 8888:8080 -v "${env:USERPROFILE}\searxng:/etc/searxng" searxng/searxng
   ```

After editing `settings.yml`, run `docker restart searxng`.

## Check the JSON API

```bash
curl "http://localhost:8888/search?q=test&format=json"
```

A JSON reply with a `results` list means the instance is ready. In Windows PowerShell, type `curl.exe`, because `curl` there is an alias for `Invoke-WebRequest`.

## Connect Claude Code

Add `mcp-searxng` once, for all your projects (user scope). It needs Node.js 22 or later. The version is pinned to 2.5.1, the release this skill was tested with; check the project's releases before moving to a newer one.

```bash
claude mcp add --scope user searxng -e SEARXNG_URL=http://localhost:8888 -- npx -y mcp-searxng@2.5.1
```

If the server fails to connect on native Windows, wrap `npx` in `cmd /c`:

```powershell
claude mcp add --scope user searxng -e SEARXNG_URL=http://localhost:8888 -- cmd /c npx -y mcp-searxng@2.5.1
```

Run `claude mcp list` to see that `searxng` connects. Its tools are `mcp__searxng__searxng_web_search`, `mcp__searxng__web_url_read`, `mcp__searxng__searxng_instance_info` and `mcp__searxng__searxng_search_suggestions`.

## Or install the repertoire-searxng plugin

The Repertoire marketplace has an opt-in plugin, `repertoire-searxng`, that runs the same server (`mcp-searxng@2.5.1`). It has one setting, `searxng_url`, which defaults to `http://localhost:8888`. Its tools carry the plugin prefix, for example `mcp__plugin_repertoire-searxng_searxng__searxng_web_search`.

- **Claude Code:** `/plugin install repertoire-searxng@repertoire`. Use either the plugin or the user-scope server above; when both are present, the skill uses the user-scope server first.
- **Desktop Cowork:** Customize > Plugins, enable `repertoire-searxng`. Cowork doesn't ask for plugin settings, so the server always uses the default `http://localhost:8888`; run SearXNG there to use it from Cowork.
- **Cloud Cowork sessions** can't run local MCP servers, so there the skill always uses WebSearch and WebFetch. Nothing needs to be configured for that.

If desktop Cowork shows the plugin but the skill still reports the fallback, the server may not reach `localhost:8888` from where Cowork runs it. Cowork can't change `searxng_url`, so keep the fallback there; a different address works only in Claude Code.

## Troubleshooting

| What you see | Cause and fix |
|--------------|---------------|
| `403 Forbidden` from the JSON check | `json` is missing from `search.formats`. Add it, then `docker restart searxng`. |
| Connection refused | The container isn't running. Check `docker ps` and `docker logs searxng`. |
| Report footer says `WebSearch + WebFetch (fallback: no SearXNG tool)` | No server is connected in this session. Check `claude mcp list`, or enable the plugin. |
| Report footer says `fallback: SearXNG not reachable` | The server runs but can't reach the instance. Check `SEARXNG_URL` or `searxng_url`, and the JSON check above. |
