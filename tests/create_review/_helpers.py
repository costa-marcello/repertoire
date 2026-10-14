"""Shared fixtures for the create-skill script tests.

Importing this module puts create-skill/scripts on sys.path with bytecode
writing disabled, so tests never leave __pycache__ in the skills tree.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "skills" / "create-skill" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SUBPROCESS_TIMEOUT_SECONDS = 120  # generous: each script finishes in well under a second

CLEAN_NAME = "csv-report"
CLEAN_DESCRIPTION = "Converts CSV files into short summary reports. Use when the user asks to summarise a CSV file."
CLEAN_BODY = """\
# CSV Report

Turns one CSV file into a five-line summary.

<instructions>

1. Read the CSV file named in the request.
2. Count the rows and columns, and list the column names.
3. Write the summary as a Markdown table.
4. Verify: the row count in the summary matches the file.

</instructions>

## Examples

<example>
Request: "Summarise sales.csv"
Result: a table with 120 rows and 4 columns.
</example>

<example>
Request: "Summarise empty.csv"
Result: the summary says the file has no rows.
</example>

<example>
Request: "Summarise missing.csv"
Result: the error names the missing file.
</example>
"""


def write_file(path: Path, text: str, newline: str = "\n", bom: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.replace("\n", newline).encode("utf-8")
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + data)
    return path


def write_evals(skill_dir: Path, name: str = CLEAN_NAME) -> None:
    cases = [
        {"id": n, "prompt": f"Summarise file {n}.csv", "expected_output": "A table",
         "files": [], "expectations": ["The table has a row count"]}
        for n in (1, 2, 3)
    ]
    write_file(skill_dir / "evals" / "evals.json", json.dumps({"skill_name": name, "evals": cases}))
    queries = [{"query": "Summarise this CSV", "should_trigger": True},
               {"query": "Write a poem", "should_trigger": False}]
    write_file(skill_dir / "evals" / "trigger_queries.json", json.dumps(queries))


def make_skill(
    parent: Path,
    name: str = CLEAN_NAME,
    frontmatter: str | None = None,
    body: str = CLEAN_BODY,
    evals: bool = True,
    newline: str = "\n",
    bom: bool = False,
    folder: str | None = None,
) -> Path:
    """Write a skill that passes every check unless the arguments change it."""
    skill_dir = Path(parent) / (folder or name)
    if frontmatter is None:
        frontmatter = f"name: {name}\ndescription: {CLEAN_DESCRIPTION}\n"
    text = f"---\n{frontmatter.rstrip(chr(10))}\n---\n\n{body}"
    write_file(skill_dir / "SKILL.md", text, newline=newline, bom=bom)
    if evals:
        write_evals(skill_dir, name)
    return skill_dir


def make_dir_link(link: Path, target: Path) -> bool:
    """Point link at the directory target: a symlink, or a junction on Windows.

    Junctions need no admin rights. Returns False when neither can be created,
    so the calling test can skip.
    """
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(target, link, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        pass
    if sys.platform == "win32":
        try:
            import _winapi
            _winapi.CreateJunction(str(target), str(link))
            return True
        except (ImportError, OSError):
            pass
    return False


def run_script(script: str, *args: str, env_extra: dict | None = None, encoding: str = "utf-8",
               cwd: Path | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / script), *args],
        capture_output=True, text=True, encoding=encoding, errors="replace",
        env=env, cwd=cwd, timeout=SUBPROCESS_TIMEOUT_SECONDS,
    )
