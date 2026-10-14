"""Build a throwaway git repository for the changelog evals.

Usage: python -B make_release_repo.py <feature|pushfails|docsonly|breaking> [folder]

Creates <folder>/origin.git, a local bare remote, and <folder>/work, a clone whose
last tag is v1.2.0 (v0.4.0 for breaking), with the scenario's commits after it,
all pushed to origin.
  feature    feat, fix, docs and chore commits; CHANGELOG.md has an [Unreleased] entry
  pushfails  as feature, then origin points at a missing path, so fetch and push fail
  docsonly   only docs, test and ci commits; no [Unreleased] section
  breaking   on 0.4.0: a feat! commit, an unprefixed feature, an internal refactor
             and a test commit; no [Unreleased] section
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

{unreleased}## [{base}] - 2026-01-10

### Added
- JSON output for the report command

{unreleased_link}[{base}]: https://github.com/acme/report-tool/compare/v{previous}...v{base}
"""

UNRELEASED_LINK = "[Unreleased]: https://github.com/acme/report-tool/compare/v{base}...HEAD\n"

FEATURE_COMMITS = [
    ("src/export.txt", "feat: add CSV export to the report command"),
    ("src/parse.txt", "fix: stop crashing on an empty input file"),
    ("README.md", "docs: describe the export flag"),
    ("deps.txt", "chore: bump development dependencies"),
]

BREAKING_COMMITS = [
    ("src/cli.txt", "feat!: rename the --out flag to --output\n\n"
                    "BREAKING CHANGE: scripts that pass --out must pass --output instead."),
    ("src/quiet.txt", "Add a --quiet flag that hides the progress bar"),
    ("src/internal/parser.txt", "refactor: split the parser into smaller private helpers"),
    ("tests/test_cli.txt", "test: cover the renamed flag"),
]

# scenario: (last tag version, version before it, commits after the tag, has [Unreleased])
SCENARIOS = {
    "feature": ("1.2.0", "1.1.0", FEATURE_COMMITS, True),
    "pushfails": ("1.2.0", "1.1.0", FEATURE_COMMITS, True),
    "docsonly": ("1.2.0", "1.1.0", [
        ("README.md", "docs: fix typos in the README"),
        ("tests/test_report.txt", "test: cover the empty report"),
        ("ci.yml", "ci: cache dependencies between runs"),
    ], False),
    "breaking": ("0.4.0", "0.3.0", BREAKING_COMMITS, False),
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
        print("usage: python -B make_release_repo.py <feature|pushfails|docsonly|breaking> [folder]",
              file=sys.stderr)
        return 2
    scenario = argv[1]
    base_version, previous, commits, with_unreleased = SCENARIOS[scenario]
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

    append(work / "CHANGELOG.md", CHANGELOG.format(
        base=base_version, previous=previous,
        unreleased=UNRELEASED if with_unreleased else "",
        unreleased_link=UNRELEASED_LINK.format(base=base_version) if with_unreleased else ""))
    append(work / "README.md", "# report-tool\n")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "feat: add JSON output to the report command")
    git(work, "tag", "-a", f"v{base_version}", "-m", f"Release v{base_version} - JSON output")

    for rel, message in commits:
        append(work / rel, message + "\n")
        git(work, "add", "-A")
        git(work, "commit", "-q", "-m", message)

    git(work, "remote", "add", "origin", origin.as_posix())
    git(work, "push", "-q", "-u", "origin", "main", "--follow-tags")
    if scenario == "pushfails":
        git(work, "remote", "set-url", "origin", (base / "missing-remote.git").as_posix())

    print(f"ready: {work.as_posix()} ({scenario}; last tag v{base_version})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
