#!/usr/bin/env python3
"""Create a new skill skeleton that follows the Repertoire authoring rules.

The generated SKILL.md, evals/evals.json, and evals/trigger_queries.json contain
[TODO placeholders. Once every placeholder is replaced, the skill passes
quick_validate.py with no findings.

Usage:
    python scripts/init_skill.py <skill-name> --path <parent-dir> [--fork] [--resources scripts,references,assets]

Exit codes: 0 created, 1 invalid name, existing target, or write failure
(the partial skill folder and any parent folders created for it are removed),
2 usage error.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # importing the sibling validator must not leave __pycache__ in the skill tree

import argparse  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
from pathlib import Path  # noqa: E402

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from quick_validate import RESERVED_NAME_WORDS, folder_name_errors, name_errors  # noqa: E402

EXIT_CREATED = 0
EXIT_FAILED = 1

RESOURCE_DIRS = ("scripts", "references", "assets")
EVAL_CASES = (  # one case per example in the SKILL.md template
    "the typical case",
    "an edge case",
    "a failure and its recovery",
)
TRIGGER_QUERIES_PER_KIND = 5  # about 10 queries in all, half of them near-misses (skill-creator's guidance)

SKILL_TEMPLATE = """\
---
name: {name}
description: "[TODO: third-person sentence on what the skill does, key use case first]. Use when [TODO: the requests that should trigger it]."
{fork_line}---

# {title}

[TODO: one sentence on what this skill produces and for whom.]

<instructions>

## Workflow

{steps}

## Gotchas

- [TODO: a mistake Claude makes without this skill, and the correct behaviour.]
- [TODO: an edge case and the default to apply.]

</instructions>

## Examples

<example>
**Typical case.** Request: "[TODO: a realistic request]"
Result: [TODO: what the skill does and returns.]
</example>

<example>
**Edge case.** Request: "[TODO: an unusual but valid request]"
Result: [TODO: how the skill adapts, and why.]
</example>

<example>
**Failure and recovery.** Request: "[TODO: a request that hits an error]"
Result: [TODO: the error message, the fix, and the retry.]
</example>
"""

INLINE_STEPS = """\
1. [TODO: the first concrete action, for example reading the input named in the request.]
2. [TODO: the main action; give exact commands for fragile steps.]
3. [TODO: produce the result and state where it goes.]
4. Verify: [TODO: the check that proves the result is correct, such as a validator run, a test, or a diff.]"""

FORK_STEPS = """\
1. Read the arguments. If [TODO: the required argument] is missing, print the usage line and stop, because a forked skill sees no conversation and cannot pause.
2. [TODO: the main action; give exact commands for fragile steps.]
3. [TODO: produce the result to return.]
4. Verify: [TODO: the check that proves the result is correct, such as a validator run, a test, or a diff.]"""


class InitError(Exception):
    """The skill cannot be created; the message says why and how to fix it."""


def title_from_name(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split("-"))


def check_name(name: str) -> None:
    """Apply the same name rules as quick_validate (M9) before anything is created."""
    if "/" in name or "\\" in name or ".." in name:
        raise InitError(f"'{name}' must be a single folder name, not a path; pass the parent folder with --path")
    problems = name_errors(name) + folder_name_errors(name)
    if problems:
        raise InitError(f"invalid skill name '{name}': " + "; ".join(problems))


def parse_resources(value: str) -> list[str]:
    requested = [part.strip() for part in value.split(",") if part.strip()]
    unknown = [part for part in requested if part not in RESOURCE_DIRS]
    if unknown:
        raise argparse.ArgumentTypeError(
            f"unknown resource folder(s): {', '.join(unknown)}; choose from {','.join(RESOURCE_DIRS)}"
        )
    return list(dict.fromkeys(requested))


def render_skill_md(name: str, fork: bool) -> str:
    return SKILL_TEMPLATE.format(
        name=name,
        title=title_from_name(name),
        fork_line="context: fork\n" if fork else "",
        steps=FORK_STEPS if fork else INLINE_STEPS,
    )


def render_evals(name: str) -> str:
    cases = [
        {
            "id": number,
            "prompt": f"[TODO: a realistic request for {case}]",
            "expected_output": "[TODO: what a correct result contains]",
            "files": [],
            "expectations": ["[TODO: an objectively checkable statement about the output]"],
        }
        for number, case in enumerate(EVAL_CASES, 1)
    ]
    return json.dumps({"skill_name": name, "evals": cases}, indent=2) + "\n"


def render_trigger_queries() -> str:
    queries = [
        {"query": f"[TODO: a request that should trigger the skill ({n})]", "should_trigger": True}
        for n in range(1, TRIGGER_QUERIES_PER_KIND + 1)
    ] + [
        {"query": f"[TODO: a near-miss request that should not trigger it ({n})]", "should_trigger": False}
        for n in range(1, TRIGGER_QUERIES_PER_KIND + 1)
    ]
    return json.dumps(queries, indent=2) + "\n"


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def _populate(skill_dir: Path, name: str, fork: bool, resources: list[str]) -> None:
    _write_text(skill_dir / "SKILL.md", render_skill_md(name, fork))
    print("[OK] Created SKILL.md")
    (skill_dir / "evals").mkdir()
    _write_text(skill_dir / "evals" / "evals.json", render_evals(name))
    _write_text(skill_dir / "evals" / "trigger_queries.json", render_trigger_queries())
    print("[OK] Created evals/evals.json and evals/trigger_queries.json")
    for resource in resources:
        (skill_dir / resource).mkdir()
        print(f"[OK] Created {resource}/")


def _missing_folders(folder: Path) -> list[Path]:
    """The folders that folder.mkdir(parents=True) would create, outermost first."""
    missing = []
    current = folder.absolute()
    while not current.exists() and current != current.parent:
        missing.append(current)
        current = current.parent
    return missing[::-1]


def _rollback(skill_dir: Path | None, created_parents: list[Path]) -> None:
    """Remove what init created: the skill folder, then the empty parent folders made for it."""
    if skill_dir is not None:
        try:
            shutil.rmtree(skill_dir)
            print(f"[OK] Removed the partially created {skill_dir}", file=sys.stderr)
        except OSError as exc:
            print(f"[ERROR] Could not remove {skill_dir} ({exc.strerror or exc}); delete it by hand", file=sys.stderr)
            return
    for folder in reversed(created_parents):
        if not folder.exists():
            continue
        try:
            folder.rmdir()  # only empty folders: anything another process wrote there stays
        except OSError as exc:
            print(f"[ERROR] Could not remove the folder {folder} ({exc.strerror or exc}); "
                  "delete it by hand if it is not needed", file=sys.stderr)
            return
        print(f"[OK] Removed the folder {folder}, created for the skill", file=sys.stderr)


def init_skill(name: str, path, fork: bool = False, resources: list[str] | None = None) -> Path:
    """Create <path>/<name> with the template files. Raises InitError on failure.

    On any failure, the skill folder and every parent folder created for it are
    removed again, so nothing is left behind.
    """
    check_name(name)
    resources = resources or []
    parent = Path(path)
    skill_dir = parent / name
    if skill_dir.exists():
        raise InitError(f"{skill_dir} already exists; choose another name or remove it first")
    created_parents = _missing_folders(parent)
    created_skill_dir: Path | None = None
    completed = False
    try:
        try:
            parent.mkdir(parents=True, exist_ok=True)
            skill_dir.mkdir()
        except OSError as exc:
            raise InitError(
                f"cannot create {skill_dir} ({exc.strerror or exc}); check the path and permissions"
            ) from exc
        created_skill_dir = skill_dir
        print(f"[OK] Created {skill_dir}")
        try:
            _populate(skill_dir, name, fork, resources)
        except OSError as exc:
            raise InitError(
                f"writing the skill files failed ({exc.strerror or exc}); check disk space and permissions"
            ) from exc
        completed = True
    finally:
        if not completed:
            _rollback(created_skill_dir, created_parents)
    return skill_dir


def _configure_output() -> None:
    """Replace unencodable characters instead of crashing on cp1252 consoles and pipes."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scripts/init_skill.py",
        description="Create a new skill folder with a SKILL.md template and evals skeletons.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Name rules: 1-64 lowercase letters, digits, and single hyphens; the folder gets the same name.\n\n"
            "Examples:\n"
            "  python scripts/init_skill.py csv-report --path skills\n"
            "  python scripts/init_skill.py csv-report --path skills --fork --resources scripts,references\n\n"
            "Exit codes: 0 created, 1 failed (nothing is left behind), 2 usage error."
        ),
    )
    parser.add_argument("name", help="skill name, which is also the folder name (for example csv-report)")
    parser.add_argument("--path", required=True, help="parent folder in which to create the skill folder")
    parser.add_argument(
        "--fork", action="store_true",
        help="add 'context: fork' (only for self-contained tasks that never ask the user anything)",
    )
    parser.add_argument(
        "--resources", type=parse_resources, default=[],
        help="comma-separated empty folders to create: scripts,references,assets",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_output()
    args = build_parser().parse_args(argv)
    print(f"Initializing skill '{args.name}' in {args.path}")
    try:
        skill_dir = init_skill(args.name, args.path, fork=args.fork, resources=args.resources)
    except InitError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return EXIT_FAILED

    if any(word in args.name for word in RESERVED_NAME_WORDS):
        print("[WARN] The name contains 'claude' or 'anthropic', which blocks upload to claude.ai and the API (m12).")
    print(f"\n[OK] Skill '{args.name}' initialized at {skill_dir}")
    print("\nNext steps:")
    print("  1. Replace every [TODO placeholder in SKILL.md, starting with the description.")
    print("  2. Replace the [TODO placeholders in evals/evals.json and evals/trigger_queries.json with real cases.")
    print("  3. Add files under scripts/, references/, or assets/ only when SKILL.md links them.")
    print(f"  4. Run: python scripts/quick_validate.py {skill_dir}")
    return EXIT_CREATED


if __name__ == "__main__":
    sys.exit(main())
