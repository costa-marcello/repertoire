"""Build a throwaway git repository for the changelog evals.

Usage: python -B make_release_repo.py <feature|pushfails|docsonly> [folder]

Creates <folder>/origin.git, a local bare remote, and <folder>/work, a clone whose
last tag is v1.2.0, with the scenario's commits after it, all pushed to origin.
  feature    feat, fix, docs and chore commits; CHANGELOG.md has an [Unreleased] entry
  pushfails  as feature, then origin points at a missing path, so fetch and push fail
  docsonly   only docs, test and ci commits; no [Unreleased] section
Nothing leaves the machine. Exit codes: 0 ready, 1 git failed or the folder is in use, 2 usage.
"""

import subprocess
import sys
from pathlib import Path

UNRELEASED = """## [Unreleased]

### Changed
- Clearer error message when the config file is missing

"""

CHANGELOG = """# Changelog

All notable changes to this project will be documented in this file.

{unreleased}## [1.2.0] - 2026-01-10

### Added
- JSON output for the report command

{unreleased_link}[1.2.0]: https://github.com/acme/report-tool/compare/v1.1.0...v1.2.0
"""

UNRELEASED_LINK = "[Unreleased]: https://github.com/acme/report-tool/compare/v1.2.0...HEAD\n"

FEATURE_COMMITS = [
    ("src/export.txt", "feat: add CSV export to the report command"),
    ("src/parse.txt", "fix: stop crashing on an empty input file"),
    ("README.md", "docs: describe the export flag"),
    ("deps.txt", "chore: bump development dependencies"),
]

SCENARIOS = {
    "feature": FEATURE_COMMITS,
    "pushfails": FEATURE_COMMITS,
    "docsonly": [
        ("README.md", "docs: fix typos in the README"),
        ("tests/test_report.txt", "test: cover the empty report"),
        ("ci.yml", "ci: cache dependencies between runs"),
    ],
}


def git(cwd: Path, *args: str) -> None:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed in {cwd}: {result.stderr.strip()}")


def append(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3) or argv[1] not in SCENARIOS:
        print("usage: python -B make_release_repo.py <feature|pushfails|docsonly> [folder]", file=sys.stderr)
        return 2
    scenario = argv[1]
    base = Path(argv[2] if len(argv) == 3 else ".").resolve()
    origin, work = base / "origin.git", base / "work"
    if origin.exists() or work.exists():
        print(f"{base} already has origin.git or work/; run this in an empty folder", file=sys.stderr)
        return 1
    base.mkdir(parents=True, exist_ok=True)

    git(base, "init", "-q", "--bare", "origin.git")
    git(base, "init", "-q", "-b", "main", "work")
    for key, value in (("user.name", "Eval Bot"), ("user.email", "eval-bot@example.com"),
                       ("commit.gpgsign", "false"), ("tag.gpgsign", "false"), ("core.autocrlf", "false")):
        git(work, "config", key, value)

    with_unreleased = scenario != "docsonly"
    append(work / "CHANGELOG.md", CHANGELOG.format(
        unreleased=UNRELEASED if with_unreleased else "",
        unreleased_link=UNRELEASED_LINK if with_unreleased else ""))
    append(work / "README.md", "# report-tool\n")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "feat: add JSON output to the report command")
    git(work, "tag", "-a", "v1.2.0", "-m", "Release v1.2.0 - JSON output")

    for rel, message in SCENARIOS[scenario]:
        append(work / rel, message + "\n")
        git(work, "add", "-A")
        git(work, "commit", "-q", "-m", message)

    git(work, "remote", "add", "origin", origin.as_posix())
    git(work, "push", "-q", "-u", "origin", "main", "--follow-tags")
    if scenario == "pushfails":
        git(work, "remote", "set-url", "origin", (base / "missing-remote.git").as_posix())

    print(f"ready: {work.as_posix()} ({scenario}; last tag v1.2.0)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
