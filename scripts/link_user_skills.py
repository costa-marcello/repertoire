#!/usr/bin/env python3
"""Link this Repertoire checkout into Claude Code as a plugin.

Creates one directory link, <dest>/repertoire, that points at the root of this
repository. Claude Code then loads the live checkout as the plugin
repertoire@skills-dir, and its skills run as /repertoire:<skill>.

On Windows the link is a directory junction, which needs no admin rights.
Elsewhere it is a symbolic link.

The script also removes stale links in <dest> that point into this repository,
such as an old per-skill link create-skill -> <repo>/skills/create-skill,
because the plugin already provides those skills. It never touches anything
that is not a link into this repository, and it never looks inside
<dest>/synced, which the Claude desktop app manages.

Requires Python 3.12 or later and nothing outside the standard library.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

LINK_NAME = "repertoire"
PROTECTED_NAMES = {"synced"}  # managed by the Claude desktop app; never read or changed

EXIT_OK = 0
EXIT_CONFLICT = 1
EXIT_USAGE = 2

EPILOG = """\
exit codes:
  0  the link is in place (or, with --unlink, no managed link is left)
  1  conflict or error (on a conflict, nothing is changed)
  2  usage error

examples:
  python scripts/link_user_skills.py --dry-run
  python scripts/link_user_skills.py
  python scripts/link_user_skills.py --unlink
"""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_dest() -> Path:
    return Path.home() / ".claude" / "skills"


def is_link(path: Path) -> bool:
    return path.is_junction() or path.is_symlink()


def link_target(link: Path) -> Path | None:
    """Where a junction or symlink points, made absolute; None if unreadable."""
    try:
        raw = os.readlink(link)
    except OSError:
        return None
    if raw.startswith("\\\\?\\UNC\\"):
        raw = "\\\\" + raw[len("\\\\?\\UNC\\"):]
    elif raw.startswith("\\\\?\\"):
        raw = raw[len("\\\\?\\"):]
    target = Path(raw)
    if not target.is_absolute():
        target = link.parent / target
    return Path(os.path.realpath(target))


def is_within(path: Path, root: Path) -> bool:
    return path == root or path.is_relative_to(root)


def remove_link(link: Path) -> None:
    """Remove only the link itself; the folder it points at is untouched."""
    if link.is_junction():
        os.rmdir(link)
    else:
        os.unlink(link)


def create_link(link: Path, target: Path) -> None:
    if sys.platform == "win32":
        try:
            import _winapi
            _winapi.CreateJunction(str(target), str(link))
            return
        except (ImportError, AttributeError, OSError):
            pass
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise OSError(f"mklink /J failed: {detail}")
        return
    os.symlink(target, link, target_is_directory=True)


def links_into_repo(dest: Path, root: Path) -> list[tuple[Path, Path]]:
    """Links in dest, other than the managed one, whose target is inside root."""
    found = []
    with os.scandir(dest) as entries:
        for entry in entries:
            name = entry.name
            if name.casefold() in PROTECTED_NAMES or name.casefold() == LINK_NAME:
                continue
            path = Path(entry.path)
            if not is_link(path):
                continue
            target = link_target(path)
            if target is not None and is_within(target, root):
                found.append((path, target))
    return sorted(found)


def report(dry_run: bool, present: str, past: str, text: str) -> None:
    """Print one action, as "Would <present> ..." in a dry run or "<Past> ..." otherwise."""
    print(f"Would {present} {text}" if dry_run else f"{past} {text}")


def describe(path: Path) -> str:
    if path.is_junction():
        return "a junction"
    if path.is_symlink():
        return "a symbolic link"
    if path.is_dir():
        return "a real folder"
    return "a file"


def print_next_steps(link: Path) -> None:
    print()
    print("Next steps:")
    print("  1. Start a new Claude Code session, or run /reload-plugins in an open one.")
    print("  2. Run the skills as /repertoire:<skill>, for example /repertoire:changelog.")
    print("  3. `claude plugin list` shows the plugin as repertoire@skills-dir.")
    print("  4. Don't also install repertoire@repertoire from the marketplace on this")
    print("     machine: an installed plugin outranks this link, so the live checkout")
    print("     would stop loading.")
    print(f"To remove the link later, run this script with --unlink (removes only {link}).")


def link(dest: Path, root: Path, dry_run: bool) -> int:
    managed = dest / LINK_NAME

    if not dest.exists():
        if dest.is_symlink() or dest.is_junction():
            print(f"Error: {dest} is a broken link. Fix or remove it, then run again.")
            return EXIT_CONFLICT
        report(dry_run, "create", "Created", f"folder {dest}")
        if not dry_run:
            try:
                dest.mkdir(parents=True)
            except OSError as exc:
                print(f"Error: {exc}")
                return EXIT_CONFLICT
        stale = []
    elif not dest.is_dir():
        print(f"Error: {dest} is not a folder.")
        return EXIT_CONFLICT
    else:
        stale = links_into_repo(dest, root)

    # Decide what to do with <dest>/repertoire before changing anything.
    action = "create"
    if os.path.lexists(managed):
        if is_link(managed):
            target = link_target(managed)
            if target == root:
                action = "keep"
            elif target is not None and is_within(target, root):
                action = "replace"
            else:
                shown = target if target is not None else "an unreadable target"
                print(f"Conflict: {managed} is {describe(managed)} to {shown}, outside this checkout ({root}).")
                print("Nothing was changed. If that link is no longer needed, remove it")
                print("(removing a link leaves the folder it points at intact), then run")
                print("this script again. To link that other checkout instead, run its own")
                print("copy of scripts/link_user_skills.py.")
                report_pending_stale(stale)
                return EXIT_CONFLICT
        else:
            print(f"Conflict: {managed} is {describe(managed)}, not a link.")
            print("Nothing was changed. Claude Code would load it in place of this checkout.")
            print("Move or rename it (for example to repertoire.old), then run this script again.")
            report_pending_stale(stale)
            return EXIT_CONFLICT

    try:
        for path, target in stale:
            report(dry_run, "remove", "Removed",
                   f"stale link {path} -> {target} (the {LINK_NAME} link already covers it)")
            if not dry_run:
                remove_link(path)

        if action == "keep":
            print(f"Already in place: {managed} -> {root}")
        elif action == "replace":
            old = link_target(managed)
            report(dry_run, "replace", "Replaced", f"{managed} -> {old} with a link to {root}")
            if not dry_run:
                remove_link(managed)
                create_link(managed, root)
        else:
            kind = "junction" if sys.platform == "win32" else "symbolic link"
            report(dry_run, "link", "Linked", f"{managed} -> {root} ({kind})")
            if not dry_run:
                create_link(managed, root)
    except OSError as exc:
        print(f"Error: {exc}")
        return EXIT_CONFLICT

    if not dry_run and link_target(managed) != root:
        print(f"Error: {managed} does not resolve to {root} after linking.")
        return EXIT_CONFLICT

    if dry_run:
        print("Dry run: nothing was changed.")
    else:
        print_next_steps(managed)
    return EXIT_OK


def report_pending_stale(stale: list[tuple[Path, Path]]) -> None:
    for path, target in stale:
        print(f"Once that is fixed, this script will also remove the stale link {path} -> {target}")


def unlink(dest: Path, root: Path, dry_run: bool) -> int:
    if not dest.is_dir():
        print(f"Nothing to remove: {dest} does not exist.")
        return EXIT_OK

    managed = dest / LINK_NAME
    to_remove = []
    if os.path.lexists(managed):
        target = link_target(managed) if is_link(managed) else None
        if target is not None and is_within(target, root):
            to_remove.append((managed, target))
        else:
            print(f"Left alone: {managed} is {describe(managed)}"
                  f"{f' to {target}' if target is not None else ''}, not a link into {root}.")
    to_remove.extend(links_into_repo(dest, root))

    if not to_remove:
        print(f"Nothing to remove: no links in {dest} point into {root}.")
        return EXIT_OK
    for path, target in to_remove:
        report(dry_run, "remove", "Removed", f"link {path} -> {target}")
        if not dry_run:
            try:
                remove_link(path)
            except OSError as exc:
                print(f"Error: {exc}")
                return EXIT_CONFLICT
    if dry_run:
        print("Dry run: nothing was changed.")
    else:
        print("The checkout itself is untouched. Start a new Claude Code session, or run")
        print("/reload-plugins, to stop loading repertoire@skills-dir.")
    return EXIT_OK


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="link_user_skills.py",
        description=(
            "Link this Repertoire checkout into Claude Code as the plugin\n"
            "repertoire@skills-dir, by creating <dest>/repertoire -> the repository root\n"
            "(a junction on Windows, a symbolic link elsewhere). Stale links in <dest>\n"
            "that point into this repository are removed. <dest>/synced is never touched."
        ),
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dest", type=Path, default=None,
        help="skills folder to link into (default: ~/.claude/skills)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print every action without changing anything",
    )
    parser.add_argument(
        "--unlink", action="store_true",
        help="remove the links this script manages: <dest>/repertoire and any other "
             "link in <dest> that points into this repository",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    if sys.version_info < (3, 12):
        print("Error: this script needs Python 3.12 or later.")
        return EXIT_CONFLICT

    root = repo_root()
    if not (root / ".claude-plugin" / "plugin.json").is_file():
        print(f"Error: {root} has no .claude-plugin/plugin.json, so it is not the Repertoire plugin root.")
        return EXIT_CONFLICT

    dest = (args.dest if args.dest is not None else default_dest()).expanduser()
    dest = Path(os.path.abspath(dest))
    if is_within(Path(os.path.realpath(dest)), root):
        print(f"Error: {dest} is inside this checkout; a link there would point at its own parent.")
        return EXIT_CONFLICT

    print(f"Repository: {root}")
    print(f"Skills folder: {dest}")
    if args.unlink:
        return unlink(dest, root, args.dry_run)
    return link(dest, root, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
