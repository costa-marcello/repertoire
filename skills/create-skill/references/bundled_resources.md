# Bundled Resources

What goes into a skill directory beside SKILL.md, how to decide what to bundle, and the naming, path, and versioning rules that keep a skill working wherever it is installed, in Claude Code and Cowork alike.

## Contents

1. [Skill directory layout](#skill-directory-layout)
2. [Planning resources from use cases](#planning-resources-from-use-cases)
3. [scripts/](#scripts)
4. [references/](#references)
5. [assets/](#assets)
6. [evals/ and tests/](#evals-and-tests)
7. [Naming files](#naming-files)
8. [Privacy and paths](#privacy-and-paths)
9. [Versioning](#versioning)

## Skill directory layout

The skill root holds only these entries; review-skill ignores dotfiles:

- `SKILL.md`
- `LICENSE*`
- `scripts/`, `references/`, `assets/`
- `evals/`, `tests/`

Anything else in the root is an S4 Style note. Keep eval workspaces, reports, and build output in a separate directory.

## Planning resources from use cases

For each eval case or concrete request, ask two questions: how would Claude do this from scratch, and what did it have to rebuild or rediscover each time? The baseline transcripts from step 2 answer the second question directly. Code they repeat and facts they had to rediscover are exactly what to bundle.

**pdf-editor.** Request: "Rotate pages 2 to 4 of this PDF."
- Every run rewrites the same rotation code.
- Bundle `pdf-editor/scripts/rotate_pdf.py`.
- Low freedom: the operation is deterministic and fragile.

**frontend-webapp-builder.** Request: "Build me a todo app" or "Build me a dashboard to track my steps."
- Every run rebuilds the same HTML and React boilerplate.
- Bundle the template project `frontend-webapp-builder/assets/hello-world/`.
- Medium freedom: a preferred pattern exists, and the implementation varies.

**big-query.** Request: "How many users logged in today?"
- Every run rediscovers the table schemas and relationships.
- Bundle `big-query/references/schema.md`.
- High freedom: many valid queries, and context decides.

| Use case | Freedom | Resource | Typical contents |
|----------|---------|----------|------------------|
| Deterministic operations | Low | `scripts/` | Format conversion, validation, migrations |
| Boilerplate | Medium | `assets/` | Project templates, document templates |
| Domain knowledge | High | `references/` | Schemas, API docs, policies |

## scripts/

**When to bundle a script**
- The eval transcripts show the agent writing the same code in every run. For example, all three baseline runs wrote a CSV-sniffing helper. Write it once.
- The operation is fragile or has to be identical on every run: file-format edits, migrations, validation.
- Running the computation is cheaper than describing it.

**When not to.** Skip a script for a one-line command that Claude writes correctly anyway.

**Contract** (review-skill M6, M10, m13):
- **Run or read.** SKILL.md says for each script either "Run ..." (only the output enters context) or "Read ... for ...".
- **Requirements.** SKILL.md names the packages the script needs and the install command (`python -m pip install pypdf`), instead of assuming them.
- **Non-interactive.**
  - Inputs come from arguments, flags, or environment variables, never `input()`.
  - Provide `--help`.
  - Put data on stdout and diagnostics on stderr.
  - Return meaningful exit codes, and keep the output size predictable.
- **Errors.** Catch specific exceptions, and print what failed and how to fix it. No bare `except:`, and no `except Exception: pass`.
- **Constants.** Comment each constant with the reason for its value.
- **Output encoding.** Use plain ASCII tags such as `[OK]` and `[FAIL]`, and write UTF-8 to stdout. Emoji crash under the Windows cp1252 console encoding when output is piped.
- **Invocation.** Write commands with `python`; use `python3` only where `python` is not on the path (on Windows `python3` is often the Microsoft Store stub). In Claude Code and Cowork, reference scripts through `${CLAUDE_SKILL_DIR}/scripts/`; `frontmatter_reference.md` covers the variants. Inside a script, find bundled files from `Path(__file__).resolve().parent`.
- **Output.** Write results to files and print their paths; never open a window, browser, or viewer. Cowork has no display, and the user collects files from the outputs folder (M11).
- **Network.** Disclose any network use, and its purpose, in SKILL.md (M10).
- **Local services.** A script that needs a local stdio MCP server or a `localhost` service states a fallback in SKILL.md, because cloud Cowork sessions cannot reach them (M11).

## references/

- **Purpose.** Knowledge needed in only some runs: schemas, API docs, policies, detailed guides, long examples.
- **Links.** SKILL.md links each reference file directly and says when to read it. Do not build chains in which one reference sends Claude to another for essential content (m10).
- **Length.** A reference file over 100 lines gets a `## Contents` list within its first 30 lines (m9).
- **Large files.** For very large files, SKILL.md gives a grep pattern that finds the right section, so Claude reads only that part.
- **One home per fact.** Each fact lives in SKILL.md or in a reference file, not both. Duplicates drift apart and become contradictions (M5).
- **Variants.** When a skill supports several domains, give each variant its own file (one per cloud provider or framework), so Claude reads only the one it needs.
- **Teaching material.** Examples that use substitution tokens or injection syntax belong here, not in SKILL.md.

## assets/

Files used in the output and not read into context: templates, images, fonts, icons, boilerplate projects, sample documents to copy or modify. Ask the user for brand files or templates that only they have.

## evals/ and tests/

- **evals/**
  - It holds `evals/evals.json` (3 or more eval cases) and `evals/trigger_queries.json` (about 10 trigger queries), both written before the skill.
  - Input files go in `evals/files/`.
  - The zip from `package_skill.py` leaves out `evals/`; a plugin install carries the folder, which does no harm. `evals_guide.md` has the formats.
- **tests/** (optional) holds unit tests for bundled scripts. Using the standard library's `unittest` keeps them free of dependencies.

## Naming files

- **Descriptive names.** A filename says what the file contains: `api-endpoints.md`, `database-schema.md`, `rotate-pdf.py`. Avoid names such as `reference.md`, `notes.md`, or `utils.py`. Test: can someone tell the contents from the name alone?
- **One separator per skill.** Hyphens (`api-endpoints.md`) and underscores (`api_endpoints.md`) both work. Mixing them in one skill's reference files is S7. When updating a skill, follow the separator its existing files use.

## Privacy and paths

**Leave out:**
- user-specific absolute paths: home directories with a real user name, cloud-sync folders;
- real people's names, and company, department, or product names (`sanitization_checklist.md` covers public releases);
- an install location for the skill's own files, such as `~/.claude/skills/<skill-name>/` or `.claude/skills/<skill-name>/`. The skill may be installed per project, per user, or in a plugin, and Cowork never reads those folders (M11);
- secrets: read them from environment variables, not only from a home-directory dotfile (M11).

**Use:**
- paths relative to the skill directory, or `${CLAUDE_SKILL_DIR}/...` in Claude Code and Cowork;
- generic placeholders (`<project-root>`, `<user>`, `your-company`);
- forward slashes, on Windows too (m11). Fenced blocks tagged `powershell`, `ps1`, `cmd`, or `bat` are exempt.

## Versioning

- **No history in SKILL.md.** Do not add a version-history section or version numbers to the body. History lives in git, in the repository CHANGELOG, and in plugin or marketplace manifests (`marketplace_update.md`).
- **Pinned dependencies.** Pin a dependency version only when the skill needs it, and add a note: "Requires pypdf 4.x (verify against the official docs)". A bare pinned version reads as time-sensitive content (m3).
