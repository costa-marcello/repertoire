"""Tests for scripts/link_user_skills.py.

Every run passes --dest with a temporary folder and points HOME and USERPROFILE
at a temporary folder too, so the real ~/.claude/skills is never touched. Most
tests run a copy of the script inside a throwaway fake repository, because the
script takes its repository root from its own location; that lets the tests
plant sentinel files in the link target without touching this checkout.

Run from the repository root:
    python -B -m unittest discover -s tests/plugin
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "link_user_skills.py"
SUBPROCESS_TIMEOUT_SECONDS = 120


def real(path: Path) -> str:
    return os.path.normcase(os.path.realpath(path))


def is_link(path: Path) -> bool:
    return path.is_junction() or path.is_symlink()


def make_link(link: Path, target: Path) -> None:
    """A junction on Windows (no admin rights needed), a symlink elsewhere."""
    link.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


def make_dangling_link(link: Path, target: Path) -> None:
    """A link whose target folder no longer exists, like an old renamed skill."""
    target.mkdir(parents=True)
    make_link(link, target)
    target.rmdir()


def remove_link(path: Path) -> None:
    if path.is_junction():
        os.rmdir(path)
        return
    try:
        os.unlink(path)
    except (IsADirectoryError, PermissionError):
        os.rmdir(path)


def remove_tree(path: Path) -> None:
    """Delete a folder without ever following a junction or symlink inside it."""
    if not os.path.lexists(path):
        return
    if is_link(path):
        remove_link(path)
        return
    with os.scandir(path) as entries:
        children = [Path(e.path) for e in entries]
    for child in children:
        if is_link(child):
            remove_link(child)
        elif child.is_dir():
            remove_tree(child)
        else:
            child.unlink()
    path.rmdir()


def snapshot(root: Path) -> list[tuple]:
    """Every entry under root, with link targets and file contents, not following links."""
    if not os.path.lexists(root):
        return []
    found = []
    for entry in sorted(os.scandir(root), key=lambda e: e.name):
        path = Path(entry.path)
        rel = path.relative_to(root).as_posix()
        if is_link(path):
            found.append((rel, "link", real(path)))
        elif path.is_dir():
            found.append((rel, "dir", ""))
            found.extend((f"{rel}/{r}", k, v) for r, k, v in snapshot(path))
        else:
            found.append((rel, "file", path.read_text(encoding="utf-8")))
    return found


class LinkScriptTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="link-skills-")).resolve()
        self.addCleanup(remove_tree, self.tmp)
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.dest = self.home / ".claude" / "skills"

        self.repo = self.tmp / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        shutil.copy2(SCRIPT, self.repo / "scripts" / SCRIPT.name)
        (self.repo / ".claude-plugin").mkdir()
        (self.repo / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "repertoire"}), encoding="utf-8")
        (self.repo / "skills" / "alpha").mkdir(parents=True)
        (self.repo / "skills" / "alpha" / "SKILL.md").write_text(
            "---\nname: alpha\n---\n", encoding="utf-8")
        (self.repo / "sentinel.txt").write_text("repo sentinel", encoding="utf-8")

        self.outside = self.tmp / "outside"
        self.outside.mkdir()
        (self.outside / "sentinel.txt").write_text("outside sentinel", encoding="utf-8")

    def run_script(self, *args: str, script: Path | None = None, dest: Path | None = None):
        script = script or self.repo / "scripts" / SCRIPT.name
        env = dict(os.environ)
        env.update({"HOME": str(self.home), "USERPROFILE": str(self.home)})
        env.pop("PYTHONIOENCODING", None)
        return subprocess.run(
            [sys.executable, "-B", str(script), "--dest", str(dest or self.dest), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env, timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )

    def link_or_skip(self, link: Path, target: Path, dangling: bool = False) -> None:
        try:
            (make_dangling_link if dangling else make_link)(link, target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"cannot create a directory link here: {exc}")

    def assert_repo_intact(self):
        self.assertEqual((self.repo / "sentinel.txt").read_text(encoding="utf-8"), "repo sentinel")
        self.assertTrue((self.repo / "skills" / "alpha" / "SKILL.md").is_file())
        self.assertTrue((self.repo / ".claude-plugin" / "plugin.json").is_file())
        self.assertEqual((self.outside / "sentinel.txt").read_text(encoding="utf-8"),
                         "outside sentinel")


class UsageTests(LinkScriptTestCase):
    def test_help_documents_exit_codes(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--help"],
                                capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT_SECONDS)
        self.assertEqual(result.returncode, 0)
        self.assertIn("exit codes:", result.stdout)
        for line in ("0  the link is in place", "1  conflict or error", "2  usage error"):
            self.assertIn(line, result.stdout)

    def test_unknown_flag_exits_2(self):
        result = self.run_script("--bogus")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(os.path.lexists(self.dest))

    def test_refuses_a_repo_without_plugin_manifest(self):
        (self.repo / ".claude-plugin" / "plugin.json").unlink()
        result = self.run_script()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(".claude-plugin/plugin.json", result.stdout)
        self.assertFalse(os.path.lexists(self.dest))

    def test_refuses_a_dest_inside_the_repo(self):
        inside = self.repo / ".claude" / "skills"
        result = self.run_script(dest=inside)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertFalse(os.path.lexists(inside))


class LinkTests(LinkScriptTestCase):
    def test_dry_run_changes_nothing(self):
        self.dest.mkdir(parents=True)
        self.link_or_skip(self.dest / "alpha", self.repo / "skills" / "alpha")
        (self.dest / "synced").mkdir()
        (self.dest / "synced" / "note.txt").write_text("app managed", encoding="utf-8")
        before = snapshot(self.dest)

        result = self.run_script("--dry-run")

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(snapshot(self.dest), before)
        self.assertIn("Would remove stale link", result.stdout)
        self.assertIn("Would link", result.stdout)
        self.assertIn("nothing was changed", result.stdout)

    def test_dry_run_does_not_create_a_missing_dest(self):
        result = self.run_script("--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Would create folder", result.stdout)
        self.assertFalse(os.path.lexists(self.dest))

    def test_real_run_links_this_checkout(self):
        # The one test that runs the real script: the link must resolve to this repo.
        result = self.run_script(script=SCRIPT)
        self.assertEqual(result.returncode, 0, result.stdout)
        link = self.dest / "repertoire"
        self.assertTrue(is_link(link))
        self.assertEqual(real(link), real(REPO))
        self.assertTrue((link / ".claude-plugin" / "plugin.json").is_file())
        self.assertIn("/repertoire:<skill>", result.stdout)
        self.assertIn("repertoire@skills-dir", result.stdout)
        self.assertIn("/reload-plugins", result.stdout)

        result = self.run_script("--unlink", script=SCRIPT)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(os.path.lexists(link))
        self.assertTrue((REPO / ".claude-plugin" / "plugin.json").is_file())

    def test_second_run_is_idempotent(self):
        first = self.run_script()
        self.assertEqual(first.returncode, 0, first.stdout)
        link = self.dest / "repertoire"
        self.assertEqual(real(link), real(self.repo))
        before = snapshot(self.dest)

        second = self.run_script()

        self.assertEqual(second.returncode, 0, second.stdout)
        self.assertIn("Already in place", second.stdout)
        self.assertEqual(snapshot(self.dest), before)

    def test_stale_links_into_the_repo_are_pruned(self):
        self.dest.mkdir(parents=True)
        self.link_or_skip(self.dest / "alpha", self.repo / "skills" / "alpha")
        self.link_or_skip(self.dest / "claude-md", self.repo / "skills" / "claude-md", dangling=True)
        self.link_or_skip(self.dest / "elsewhere", self.outside)
        (self.dest / "my-skill").mkdir()
        (self.dest / "my-skill" / "SKILL.md").write_text("---\nname: my-skill\n---\n",
                                                         encoding="utf-8")

        result = self.run_script()

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(os.path.lexists(self.dest / "alpha"))
        self.assertFalse(os.path.lexists(self.dest / "claude-md"))
        self.assertIn(str(self.dest / "alpha"), result.stdout)
        self.assertIn(str(self.dest / "claude-md"), result.stdout)
        self.assertEqual(real(self.dest / "elsewhere"), real(self.outside))
        self.assertTrue((self.dest / "my-skill" / "SKILL.md").is_file())
        self.assertEqual(real(self.dest / "repertoire"), real(self.repo))
        self.assert_repo_intact()

    def test_link_into_a_repo_subfolder_is_replaced(self):
        self.dest.mkdir(parents=True)
        self.link_or_skip(self.dest / "repertoire", self.repo / "skills")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Replaced", result.stdout)
        self.assertEqual(real(self.dest / "repertoire"), real(self.repo))
        self.assert_repo_intact()


class ConflictTests(LinkScriptTestCase):
    def test_link_pointing_outside_the_repo_is_left_alone(self):
        self.dest.mkdir(parents=True)
        self.link_or_skip(self.dest / "repertoire", self.outside)
        self.link_or_skip(self.dest / "alpha", self.repo / "skills" / "alpha")
        before = snapshot(self.dest)

        result = self.run_script()

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Conflict", result.stdout)
        self.assertIn("Nothing was changed", result.stdout)
        self.assertEqual(snapshot(self.dest), before)
        self.assertEqual(real(self.dest / "repertoire"), real(self.outside))
        self.assert_repo_intact()

    def test_real_folder_named_repertoire_is_left_alone(self):
        folder = self.dest / "repertoire"
        folder.mkdir(parents=True)
        (folder / "keep.txt").write_text("mine", encoding="utf-8")
        before = snapshot(self.dest)

        result = self.run_script()

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("real folder", result.stdout)
        self.assertEqual(snapshot(self.dest), before)

        result = self.run_script("--unlink")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Left alone", result.stdout)
        self.assertEqual(snapshot(self.dest), before)


class SyncedTests(LinkScriptTestCase):
    def test_synced_folder_and_its_contents_are_untouched(self):
        synced = self.dest / "synced"
        (synced / "some-plugin").mkdir(parents=True)
        (synced / "some-plugin" / "SKILL.md").write_text("app managed", encoding="utf-8")
        # Even a link into this repo inside synced/ must survive link and unlink.
        self.link_or_skip(synced / "alpha", self.repo / "skills" / "alpha")
        before = snapshot(synced)

        self.assertEqual(self.run_script().returncode, 0)
        self.assertEqual(snapshot(synced), before)
        self.assertEqual(self.run_script("--unlink").returncode, 0)
        self.assertEqual(snapshot(synced), before)

    def test_synced_link_into_the_repo_is_not_pruned(self):
        self.dest.mkdir(parents=True)
        self.link_or_skip(self.dest / "synced", self.repo / "skills")

        self.assertEqual(self.run_script().returncode, 0)
        self.assertEqual(real(self.dest / "synced"), real(self.repo / "skills"))
        self.assertEqual(self.run_script("--unlink").returncode, 0)
        self.assertEqual(real(self.dest / "synced"), real(self.repo / "skills"))


class UnlinkTests(LinkScriptTestCase):
    def test_unlink_removes_only_the_managed_links(self):
        self.assertEqual(self.run_script().returncode, 0)
        link = self.dest / "repertoire"
        self.assertEqual((link / "sentinel.txt").read_text(encoding="utf-8"), "repo sentinel")
        self.link_or_skip(self.dest / "elsewhere", self.outside)
        (self.dest / "mine").mkdir()
        (self.dest / "mine" / "SKILL.md").write_text("mine", encoding="utf-8")

        result = self.run_script("--unlink")

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(os.path.lexists(link))
        self.assertEqual(real(self.dest / "elsewhere"), real(self.outside))
        self.assertEqual((self.dest / "mine" / "SKILL.md").read_text(encoding="utf-8"), "mine")
        self.assert_repo_intact()

    def test_unlink_dry_run_changes_nothing(self):
        self.assertEqual(self.run_script().returncode, 0)
        before = snapshot(self.dest)
        result = self.run_script("--unlink", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Would remove link", result.stdout)
        self.assertEqual(snapshot(self.dest), before)

    def test_unlink_with_nothing_to_remove(self):
        result = self.run_script("--unlink")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Nothing to remove", result.stdout)
        self.assertFalse(os.path.lexists(self.dest))


if __name__ == "__main__":
    unittest.main()
