"""Checks the skill-folder block that finds a skill's own folder when a session
hands over a ${CLAUDE_SKILL_DIR} or base directory that points at a missing
folder (anthropics/claude-code#98790).

create-skill's bundled_resources.md holds the canonical block. Every skill that
bundles files (a references/, scripts/ or assets/ folder) must carry it word for
word in SKILL.md, with only its own name, a marker file it really bundles, and
its fallback filled in.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILLS = REPO / "skills"
CANONICAL = SKILLS / "create-skill" / "references" / "bundled_resources.md"
RESOURCE_DIRS = ("references", "scripts", "assets")
BLOCK_RE = re.compile(
    r"Use `\$\{CLAUDE_SKILL_DIR\}` unless it is blank(?P<body>[^\n]*?) If nothing matches, "
)
MARKER_RE = re.compile(r"if it holds `(?P<marker>[^`]+)`")
GLOB_RE = re.compile(r"last match Glob lists for `\*\*/(?P<name>[^/`]+)/(?P<marker>[^`]+)`")


def canonical_body() -> str:
    match = BLOCK_RE.search(CANONICAL.read_text(encoding="utf-8"))
    if match is None:
        raise AssertionError(f"{CANONICAL.name} has no skill-folder block")
    return match.group("body")


def skills_with_bundled_files():
    for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
        folder = skill_md.parent
        if any((folder / name).is_dir() for name in RESOURCE_DIRS):
            yield folder.name, skill_md.read_text(encoding="utf-8")


class SkillFolderBlock(unittest.TestCase):
    def test_each_skill_with_bundled_files_has_one_canonical_block(self):
        template = canonical_body()
        found = list(skills_with_bundled_files())
        self.assertTrue(found, "no skill bundles files")
        for name, text in found:
            with self.subTest(skill=name):
                blocks = BLOCK_RE.findall(text)
                self.assertEqual(len(blocks), 1, "needs exactly one skill-folder block")
                marker = MARKER_RE.search(blocks[0]).group("marker")
                expected = template.replace("<name>", name).replace("<marker>", marker)
                self.assertEqual(blocks[0], expected, "block drifted from bundled_resources.md")

    def test_glob_names_the_skill_and_a_real_marker_two_levels_down(self):
        for name, text in skills_with_bundled_files():
            with self.subTest(skill=name):
                glob = GLOB_RE.search(text)
                self.assertIsNotNone(glob, "the block has no Glob pattern")
                self.assertEqual(glob.group("name"), name)
                marker = glob.group("marker")
                self.assertEqual(len(marker.split("/")), 2, "the block climbs exactly two levels")
                self.assertTrue((SKILLS / name / marker).is_file(), f"{marker} is not bundled")
                self.assertIn(f"if it holds `{marker}`", text, "base-directory check uses another marker")


if __name__ == "__main__":
    unittest.main()
