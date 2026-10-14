"""Checks that create-skill and review-skill share one rule set.

review-skill/references/rules.md is canonical. create-skill's authoring_rules.md
must list the same IDs, titles, and severities, the scripts may only emit IDs
that exist in rules.md, and every script flag the docs mention must exist.
"""

import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CREATE = REPO / "skills" / "create-skill"
REVIEW = REPO / "skills" / "review-skill"
RULES = REVIEW / "references" / "rules.md"
AUTHORING = CREATE / "references" / "authoring_rules.md"
SCRIPTS = CREATE / "scripts"

# A rule-index row: | ID | Title | Severity | ...
ROW = re.compile(r"^\|\s*([MmS]\d+)\s*\|\s*([^|]+?)\s*\|\s*(Major|Minor|Style)\s*\|", re.MULTILINE)
RETIRED = {"m5", "m6", "m7", "m8"}
SCRIPT_NAMES = ("quick_validate.py", "init_skill.py", "package_skill.py", "security_scan.py")
# Validators may also emit F (grade-F triggers) and info/env lines that carry no rule.
NON_RULE_IDS = {"F"}


def rule_index(path):
    rows = ROW.findall(path.read_text(encoding="utf-8"))
    return {rule_id: (title, severity) for rule_id, title, severity in rows}


def skill_markdown_files():
    for skill in (CREATE, REVIEW):
        yield from sorted(skill.rglob("*.md"))


class RuleIndexAlignment(unittest.TestCase):
    def test_rules_md_has_index(self):
        index = rule_index(RULES)
        self.assertGreaterEqual(len(index), 20, "rules.md rule index looks incomplete")

    def test_authoring_rules_mirror_rules_md(self):
        canonical = rule_index(RULES)
        mirror = rule_index(AUTHORING)
        self.assertEqual(
            sorted(canonical), sorted(mirror),
            "rule IDs differ between rules.md and authoring_rules.md",
        )
        for rule_id, (title, severity) in canonical.items():
            self.assertEqual(mirror[rule_id], (title, severity), f"{rule_id} title or severity drifted")

    def test_retired_ids_not_reused(self):
        for path in (RULES, AUTHORING):
            self.assertFalse(RETIRED & set(rule_index(path)), f"{path.name} reuses a retired ID")

    def test_severity_matches_id_prefix(self):
        expected = {"M": "Major", "m": "Minor", "S": "Style"}
        for rule_id, (_, severity) in rule_index(RULES).items():
            self.assertEqual(severity, expected[rule_id[0]], f"{rule_id} has severity {severity}")


class ScriptRuleIds(unittest.TestCase):
    def test_validator_ids_exist_in_rules(self):
        known = set(rule_index(RULES)) | NON_RULE_IDS
        source = (SCRIPTS / "quick_validate.py").read_text(encoding="utf-8")
        used = set(re.findall(r"""["']((?:M|m|S)\d+|F)["']""", source))
        self.assertTrue(used, "no rule IDs found in quick_validate.py")
        self.assertFalse(used - known, f"quick_validate.py emits unknown IDs: {sorted(used - known)}")

    def test_security_scan_ids_exist_in_rules(self):
        known = set(rule_index(RULES))
        source = (SCRIPTS / "security_scan.py").read_text(encoding="utf-8")
        used = set(re.findall(r"\[((?:M|m)\d+)\]", source))
        self.assertFalse(used - known, f"security_scan.py emits unknown IDs: {sorted(used - known)}")


class DocumentedFlagsExist(unittest.TestCase):
    @staticmethod
    def help_flags(script):
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / script), "--help"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
        )
        return set(re.findall(r"--[a-z][a-z-]*", result.stdout))

    def test_flags_in_docs_match_help(self):
        flags = {script: self.help_flags(script) | {"--help"} for script in SCRIPT_NAMES}
        problems = []
        for md in skill_markdown_files():
            for number, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
                for script in SCRIPT_NAMES:
                    if script not in line:
                        continue
                    # Only flags written after the script name belong to it.
                    tail = line.split(script, 1)[1]
                    for flag in re.findall(r"(?<![\w-])--[a-z][a-z-]*", tail):
                        if flag not in flags[script]:
                            problems.append(f"{md.relative_to(REPO).as_posix()}:{number} {script} {flag}")
        self.assertFalse(problems, "docs mention flags the scripts do not accept:\n" + "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
