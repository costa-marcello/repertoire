"""Build the team-tools plugin repository for create-skill eval 1.

Usage: python -B make_team_tools.py [folder]

Creates <folder>/team-tools (default: the current folder): .claude-plugin/plugin.json and
a stand-in scripts/link_user_skills.py that changes nothing. The manifest is generated
instead of shipped because Cowork skips a "./" plugin whose folder holds another
.claude-plugin/plugin.json, and this fixture lives inside the Repertoire plugin.
Nothing leaves the machine. Exit codes: 0 ready, 1 team-tools/ already exists, 2 usage.
"""

import sys
from pathlib import Path

MANIFEST = """{
  "name": "team-tools",
  "description": "Skills for the platform team's daily work.",
  "author": { "name": "Platform Team" }
}
"""

LINK_SCRIPT = '''"""Eval fixture: stands in for a plugin repository's link script and changes nothing."""

print("fixture: link_user_skills.py makes no links in an eval run")
'''


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print("usage: python -B make_team_tools.py [folder]", file=sys.stderr)
        return 2
    repo = Path(argv[1] if len(argv) == 2 else ".").resolve() / "team-tools"
    if repo.exists():
        print(f"{repo} already exists; run this in a folder without team-tools/", file=sys.stderr)
        return 1
    (repo / ".claude-plugin").mkdir(parents=True)
    (repo / "scripts").mkdir()
    (repo / ".claude-plugin" / "plugin.json").write_text(MANIFEST, encoding="utf-8")
    (repo / "scripts" / "link_user_skills.py").write_text(LINK_SCRIPT, encoding="utf-8")
    print(f"ready: {repo.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
