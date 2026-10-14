#!/usr/bin/env python3
"""Package a validated, security-scanned skill into <skill-name>.zip.

The zip is a single-skill upload for claude.ai and the Claude API, never for
Cowork, which installs the plugin (as Claude Code does). So packaging validates
against the portable target (quick_validate.py --portable), which accepts only
six frontmatter fields.

Packaging requires quick_validate.py --portable to find no definitive Major and a
.security-scan-passed marker whose content hash matches the skill. The zip holds
the same files the hash covers: the top-level evals/, caches (__pycache__/,
node_modules/, .venv/, venv/, *.pyc), .git/, the marker, .env files and folders
(except .env.example), and zips are left out. Packaging also refuses a skill
that contains symlinks or junctions, which it never follows, and a skill whose
SKILL.md references a bundled file that the zip would leave out.

Usage:
    python scripts/package_skill.py <skill-dir> [output-dir]

Exit codes: 0 packaged, 1 refused or failed, 2 usage error.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # sibling imports must not write __pycache__ into the skill being packaged

import argparse  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import tempfile  # noqa: E402
import zipfile  # noqa: E402
from pathlib import Path  # noqa: E402

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from quick_validate import extract_bundled_paths, validate_skill  # noqa: E402
from security_scan import (  # noqa: E402
    ENV_PREFIX,
    MARKER_NAME,
    calculate_skill_hash,
    exclusion_reason,
    iter_skill_files,
    skill_links,
)

EXIT_PACKAGED = 0
EXIT_FAILED = 1

MARKER_HASH_RE = re.compile(r"Content hash:\s*([a-f0-9]{64})")  # 64 hex digits: a SHA-256 digest
PARTIAL_SUFFIX = ".zip.partial"  # the zip is built under this name and renamed only when complete
ENV_ERROR_TAG = "[env]"  # quick_validate starts environment errors (PyYAML missing, unreadable file) with this
DEFAULT_FILE_MODE = 0o666  # what open() creates before the umask; mkstemp would leave the zip owner-only (0600)
UPLOAD_NOTE = "This zip is for uploads to claude.ai and the Claude API, not for Cowork, which installs the plugin."


def validate_security_marker(skill_path: Path) -> tuple[bool, str]:
    """Check that the marker exists and its hash matches the current content."""
    marker = skill_path / MARKER_NAME
    if not marker.is_file():
        return False, "no security marker: the security scan has not passed for this skill"
    try:
        stored = MARKER_HASH_RE.search(marker.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        return False, f"cannot read {MARKER_NAME} ({exc})"
    if not stored:
        return False, f"{MARKER_NAME} has no content hash (old format)"
    try:
        current = calculate_skill_hash(skill_path)
    except OSError as exc:
        return False, f"cannot hash the skill files ({exc})"
    if stored.group(1) != current:
        return False, "the skill changed after the last security scan"
    return True, "security marker matches the current content"


def _body_lines(text: str) -> tuple[list[str], int]:
    """SKILL.md body lines and the file line number of the first one."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return lines[index + 1:], index + 2
    return lines, 1


LOCAL_ENV_DIR_NAMES = frozenset({".venv", "venv"})  # virtualenvs each user creates locally


def _is_local_only(rel: str) -> bool:
    """.env files and virtualenvs are created by each user, so SKILL.md may name them without shipping them."""
    return any(part.lower().startswith(ENV_PREFIX) or part.lower() in LOCAL_ENV_DIR_NAMES
               for part in Path(rel).parts)


def excluded_references(skill_path: Path) -> tuple[list[str], list[str]]:
    """SKILL.md mentions of bundled paths that exist but that the zip would leave out.

    quick_validate's M5 sees these files on disk and passes, so without this
    check the zip would ship broken references. The top-level evals/ is exempt:
    packaging strips it by design, and M5 treats it the same way. Returns
    (problems, notes): a left-out .env file or virtualenv is only a note, because
    each user creates their own and it must never ship.
    """
    text = (skill_path / "SKILL.md").read_text(encoding="utf-8-sig")
    lines, first_line = _body_lines(text)
    problems: list[str] = []
    notes: list[str] = []
    seen: set[str] = set()
    for line, sibling, token in extract_bundled_paths(lines, first_line):
        rel = token.rstrip("/")
        if sibling or rel in seen or not os.path.lexists(skill_path / rel):
            continue  # sibling skills and missing files are M5's job
        seen.add(rel)
        reason = exclusion_reason(rel, include_evals=True)
        if reason:
            message = f"SKILL.md:{line} references {token}, but the zip leaves it out ({reason})"
            (notes if _is_local_only(rel) else problems).append(message)
    return problems, notes


def _inside(path: Path, directory: Path) -> bool:
    return path == directory or directory in path.parents


def _default_mode() -> int:
    mask = os.umask(0)  # os.umask only reads the mask by setting it, so restore it at once
    os.umask(mask)
    return DEFAULT_FILE_MODE & ~mask


def build_zip(skill_path: Path, zip_path: Path) -> list[str]:
    """Write the zip through a temporary file in the same folder; return the archive names."""
    skill_name = skill_path.name
    fd, partial_name = tempfile.mkstemp(prefix=f".{skill_name}-", suffix=PARTIAL_SUFFIX, dir=zip_path.parent)
    os.close(fd)
    partial = Path(partial_name)
    skip = {partial.resolve(), zip_path.resolve()}
    added: list[str] = []
    completed = False
    try:
        with zipfile.ZipFile(partial, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in iter_skill_files(skill_path):
                if path.resolve() in skip:
                    continue
                arcname = f"{skill_name}/{path.relative_to(skill_path).as_posix()}"
                archive.write(path, arcname)
                added.append(arcname)
        os.chmod(partial, _default_mode())
        os.replace(partial, zip_path)
        completed = True
    finally:
        if not completed:
            partial.unlink(missing_ok=True)
    return added


def check_shipped_files(skill_path: Path) -> tuple[list[str], list[str]]:
    """(problems, notes): links and references to left-out files block packaging; local-only files are notes."""
    problems = [
        f"{path.relative_to(skill_path).as_posix()} is a symlink or junction, which packaging never follows"
        for path in skill_links(skill_path)
    ]
    reference_problems, notes = excluded_references(skill_path)
    return problems + reference_problems, notes


def package_skill(skill_path, output_dir=None) -> Path | None:
    """Validate, check the security marker and the file list, and zip the skill. Return the zip path or None."""
    skill_path = Path(skill_path).resolve()
    if not skill_path.is_dir():
        print(f"[ERROR] skill folder not found: {skill_path}", file=sys.stderr)
        return None
    if not (skill_path / "SKILL.md").is_file():
        print(f"[ERROR] SKILL.md not found in {skill_path}", file=sys.stderr)
        return None
    output_path = Path(output_dir).resolve() if output_dir else Path.cwd().resolve()
    if _inside(output_path, skill_path):
        print(f"[ERROR] the output folder {output_path} is inside the skill; "
              "pass an output folder outside it, for example its parent", file=sys.stderr)
        return None

    print(UPLOAD_NOTE)
    print("Step 1: validating the skill for the portable target")
    valid, message, warnings = validate_skill(skill_path, portable=True)
    if not valid:
        if message.lstrip().startswith(ENV_ERROR_TAG):
            print("[FAIL] quick_validate could not run:")
            print(message)
            print("Fix the problem above, then run this script again.")
        else:
            print("[FAIL] quick_validate found definitive Major findings for the portable target:")
            print(message)
            print(f"Fix them, then run: python scripts/quick_validate.py {skill_path} --portable")
        return None
    print(f"[OK] {message}")
    for warning in warnings:
        print(f"[WARN] {warning}")

    print("Step 2: checking the security marker")
    marker_ok, marker_message = validate_security_marker(skill_path)
    if not marker_ok:
        print(f"[FAIL] {marker_message}")
        print(f"Run: python scripts/security_scan.py {skill_path}")
        return None
    print(f"[OK] {marker_message}")

    print("Step 3: checking the files to ship")
    try:
        problems, notes = check_shipped_files(skill_path)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"[ERROR] cannot read the skill files ({exc}); check the folder permissions", file=sys.stderr)
        return None
    if problems:
        print("[FAIL] the zip would not match the skill:")
        for problem in problems:
            print(f"  {problem}")
        print("Replace each link with the real files, and move or rename each left-out file "
              "(or drop its reference); then re-run the security scan and this script.")
        return None
    for note in notes:
        print(f"[WARN] {note}; each user creates it, so it stays out of the zip")
    print("[OK] no links, and every referenced bundled file ships")

    print("Step 4: creating the package")
    zip_path = output_path / f"{skill_path.name}.zip"
    try:
        output_path.mkdir(parents=True, exist_ok=True)
        added = build_zip(skill_path, zip_path)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"[ERROR] could not write {zip_path} ({exc}); check the output folder and disk space",
              file=sys.stderr)
        return None
    for arcname in added:
        print(f"  added: {arcname}")
    print(f"[OK] Packaged {len(added)} file(s) to {zip_path}")
    return zip_path


def _configure_output() -> None:
    """Replace unencodable characters instead of crashing on cp1252 consoles and pipes."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scripts/package_skill.py",
        description="Package a validated, security-scanned skill into <skill-name>.zip.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "The zip is for uploads to claude.ai and the Claude API, never for Cowork, which installs\n"
            "the plugin. Packaging therefore validates against the portable target (six frontmatter fields).\n"
            "Run python scripts/security_scan.py <skill-dir> first; packaging needs its marker.\n"
            "Excluded from the zip: the top-level evals/, __pycache__/, node_modules/, .venv/, venv/,\n"
            ".git/, *.pyc, *.zip, .env files and folders (except .env.example), .DS_Store, Thumbs.db,\n"
            "and the security marker. Packaging refuses symlinks and junctions, and SKILL.md\n"
            "references to bundled files that the zip would leave out.\n\n"
            "Exit codes: 0 packaged, 1 refused or failed, 2 usage error."
        ),
    )
    parser.add_argument("skill_dir", help="path to the skill directory")
    parser.add_argument("output_dir", nargs="?", default=None,
                        help="folder for the zip, outside the skill (default: the current folder)")
    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_output()
    args = build_parser().parse_args(argv)
    print(f"Packaging skill: {args.skill_dir}")
    return EXIT_PACKAGED if package_skill(args.skill_dir, args.output_dir) else EXIT_FAILED


if __name__ == "__main__":
    sys.exit(main())
