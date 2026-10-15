"""Checks the plugin packaging: the marketplace and its single repertoire
plugin, the repertoire manifest, the skills the plugin ships, and Cowork's
plugin limits.

Run from the repository root:
    python -B -m unittest discover -s tests/plugin
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
ROOT_PLUGIN = REPO

# The repertoire plugin's folder is the whole repository, and Cowork skips a
# plugin whose folder holds another .claude-plugin/plugin.json. These are the
# only .claude-plugin files the repository may contain.
ALLOWED_PLUGIN_FILES = {".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"}

# Fields that add components. The repertoire entry leaves them to plugin.json.
# No userConfig: desktop Cowork drops a plugin MCP server that references
# ${user_config.*} ("user_config is not supported on the desktop host bridge").
COMPONENT_FIELDS = {
    "skills", "commands", "agents", "hooks", "mcpServers", "lspServers",
    "outputStyles", "themes", "workflows", "experimental", "monitors",
    "userConfig", "channels", "settings", "types",
}

# Cowork refuses a plugin above these limits.
MAX_FILES = 5000
MAX_BYTES = 200 * 1024 * 1024
WALK_SKIP = {".git", ".claude", "__pycache__", "node_modules"}

CLI_TIMEOUT_SECONDS = 120


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def manifest(root: Path) -> dict:
    return load_json(root / ".claude-plugin" / "plugin.json")


def keys_anywhere(value) -> set[str]:
    """Every object key at any depth of a parsed JSON value."""
    found: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            found.add(key)
            found |= keys_anywhere(item)
    elif isinstance(value, list):
        for item in value:
            found |= keys_anywhere(item)
    return found


def frontmatter_name(skill_md: Path) -> str | None:
    lines = skill_md.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        match = re.match(r"^name:\s*(.+?)\s*$", line)
        if match:
            return match.group(1).strip("'\"")
    return None


def skill_dirs() -> list[Path]:
    return sorted(p for p in (REPO / "skills").iterdir() if p.is_dir())


def walk_files(root: Path):
    """Files under root, skipping WALK_SKIP folders and never following links."""
    with os.scandir(root) as entries:
        for entry in entries:
            path = Path(entry.path)
            if entry.is_symlink() or path.is_junction():
                continue
            if entry.is_dir(follow_symlinks=False):
                if entry.name not in WALK_SKIP:
                    yield from walk_files(path)
            elif entry.is_file(follow_symlinks=False):
                yield path


def shipped_files() -> tuple[list[Path], str]:
    """The files a git install of the plugin would carry, and how they were found."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=REPO, capture_output=True, timeout=CLI_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        result = None
    if result is not None and result.returncode == 0:
        names = result.stdout.decode("utf-8", errors="replace").split("\0")
        files = [REPO / name for name in names if name]
        return [f for f in files if f.is_file()], "git ls-files"
    return list(walk_files(REPO)), "a walk of the tree"


class MarketplaceTests(unittest.TestCase):
    def setUp(self):
        self.data = load_json(MARKETPLACE)

    def test_required_fields(self):
        self.assertEqual(self.data.get("name"), "repertoire")
        self.assertTrue(self.data.get("owner", {}).get("name"))
        self.assertTrue(self.data.get("description"))
        self.assertIsInstance(self.data.get("plugins"), list)
        # The "./" repertoire plugin is the whole repository, so a second
        # plugin here would sit inside it, which Cowork does not load.
        self.assertEqual([p.get("name") for p in self.data["plugins"]], ["repertoire"])

    def test_entries_point_at_existing_plugins_with_matching_names(self):
        for entry in self.data["plugins"]:
            with self.subTest(entry=entry.get("name")):
                source = entry.get("source")
                self.assertIsInstance(source, str)
                self.assertTrue(source.startswith("./"), source)
                self.assertNotIn("..", source)
                self.assertNotIn("\\", source)
                root = (REPO / source).resolve()
                self.assertTrue(root.is_dir(), f"{source} does not exist")
                self.assertTrue(root == REPO or root.is_relative_to(REPO))
                self.assertTrue(entry.get("description"))
                self.assertTrue((root / ".claude-plugin" / "plugin.json").is_file())
                self.assertEqual(entry["name"], manifest(root)["name"])

    def test_entries_declare_no_components_and_leave_strict_unset(self):
        # claude.ai does not accept a strict:false entry that only defines an
        # MCP server, so components stay in plugin.json.
        for entry in self.data["plugins"]:
            with self.subTest(entry=entry.get("name")):
                self.assertFalse(COMPONENT_FIELDS & entry.keys(), "component fields belong in plugin.json")
                self.assertNotIn("strict", entry)


class ManifestTests(unittest.TestCase):
    def test_no_version_anywhere(self):
        # Without a version, the plugin cache follows the commit.
        for path in (MARKETPLACE, ROOT_PLUGIN / ".claude-plugin" / "plugin.json"):
            with self.subTest(file=str(path.relative_to(REPO))):
                self.assertNotIn("version", keys_anywhere(load_json(path)))

    def test_repertoire_manifest(self):
        data = manifest(ROOT_PLUGIN)
        self.assertEqual(data["name"], "repertoire")
        self.assertTrue(data.get("description", "").startswith("Skills for Claude Code and Cowork"))
        self.assertTrue(data.get("author", {}).get("name"))
        self.assertEqual(data.get("homepage"), "https://github.com/costa-marcello/repertoire")
        self.assertEqual(data.get("repository"), "https://github.com/costa-marcello/repertoire")
        self.assertEqual(data.get("license"), "MIT")
        self.assertTrue(data.get("keywords"))
        # skills/ is scanned by default; a "skills" key would add a second scan.
        self.assertFalse(COMPONENT_FIELDS & data.keys())

    def test_no_plugin_settings(self):
        # Desktop Cowork drops an MCP server whose config uses plugin settings.
        for name, data in (("plugin.json", manifest(ROOT_PLUGIN)),
                           ("marketplace.json", load_json(MARKETPLACE))):
            with self.subTest(file=name):
                self.assertNotIn("userConfig", keys_anywhere(data))
                self.assertNotIn("${user_config.", json.dumps(data))


class LayoutTests(unittest.TestCase):
    def test_no_bin_hooks_or_mcp_json_at_plugin_root(self):
        # Cowork refuses a plugin with a top-level bin/. A root .mcp.json would
        # also be this repository's project MCP config, and hooks/ would run
        # in every session that loads the plugin.
        self.assertFalse((ROOT_PLUGIN / "bin").exists())
        self.assertFalse((ROOT_PLUGIN / ".mcp.json").exists())
        self.assertFalse((ROOT_PLUGIN / "hooks").exists())

    def test_every_skill_has_matching_name_and_readme_row(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        dirs = skill_dirs()
        self.assertTrue(dirs)
        for skill in dirs:
            with self.subTest(skill=skill.name):
                skill_md = skill / "SKILL.md"
                self.assertTrue(skill_md.is_file(), f"{skill.name} has no SKILL.md")
                self.assertEqual(frontmatter_name(skill_md), skill.name)
                self.assertRegex(readme, rf"(?<![\w-]){re.escape(skill.name)}(?![\w-])",
                                 f"{skill.name} is not mentioned in README.md")

    def test_only_root_plugin_manifest(self):
        # Cowork skips the "./" repertoire plugin when any other
        # .claude-plugin/ sits inside it, test fixtures included; the
        # Claude Code validator does not catch this.
        files, method = shipped_files()
        nested = sorted(
            rel for rel in (f.relative_to(REPO).as_posix() for f in files)
            if ".claude-plugin" in rel.split("/")[:-1] and rel not in ALLOWED_PLUGIN_FILES
        )
        self.assertEqual(nested, [], f"nested plugin files found by {method}")

    def test_skill_files_only_in_skill_folders(self):
        # Cowork lists every SKILL.md inside the plugin as a skill, so a
        # fixture skill under evals/ would show up next to the real ones.
        files, method = shipped_files()
        stray = sorted(
            rel for rel in (f.relative_to(REPO).as_posix() for f in files)
            if rel.rsplit("/", 1)[-1].casefold() == "skill.md"
            and not re.fullmatch(r"skills/[^/]+/SKILL\.md", rel)
        )
        self.assertEqual(stray, [], f"SKILL.md files outside skills/<name>/ found by {method}")

    def test_plugin_stays_within_cowork_limits(self):
        files, method = shipped_files()
        total = sum(f.stat().st_size for f in files)
        self.assertLess(len(files), MAX_FILES, f"{len(files)} files by {method}")
        self.assertLess(total, MAX_BYTES, f"{total} bytes by {method}")


class ClaudeValidateTests(unittest.TestCase):
    def validate(self, target: str):
        claude = shutil.which("claude")
        if claude is None:
            self.skipTest("the claude CLI is not on PATH")
        result = subprocess.run(
            [claude, "plugin", "validate", target],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=CLI_TIMEOUT_SECONDS,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validate_marketplace_and_root_plugin(self):
        self.validate(".")


if __name__ == "__main__":
    unittest.main()
