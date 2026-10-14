# Script Quality

How to review a skill's bundled scripts. Scripts should solve the problem rather than hand it back to Claude, and they run inside an agent, so they must never wait for input. Read the scripts; never run the target's scripts to test them.

## Contents

1. [Error handling (M6)](#error-handling-m6)
2. [No interactive input (M6)](#no-interactive-input-m6)
3. [Script contract in SKILL.md (m13)](#script-contract-in-skillmd-m13)
4. [Agent-friendly behavior](#agent-friendly-behavior)
5. [Constants and paths](#constants-and-paths)
6. [Security (M10)](#security-m10)
7. [Checklist](#checklist)

## Error handling (M6)

- **Definitive M6:** a bare `except:`, or an `except Exception:` or `except BaseException:` whose body is only `pass`.
- **Heuristic M6:** a catch-all handler that hides the cause and offers no recovery or actionable message. That includes a handler that prints a vague error and then exits 0, so Claude reads the failure as success.

Fails, because it hides the cause:

```python
try:
    rows = load(path)
except Exception:
    pass
```

Passes, because it names the failure and the fix and returns a meaningful exit code:

```python
try:
    rows = load(path)
except FileNotFoundError:
    print(f"error: input not found: {path}; pass an existing CSV path", file=sys.stderr)
    sys.exit(2)
```

Fix: catch the specific exceptions the code can raise, print what failed and how to fix it, and exit non-zero.

## No interactive input (M6)

The Agent Skills specification makes "no interactive prompts" a hard requirement: an agent cannot answer a prompt, so the script hangs.

- **Definitive M6:** a bundled Python script calls `input()`, `raw_input()`, or `getpass.getpass()`.
- **Heuristic M6:** a Python script reads `sys.stdin` interactively, or a shell script runs `read` (including `read -p`). quick_validate prints both as `check` lines; confirm each by reading.
- Fix: take every input as an argument, a flag, or an environment variable, and fail with a usage message when one is missing.

## Script contract in SKILL.md (m13)

For each script, SKILL.md must say:

- **Run or read.** "Run `python scripts/x.py <in>`" or "Read `scripts/x.py` for the algorithm." Running is the usual intent; reading is for reference code.
- **Requirements.** Packages and tools the script needs, with the install command: "Requires pypdf: `python -m pip install pypdf`." Do not assume anything beyond the standard library is installed.

Missing either one is m13.

## Agent-friendly behavior

From the Agent Skills specification. Report gaps as advisory notes unless a rule above applies.

| Behavior | Why it matters | Rule when missing |
|----------|----------------|-------------------|
| `--help` prints usage and exits 0 | Claude can learn the flags without reading the source | advisory |
| Data on stdout, diagnostics on stderr | Claude can parse the output without filtering noise | advisory |
| Meaningful exit codes (0 success, non-zero failure) | Claude can branch on the result | M6 (heuristic) when an error handler exits 0; otherwise advisory |
| Predictable output size (limits, `--max`, summaries) | Large dumps flood the context window | advisory |
| Errors handled in the script ("solve, don't punt") | Claude does not have to debug the script mid-task | M6 when errors are swallowed |

## Constants and paths

- **Documented constants.** Anthropic's guidance warns against "voodoo constants". Each timeout, retry count, or threshold gets a comment saying why it has that value. A missing reason is advisory.

  ```python
  # Most intermittent API failures clear by the second retry; 3 bounds the wait.
  MAX_RETRIES = 3
  ```

- **Paths.** Scripts take paths as arguments or derive them from their own location. A user-specific absolute path in a script is reported by security_scan as an `[m11] minor check` line; confirm it by reading.
- **Runs in Cowork (M11).** A script that reaches its own skill's files through an install location (`~/.claude/skills/<own-name>/`, `.claude/skills/<own-name>/`, or the same under `.agents/skills/`) breaks in plugin installs and in Cowork; derive the path from `Path(__file__).resolve().parent`. Also M11, after confirming by reading: opening a browser or window (quick_validate prints a `webbrowser` import as an `[M11] major check` line), calling `claude -p`, needing a `localhost` service with no fallback, or reading secrets only from a home-directory dotfile.

## Security (M10)

Read every script for:

- network calls (`requests`, `urllib`, `curl`, `fetch`, sockets) that SKILL.md does not disclose;
- file access outside the skill and the user's stated inputs;
- data sent to a host the user did not name;
- hardcoded credentials (gitleaks finds most; read for the rest when it did not run);
- code that downloads and runs other code.

Disclosed network use with a stated purpose passes. A script that silently posts file contents to an unlisted host fails.

## Checklist

```text
Script review:
- [ ] No bare except, and no except Exception or BaseException with only pass (M6)
- [ ] No input(), raw_input(), or getpass.getpass() (M6, definitive), and no interactive stdin or shell read (M6, heuristic)
- [ ] Failures exit non-zero with an actionable message (M6)
- [ ] SKILL.md says run or read for each script, and names its requirements (m13)
- [ ] Network use, file access, and credentials checked against SKILL.md (M10)
- [ ] Own files reached through the script's location, no browser or window, no `claude -p`, a fallback for local services, secrets from environment variables (M11)
- [ ] --help, stdout/stderr split, output size, documented constants (advisory)
```
