"""Build a fixture for create-skill's evals.

Usage: python -B make_fixture.py <team-tools|csv-summary> [folder]

Creates <folder>/<fixture> (default: the current folder):
  team-tools   a plugin repository: .claude-plugin/plugin.json and a stand-in
               scripts/link_user_skills.py that changes nothing (eval 1)
  csv-summary  a one-file skill whose step 2 assumes commas (eval 3)
The fixtures are generated instead of shipped because Cowork reads the whole Repertoire
plugin: a shipped .claude-plugin/plugin.json makes it skip the plugin, and a shipped
SKILL.md shows up as a skill of its own.
Nothing leaves the machine. Exit codes: 0 ready, 1 the fixture folder already exists, 2 usage.
"""

import sys
from pathlib import Path

TEAM_TOOLS_MANIFEST = """{
  "name": "team-tools",
  "description": "Skills for the platform team's daily work.",
  "author": { "name": "Platform Team" }
}
"""

TEAM_TOOLS_LINK_SCRIPT = '''"""Eval fixture: stands in for a plugin repository's link script and changes nothing."""

print("fixture: link_user_skills.py makes no links in an eval run")
'''

CSV_SUMMARY_SKILL = """---
name: csv-summary
description: "Summarises a CSV file as a Markdown table of row and column counts. Use when the user asks how many rows or columns a CSV has."
---

# CSV Summary

<instructions>

1. Read the CSV file the user names.
2. Split each line on commas to get the fields.
3. Count the rows (excluding the header) and the columns in the header.
4. Reply with a two-row Markdown table: `rows | columns`.
5. Verify: the row count equals the number of non-empty lines minus one.

</instructions>
"""

FIXTURES = {
    "team-tools": {
        ".claude-plugin/plugin.json": TEAM_TOOLS_MANIFEST,
        "scripts/link_user_skills.py": TEAM_TOOLS_LINK_SCRIPT,
    },
    "csv-summary": {
        "SKILL.md": CSV_SUMMARY_SKILL,
    },
}


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3) or argv[1] not in FIXTURES:
        print("usage: python -B make_fixture.py <team-tools|csv-summary> [folder]", file=sys.stderr)
        return 2
    name = argv[1]
    target = Path(argv[2] if len(argv) == 3 else ".").resolve() / name
    if target.exists():
        print(f"{target} already exists; run this in a folder without {name}/", file=sys.stderr)
        return 1
    for relative, text in FIXTURES[name].items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"ready: {target.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
