"""Tests for init_skill.py, package_skill.py, security_scan.py, and output encoding.

gitleaks is never required: tests that need a scan replace subprocess.run with
FakeGitleaks, which writes the --report-path file the way gitleaks does, so
run_gitleaks's return-code handling runs end to end.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import _helpers
from _helpers import CLEAN_BODY, CLEAN_NAME, make_skill, run_script, write_file

import init_skill
import package_skill
import quick_validate as qv
import security_scan

TODO_RE = re.compile(r"\[TODO[^\]]*\]")
FILLED_DESCRIPTION = 'description: "Converts CSV files into summary reports. Use when the user asks for a CSV summary."'
FILLED_TEXT = "the input file is summarised"
GITLEAKS_NAME = "gitleaks.exe" if os.name == "nt" else "gitleaks"
SCRIPT_NAMES = ("quick_validate.py", "init_skill.py", "package_skill.py", "security_scan.py")


def quietly(function, *args, **kwargs):
    """Call function with stdout and stderr captured; return (result, output)."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        result = function(*args, **kwargs)
    return result, buffer.getvalue()


def fill_template(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    text = re.sub(r"^description: .*$", FILLED_DESCRIPTION, text, count=1, flags=re.MULTILINE)
    skill_md.write_text(TODO_RE.sub(FILLED_TEXT, text), encoding="utf-8")


def make_dir_link(link: Path, target: Path) -> None:
    """A directory link: a junction on Windows (no admin rights needed), a symlink elsewhere."""
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


def make_executable(path: Path) -> Path:
    write_file(path, "not a real gitleaks\n")
    path.chmod(0o755)
    return path


def last_line(output: str) -> str:
    return output.strip().splitlines()[-1]


class FakeGitleaks:
    """Stands in for subprocess.run: records each gitleaks call and writes its report file."""

    def __init__(self, returncode=0, findings=None, raw_report=None, stderr="", reject_flag=False,
                 timeout=False):
        self.returncode = returncode
        self.findings = findings  # list of (relative file, rule id, line), written as absolute paths
        self.raw_report = raw_report  # literal report text, for broken reports
        self.stderr = stderr
        self.reject_flag = reject_flag
        self.timeout = timeout
        self.scans: list[dict] = []

    def __call__(self, command, **kwargs):
        command = list(command)
        if "--help" in command:
            return subprocess.CompletedProcess(command, 0, "", "")
        source = Path(command[2] if command[1] == "dir" else command[command.index("--source") + 1])
        self.scans.append({
            "command": command, "kwargs": kwargs, "source": source,
            "files": sorted(p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file()),
        })
        if self.timeout:
            raise subprocess.TimeoutExpired(command, kwargs.get("timeout"))
        if self.reject_flag and security_scan.IGNORE_ALLOW_FLAG in command:
            return subprocess.CompletedProcess(
                command, 1, "", f"Error: unknown flag: {security_scan.IGNORE_ALLOW_FLAG}")
        report = Path(command[command.index("--report-path") + 1])
        if self.raw_report is not None:
            report.write_text(self.raw_report, encoding="utf-8")
        elif self.findings is not None:
            report.write_text(json.dumps([
                {"RuleID": rule, "File": str(source / rel), "StartLine": line} for rel, rule, line in self.findings
            ]), encoding="utf-8")
        return subprocess.CompletedProcess(command, self.returncode, "", self.stderr)


class TempDirCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name).resolve()

    def tearDown(self) -> None:
        self._tmp.cleanup()


class InitSkill(TempDirCase):
    def init(self, *args: str) -> int:
        code, _ = quietly(init_skill.main, list(args))
        return code

    def test_template_fails_only_on_todo_placeholders(self):
        self.assertEqual(0, self.init("demo-skill", "--path", str(self.tmp)))
        findings = qv.collect_findings(self.tmp / "demo-skill")
        self.assertTrue(findings)
        self.assertEqual({("M9", "major", "definitive")},
                         {(f.rule_id, f.severity, f.confidence) for f in findings})
        self.assertTrue(all("[TODO" in f.message for f in findings))

    def test_filled_template_has_zero_findings(self):
        for fork in (False, True):
            name = "forked-skill" if fork else "inline-skill"
            args = [name, "--path", str(self.tmp)] + (["--fork"] if fork else [])
            self.assertEqual(0, self.init(*args))
            skill = self.tmp / name
            fill_template(skill)
            self.assertEqual([], [f.format() for f in qv.collect_findings(skill)], name)
            result = run_script("quick_validate.py", str(skill))
            self.assertEqual(0, result.returncode, result.stdout)
            self.assertEqual("RESULT major=0 minor=0 style=0 checks=0", result.stdout.strip())

    def test_fork_is_opt_in_and_never_adds_agent(self):
        self.init("plain-skill", "--path", str(self.tmp))
        self.init("fork-skill", "--path", str(self.tmp), "--fork")
        plain = (self.tmp / "plain-skill" / "SKILL.md").read_text(encoding="utf-8")
        forked = (self.tmp / "fork-skill" / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("context:", plain)
        self.assertIn("context: fork", forked)
        self.assertNotIn("agent:", forked)
        self.assertNotIn("license:", plain)

    def test_resources_and_no_placeholder_files(self):
        self.init("res-skill", "--path", str(self.tmp), "--resources", "scripts,assets")
        skill = self.tmp / "res-skill"
        self.assertTrue((skill / "scripts").is_dir())
        self.assertTrue((skill / "assets").is_dir())
        self.assertFalse((skill / "references").exists())
        for placeholder in qv.INIT_PLACEHOLDER_FILES:
            self.assertFalse((skill / placeholder).exists(), placeholder)
        self.assertEqual(3, len(json.loads((skill / "evals" / "evals.json").read_text())["evals"]))
        queries = json.loads((skill / "evals" / "trigger_queries.json").read_text())
        self.assertEqual((5, 5), (sum(q["should_trigger"] for q in queries),
                                  sum(not q["should_trigger"] for q in queries)))

    def test_rejects_bad_names_and_creates_nothing(self):
        for name in ("../evil", "Bad_Name", "a/b", "trailing-", "double--hyphen", "synced", "x" * 65):
            self.assertEqual(1, self.init(name, "--path", str(self.tmp)), name)
        self.assertEqual([], list(self.tmp.iterdir()))
        self.assertFalse((self.tmp.parent / "evil").exists())

    def test_rejects_existing_directory_and_leaves_it_alone(self):
        existing = self.tmp / "taken"
        write_file(existing / "keep.txt", "keep\n")
        self.assertEqual(1, self.init("taken", "--path", str(self.tmp)))
        self.assertEqual(["keep.txt"], [p.name for p in existing.iterdir()])

    def failing_second_write(self, calls):
        real_write = init_skill._write_text

        def failing_write(path, text):
            calls.append(path)
            if len(calls) == 2:
                raise OSError(28, "No space left on device")
            real_write(path, text)

        return mock.patch.object(init_skill, "_write_text", side_effect=failing_write)

    def test_rollback_on_write_failure(self):
        calls = []
        with self.failing_second_write(calls):
            self.assertEqual(1, self.init("half-skill", "--path", str(self.tmp)))
        self.assertEqual(2, len(calls))
        self.assertFalse((self.tmp / "half-skill").exists())

    def test_rollback_removes_parent_folders_it_created(self):
        calls = []
        with self.failing_second_write(calls):
            self.assertEqual(1, self.init("half-skill", "--path", str(self.tmp / "c" / "new" / "parent")))
        self.assertEqual(2, len(calls))
        self.assertEqual([], list(self.tmp.iterdir()), "parent folders created by init were left behind")

    def test_rollback_keeps_existing_parents_and_their_files(self):
        write_file(self.tmp / "c" / "keep.txt", "keep\n")
        calls = []
        with self.failing_second_write(calls):
            self.assertEqual(1, self.init("half-skill", "--path", str(self.tmp / "c" / "new")))
        self.assertEqual(["keep.txt"], [p.name for p in (self.tmp / "c").iterdir()])

    def test_rollback_when_the_skill_folder_cannot_be_made(self):
        real_mkdir = Path.mkdir

        def failing_mkdir(path, *args, **kwargs):
            if path.name == "blocked-skill":
                raise OSError(13, "Permission denied")
            return real_mkdir(path, *args, **kwargs)

        with mock.patch.object(Path, "mkdir", failing_mkdir):
            self.assertEqual(1, self.init("blocked-skill", "--path", str(self.tmp / "made" / "here")))
        self.assertEqual([], list(self.tmp.iterdir()))

    def test_rollback_on_unexpected_error(self):
        with mock.patch.object(init_skill, "render_evals", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                quietly(init_skill.main, ["boom-skill", "--path", str(self.tmp / "new")])
        self.assertEqual([], list(self.tmp.iterdir()))

    def test_unknown_resource_is_a_usage_error(self):
        with self.assertRaises(SystemExit) as raised:
            quietly(init_skill.main, ["x-skill", "--path", str(self.tmp), "--resources", "scripts,bin"])
        self.assertEqual(2, raised.exception.code)
        self.assertFalse((self.tmp / "x-skill").exists())


class SkillFiles(TempDirCase):
    def shipped(self, skill: Path, include_evals: bool = False) -> set[str]:
        return {p.relative_to(skill).as_posix() for p in security_scan.iter_skill_files(skill, include_evals)}

    def test_iter_skill_files_shared_exclusions(self):
        skill = make_skill(self.tmp)
        excluded = (
            "scripts/__pycache__/run.cpython-313.pyc", "node_modules/x/index.js", ".git/config", ".env",
            ".env.local", ".envrc", "references/.env/production", "assets/.env", "old.zip", "assets/starter.zip",
            ".DS_Store", "Thumbs.db", "scripts/stale.pyc", security_scan.MARKER_NAME,
            ".venv/Lib/site-packages/pkg.py", "venv/bin/activate", "references/node_modules/notes.md",
        )
        kept = ("scripts/run.py", "references/guide.md", ".gitignore", "scripts/evals/score.py",
                "assets/.env.example")
        for rel in excluded + kept:
            write_file(skill / rel, "x\n")
        self.assertEqual({"SKILL.md", *kept}, self.shipped(skill))
        self.assertEqual({"SKILL.md", *kept, "evals/evals.json", "evals/trigger_queries.json"},
                         self.shipped(skill, include_evals=True))

    def test_exclusion_reason_names_the_rule(self):
        self.assertIsNone(security_scan.exclusion_reason("scripts/evals/score.py"))
        self.assertIsNone(security_scan.exclusion_reason("assets/.env.example"))
        self.assertIn("evals/", security_scan.exclusion_reason("evals/evals.json"))
        self.assertIsNone(security_scan.exclusion_reason("evals/evals.json", include_evals=True))
        self.assertIn(".zip", security_scan.exclusion_reason("assets/starter.zip"))
        self.assertIn(".env", security_scan.exclusion_reason(".env/production"))
        self.assertIn("node_modules", security_scan.exclusion_reason("references/node_modules/notes.md"))

    def test_directory_links_are_listed_not_followed(self):
        outside = self.tmp / "outside"
        write_file(outside / "secret.txt", "TOKEN=abc\n")
        skill = make_skill(self.tmp / "src")
        make_dir_link(skill / "assets", outside)
        make_dir_link(skill / "evals" / "shared", outside)
        self.assertTrue(security_scan.is_link(skill / "assets"))
        self.assertNotIn("assets/secret.txt", self.shipped(skill, include_evals=True))
        self.assertEqual(["assets"], [p.relative_to(skill).as_posix() for p in security_scan.skill_links(skill)])
        self.assertEqual(["assets", "evals/shared"],
                         [p.relative_to(skill).as_posix() for p in security_scan.skill_links(skill, True)])

    @unittest.skipIf(os.name == "nt", "file symlinks need admin rights or developer mode on Windows")
    def test_file_symlinks_are_listed_not_followed(self):
        write_file(self.tmp / "credentials", "secret\n")
        skill = make_skill(self.tmp / "src")
        (skill / "references").mkdir()
        os.symlink(self.tmp / "credentials", skill / "references" / "x.md")
        self.assertNotIn("references/x.md", self.shipped(skill))
        self.assertEqual(["references/x.md"],
                         [p.relative_to(skill).as_posix() for p in security_scan.skill_links(skill)])

    def test_hash_under_dot_folder_is_real_stable_and_content_sensitive(self):
        skill = make_skill(self.tmp / ".claude" / "skills")
        empty = hashlib.sha256().hexdigest()
        first = security_scan.calculate_skill_hash(skill)
        self.assertTrue(first)
        self.assertNotEqual(empty, first, "no files were hashed under the .claude folder")
        self.assertEqual(first, security_scan.calculate_skill_hash(skill))
        write_file(skill / "evals" / "extra.json", "[]")
        write_file(skill / "scripts" / "__pycache__" / "a.pyc", "x")
        write_file(skill / security_scan.MARKER_NAME, "marker")
        self.assertEqual(first, security_scan.calculate_skill_hash(skill), "excluded files changed the hash")
        with open(skill / "SKILL.md", "a", encoding="utf-8") as handle:
            handle.write("More text.\n")
        self.assertNotEqual(first, security_scan.calculate_skill_hash(skill))

    def test_hash_ignores_line_endings(self):
        lf = make_skill(self.tmp / "lf")
        crlf = make_skill(self.tmp / "crlf", newline="\r\n")
        self.assertEqual(security_scan.calculate_skill_hash(lf), security_scan.calculate_skill_hash(crlf))

    def test_hash_ignores_line_endings_in_non_utf8_text(self):
        lf = make_skill(self.tmp / "lf")
        crlf = make_skill(self.tmp / "crlf")
        (lf / "legacy.txt").write_bytes(b"caf\xe9\nline\n")  # cp1252, not valid UTF-8
        (crlf / "legacy.txt").write_bytes(b"caf\xe9\r\nline\r\n")
        self.assertEqual(security_scan.calculate_skill_hash(lf), security_scan.calculate_skill_hash(crlf))

    def test_hash_keeps_line_endings_in_binary_files(self):
        lf = make_skill(self.tmp / "lf")
        crlf = make_skill(self.tmp / "crlf")
        (lf / "image.bin").write_bytes(b"\x00\x01\n")
        (crlf / "image.bin").write_bytes(b"\x00\x01\r\n")
        self.assertNotEqual(security_scan.calculate_skill_hash(lf), security_scan.calculate_skill_hash(crlf))

    def test_hash_keeps_file_boundaries(self):
        one = make_skill(self.tmp / "one")
        two = make_skill(self.tmp / "two")
        (one / "t.md").write_bytes(b"foo\0u.md\0bar")
        (two / "t.md").write_bytes(b"foo")
        (two / "u.md").write_bytes(b"bar")
        self.assertNotEqual(security_scan.calculate_skill_hash(one), security_scan.calculate_skill_hash(two))


class SecurityScan(TempDirCase):
    FAKE_EXE = "/opt/fake/bin/gitleaks"

    def scan(self, *args: str, fake: FakeGitleaks | None = None, lookup=None):
        lookup = lookup or security_scan.GitleaksLookup(self.FAKE_EXE)
        with mock.patch.object(security_scan, "find_gitleaks", return_value=lookup), \
             mock.patch.object(security_scan.subprocess, "run", fake or FakeGitleaks()):
            return quietly(security_scan.main, list(args))

    def test_no_marker_writes_nothing(self):
        skill = make_skill(self.tmp)
        before = sorted(p.name for p in skill.rglob("*"))
        code, output = self.scan(str(skill), "--no-marker", "--verbose")
        self.assertEqual(0, code, output)
        self.assertFalse((skill / security_scan.MARKER_NAME).exists())
        self.assertEqual(before, sorted(p.name for p in skill.rglob("*")))
        self.assertEqual("RESULT secrets=0 leads=0", last_line(output))

    def test_clean_scan_runs_the_resolved_gitleaks_safely_and_writes_a_matching_marker(self):
        skill = make_skill(self.tmp)
        shipped = sorted(p.relative_to(skill).as_posix() for p in skill.rglob("*") if p.is_file())
        fake = FakeGitleaks(returncode=0)
        code, output = self.scan(str(skill), fake=fake)
        self.assertEqual(0, code, output)
        self.assertEqual((True, "security marker matches the current content"),
                         package_skill.validate_security_marker(skill))
        self.assertEqual("RESULT secrets=0 leads=0", last_line(output))
        self.assertEqual(1, len(fake.scans))
        scan = fake.scans[0]
        self.assertEqual(self.FAKE_EXE, scan["command"][0])
        self.assertIn(security_scan.IGNORE_ALLOW_FLAG, scan["command"])
        # gitleaks scans a copy of the skill's regular files, never the skill folder itself.
        self.assertNotEqual(skill, scan["source"])
        self.assertEqual(skill.name, scan["source"].name)
        self.assertEqual(shipped, scan["files"])
        work = Path(scan["kwargs"]["cwd"])
        self.assertNotEqual(Path.cwd().resolve(), work.resolve())
        self.assertFalse(work.exists(), "the temporary working folder was left behind")
        self.assertIs(subprocess.DEVNULL, scan["kwargs"]["stdin"])

    def test_leaks_found_with_findings_exit_2_without_marker(self):
        skill = make_skill(self.tmp)
        fake = FakeGitleaks(returncode=2, findings=[("scripts/a.py", "generic-api-key", 3)])
        code, output = self.scan(str(skill), fake=fake)
        self.assertEqual(2, code, output)
        self.assertIn("[M10] major definitive scripts/a.py:3 generic-api-key (CRITICAL)", output)
        self.assertEqual("RESULT secrets=1 leads=0", last_line(output))
        self.assertFalse((skill / security_scan.MARKER_NAME).exists())

    def test_high_severity_findings_exit_1(self):
        skill = make_skill(self.tmp)
        fake = FakeGitleaks(returncode=2, findings=[("SKILL.md", "private-url", 9)])
        code, output = self.scan(str(skill), fake=fake)
        self.assertEqual(1, code, output)
        self.assertEqual("RESULT secrets=1 leads=0", last_line(output))

    def test_leaks_code_with_an_unusable_report_is_a_scan_error(self):
        for number, raw in enumerate(("{}", "null", "[]", "[1]", '{"findings": []}', "", '[{"RuleID": "x"')):
            skill = make_skill(self.tmp / f"case-{number}")
            code, output = self.scan(str(skill), fake=FakeGitleaks(returncode=2, raw_report=raw))
            self.assertEqual(4, code, f"report {raw!r}: {output}")
            self.assertNotIn("[PASS] gitleaks", output)
            self.assertFalse((skill / security_scan.MARKER_NAME).exists(), raw)

    def test_leaks_code_without_a_report_is_a_scan_error(self):
        skill = make_skill(self.tmp)
        code, output = self.scan(str(skill), fake=FakeGitleaks(returncode=2))
        self.assertEqual(4, code, output)
        self.assertFalse((skill / security_scan.MARKER_NAME).exists())

    def test_gitleaks_error_code_is_a_scan_error(self):
        skill = make_skill(self.tmp)
        code, output = self.scan(str(skill), fake=FakeGitleaks(returncode=1, stderr="bad config"))
        self.assertEqual(4, code, output)
        self.assertIn("gitleaks exited with code 1: bad config", output)
        self.assertFalse((skill / security_scan.MARKER_NAME).exists())

    def test_timeout_is_a_scan_error(self):
        skill = make_skill(self.tmp)
        code, output = self.scan(str(skill), fake=FakeGitleaks(timeout=True))
        self.assertEqual(4, code, output)
        self.assertIn("did not finish", output)

    def test_rejected_ignore_allow_flag_retries_without_it(self):
        skill = make_skill(self.tmp)
        fake = FakeGitleaks(returncode=0, reject_flag=True)
        code, output = self.scan(str(skill), "--no-marker", fake=fake)
        self.assertEqual(0, code, output)
        self.assertEqual(2, len(fake.scans))
        self.assertIn(security_scan.IGNORE_ALLOW_FLAG, fake.scans[0]["command"])
        self.assertNotIn(security_scan.IGNORE_ALLOW_FLAG, fake.scans[1]["command"])
        self.assertIn("[WARN] this gitleaks does not accept", output)

    def test_gitleaks_configs_are_reported_and_left_out_of_the_scan(self):
        skill = make_skill(self.tmp)
        write_file(skill / ".gitleaks.toml", "[allowlist]\npaths = ['.*']\n")
        write_file(skill / "references" / ".gitleaksignore", "*\n")
        write_file(skill / "scripts" / "run.py", "print('ok')\n")
        fake = FakeGitleaks(returncode=0)
        code, output = self.scan(str(skill), "--no-marker", fake=fake)
        self.assertEqual(0, code, output)
        self.assertIn("[M10] major check .gitleaks.toml:0 Gitleaks config", output)
        self.assertIn("[M10] major check references/.gitleaksignore:0 Gitleaks config", output)
        self.assertEqual("RESULT secrets=0 leads=2", last_line(output))
        scan = fake.scans[0]
        self.assertNotEqual(skill, scan["source"], "the skill itself was scanned, configs included")
        self.assertEqual(skill.name, scan["source"].name)
        self.assertIn("SKILL.md", scan["files"])
        self.assertIn("scripts/run.py", scan["files"])
        self.assertNotIn(".gitleaks.toml", scan["files"])
        self.assertNotIn("references/.gitleaksignore", scan["files"])
        self.assertFalse(scan["source"].exists(), "the temporary copy was left behind")
        self.assertTrue((skill / ".gitleaks.toml").exists(), "the scan changed the target")

    def test_findings_in_the_copy_are_reported_relative_to_the_skill(self):
        skill = make_skill(self.tmp)
        write_file(skill / ".gitleaks.toml", "title = 'x'\n")
        fake = FakeGitleaks(returncode=2, findings=[("scripts/a.py", "aws-access-token", 4)])
        code, output = self.scan(str(skill), fake=fake)
        self.assertEqual(2, code, output)
        self.assertIn("[M10] major definitive scripts/a.py:4 aws-access-token", output)

    def test_pattern_leads_map_to_rules(self):
        skill = make_skill(self.tmp)
        write_file(skill / "scripts" / "net.py", (
            "import requests\n"
            "requests.get('https://example.com/data')\n"
            "PATH = 'C:\\\\Users\\\\jsmith\\\\data'\n"
            "OTHER = r'C:\\Users\\jsmith\\data'\n"
            "HOME = '/Users/username/data/'\n"
            "CONTACT = 'jane.doe@corp.io'\n"
        ))
        issues = security_scan.scan_skill_patterns(skill)
        rules = sorted((i.rule, i.line) for i in issues)
        self.assertIn(("[M10] major check", 2), rules)
        self.assertIn(("[m11] minor check", 3), rules)
        self.assertIn(("[m11] minor check", 4), rules, "single-backslash Windows path not detected")
        self.assertNotIn(("[m11] minor check", 5), rules, "placeholder user name flagged")
        self.assertIn(("[info]", 6), rules)
        self.assertTrue(all(i.file == "scripts/net.py" for i in issues))

    def test_pattern_leads_do_not_change_exit_code_and_are_counted(self):
        skill = make_skill(self.tmp)
        write_file(skill / "scripts" / "net.py", "import os\nos.system('ls')\nMAIL = 'jane.doe@corp.io'\n")
        code, output = self.scan(str(skill), "--verbose", "--no-marker")
        self.assertEqual(0, code)
        self.assertIn("[M10] major check scripts/net.py:2 Dangerous code", output)
        self.assertIn("[info] scripts/net.py:3 Email address", output)
        self.assertEqual("RESULT secrets=0 leads=1", last_line(output))

    def test_linked_gitleaks_config_is_flagged_and_never_scanned(self):
        outside = write_file(self.tmp / "elsewhere" / "allow-all.toml", "[allowlist]\npaths = ['.*']\n")
        skill = make_skill(self.tmp / "src")
        try:
            os.symlink(outside, skill / ".gitleaks.toml")
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"cannot create a file symlink here ({exc})")
        fake = FakeGitleaks(returncode=0)
        code, output = self.scan(str(skill), "--no-marker", fake=fake)
        self.assertEqual(0, code, output)
        self.assertIn("[M10] major check .gitleaks.toml:0 Gitleaks config", output)
        self.assertNotIn(".gitleaks.toml", fake.scans[0]["files"])

    def test_links_are_reported_as_info(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        skill = make_skill(self.tmp / "src")
        make_dir_link(skill / "assets", outside)
        code, output = self.scan(str(skill), "--no-marker")
        self.assertEqual(0, code, output)
        self.assertIn("[info] assets:0 Link not followed", output)
        self.assertEqual("RESULT secrets=0 leads=0", last_line(output))

    def test_missing_gitleaks_exits_3_without_marker(self):
        skill = make_skill(self.tmp)
        code, output = self.scan(str(skill), lookup=security_scan.GitleaksLookup(None))
        self.assertEqual(3, code)
        self.assertIn("winget install gitleaks", output)
        self.assertFalse((skill / security_scan.MARKER_NAME).exists())
        self.assertEqual("RESULT secrets=0 leads=0", last_line(output))

    def test_refused_gitleaks_is_named_and_never_run(self):
        skill = make_skill(self.tmp)
        planted = str(skill / GITLEAKS_NAME)
        fake = FakeGitleaks()
        code, output = self.scan(str(skill), fake=fake, lookup=security_scan.GitleaksLookup(None, (planted,)))
        self.assertEqual(3, code)
        self.assertIn(f"[WARN] ignored {planted}", output)
        self.assertEqual([], fake.scans)

    def test_internal_error_exits_4_with_one_line(self):
        skill = make_skill(self.tmp)
        with mock.patch.object(security_scan, "find_gitleaks_config", side_effect=RuntimeError("boom\nsecond")):
            code, output = quietly(security_scan.main, [str(skill)])
        self.assertEqual(4, code)
        error_lines = [line for line in output.splitlines() if "[ERROR]" in line]
        self.assertEqual(1, len(error_lines), output)
        self.assertIn("internal error", error_lines[0])
        self.assertIn("RuntimeError: boom second", error_lines[0])
        self.assertNotIn("Traceback", output)

    def test_usage_error_exits_4(self):
        with self.assertRaises(SystemExit) as raised:
            quietly(security_scan.main, ["--no-such-flag"])
        self.assertEqual(4, raised.exception.code)

    def test_gitleaks_command_prefers_dir_and_falls_back(self):
        skill = make_skill(self.tmp)
        command = security_scan._gitleaks_command(self.FAKE_EXE, skill, "r.json", use_dir=True)
        self.assertEqual([self.FAKE_EXE, "dir", str(skill)], command[:3])
        self.assertIn(security_scan.IGNORE_ALLOW_FLAG, command)
        command = security_scan._gitleaks_command(self.FAKE_EXE, skill, "r.json", use_dir=False, ignore_allow=False)
        self.assertEqual([self.FAKE_EXE, "detect", "--no-git"], command[:3])
        self.assertIn("--exit-code", command)
        self.assertNotIn(security_scan.IGNORE_ALLOW_FLAG, command)


class FindGitleaks(TempDirCase):
    def setUp(self) -> None:
        super().setUp()
        self.skill = make_skill(self.tmp / "src")
        self.cwd = self.tmp / "work"
        self.cwd.mkdir()

    def test_skips_the_current_folder_the_skill_and_relative_entries(self):
        in_cwd = make_executable(self.cwd / GITLEAKS_NAME)
        in_skill = make_executable(self.skill / "bin" / GITLEAKS_NAME)
        good = make_executable(self.tmp / "tools" / GITLEAKS_NAME)
        search = os.pathsep.join([str(self.skill / "bin"), str(self.cwd), "", "relative/bin", str(good.parent)])
        lookup = security_scan.find_gitleaks(self.skill, search_path=search, cwd=self.cwd)
        self.assertEqual(str(good.resolve()), lookup.path)
        self.assertTrue(Path(lookup.path).is_absolute())
        self.assertIn(str(in_cwd), lookup.refused)
        self.assertIn(str(in_skill), lookup.refused)

    def test_a_planted_gitleaks_alone_is_refused(self):
        make_executable(self.cwd / GITLEAKS_NAME)
        lookup = security_scan.find_gitleaks(self.skill, search_path=str(self.cwd), cwd=self.cwd)
        self.assertIsNone(lookup.path)
        self.assertEqual((str(self.cwd / GITLEAKS_NAME),), lookup.refused)

    def test_nothing_on_path(self):
        lookup = security_scan.find_gitleaks(self.skill, search_path=str(self.tmp / "empty"), cwd=self.cwd)
        self.assertEqual(security_scan.GitleaksLookup(None, ()), lookup)


class PackageSkill(TempDirCase):
    def make_packageable(self, body: str = CLEAN_BODY) -> Path:
        skill = make_skill(self.tmp / "src", body=body)
        write_file(skill / "scripts" / "run.py", "print('ok')\n")
        write_file(skill / "scripts" / "evals" / "score.py", "print('score')\n")
        write_file(skill / "scripts" / "__pycache__" / "run.cpython-313.pyc", "x")
        write_file(skill / "assets" / ".env.example", "TOKEN=\n")
        write_file(skill / ".env", "TOKEN=abc\n")
        write_file(skill / "assets" / ".env" / "production", "TOKEN=abc\n")  # a .env folder, not a file
        write_file(skill / ".venv" / "Lib" / "pkg.py", "x\n")
        write_file(skill / "old.zip", "x")
        security_scan.create_security_marker(skill)
        return skill

    def package(self, skill: Path):
        return quietly(package_skill.main, [str(skill), str(self.tmp / "dist")])

    def test_zip_excludes_authoring_and_cache_files(self):
        skill = self.make_packageable()
        out = self.tmp / "dist"
        code, output = self.package(skill)
        self.assertEqual(0, code, output)
        with zipfile.ZipFile(out / f"{CLEAN_NAME}.zip") as archive:
            names = set(archive.namelist())
        self.assertEqual({f"{CLEAN_NAME}/SKILL.md", f"{CLEAN_NAME}/scripts/run.py",
                          f"{CLEAN_NAME}/scripts/evals/score.py", f"{CLEAN_NAME}/assets/.env.example"}, names)
        self.assertEqual([f"{CLEAN_NAME}.zip"], [p.name for p in out.iterdir()], "partial file left behind")

    @unittest.skipIf(os.name == "nt", "Windows has no group or other permission bits")
    def test_zip_gets_the_default_permissions(self):
        skill = self.make_packageable()
        code, output = self.package(skill)
        self.assertEqual(0, code, output)
        mask = os.umask(0)
        os.umask(mask)
        mode = (self.tmp / "dist" / f"{CLEAN_NAME}.zip").stat().st_mode & 0o777
        self.assertEqual(0o666 & ~mask, mode)

    def test_refuses_output_inside_skill(self):
        skill = self.make_packageable()
        for target in (skill, skill / "dist"):
            code, output = quietly(package_skill.main, [str(skill), str(target)])
            self.assertEqual(1, code)
            self.assertIn("inside the skill", output)
        self.assertFalse((skill / "dist").exists())
        self.assertEqual([], list(skill.rglob("*.zip.partial")))
        self.assertFalse((skill / f"{CLEAN_NAME}.zip").exists())

    def test_stale_marker_blocks_packaging(self):
        skill = self.make_packageable()
        with open(skill / "SKILL.md", "a", encoding="utf-8") as handle:
            handle.write("Changed.\n")
        code, output = self.package(skill)
        self.assertEqual(1, code)
        self.assertIn(f"python scripts/security_scan.py {skill.resolve()}", output)

    def test_unreadable_marker_message_carries_the_error_text(self):
        skill = self.make_packageable()
        (skill / security_scan.MARKER_NAME).write_bytes(b"Content hash: \xff\xfe")
        ok, message = package_skill.validate_security_marker(skill)
        self.assertFalse(ok)
        self.assertIn("can't decode byte", message)

    def test_definitive_major_blocks_packaging(self):
        skill = self.make_packageable()
        text = (skill / "SKILL.md").read_text(encoding="utf-8").replace(f"name: {CLEAN_NAME}", "name: wrong-name")
        (skill / "SKILL.md").write_text(text, encoding="utf-8")
        security_scan.create_security_marker(skill)
        code, output = self.package(skill)
        self.assertEqual(1, code)
        self.assertIn("[M9]", output)
        self.assertIn("definitive Major", output)

    def test_environment_error_is_not_reported_as_a_major(self):
        skill = self.make_packageable()
        env_message = "[env] PyYAML is required: python -m pip install pyyaml"
        with mock.patch.object(package_skill, "validate_skill", return_value=(False, env_message, [])):
            code, output = self.package(skill)
        self.assertEqual(1, code)
        self.assertIn("quick_validate could not run", output)
        self.assertIn(env_message, output)
        self.assertNotIn("definitive Major", output)

    def test_refuses_links_and_names_them(self):
        outside = self.tmp / "outside"
        write_file(outside / "secret.txt", "TOKEN=abc\n")
        skill = self.make_packageable()
        make_dir_link(skill / "references" / "shared", outside)
        security_scan.create_security_marker(skill)
        code, output = self.package(skill)
        self.assertEqual(1, code, output)
        self.assertIn("references/shared is a symlink or junction", output)
        self.assertFalse((self.tmp / "dist" / f"{CLEAN_NAME}.zip").exists())

    def test_refuses_references_to_files_the_zip_leaves_out(self):
        body = CLEAN_BODY.replace(
            "4. Verify:",
            "4. Unpack `assets/starter.zip` and read [notes](references/node_modules/notes.md).\n"
            "5. Copy `assets/.env.example`, run `python scripts/evals/score.py`, and see `evals/evals.json`.\n"
            "6. Verify:",
        )
        skill = make_skill(self.tmp / "src", body=body)
        for rel in ("assets/starter.zip", "references/node_modules/notes.md", "assets/.env.example",
                    "scripts/evals/score.py"):
            write_file(skill / rel, "x\n")
        self.assertEqual([], [f.format() for f in qv.collect_findings(skill) if f.rule_id == "M5"])
        security_scan.create_security_marker(skill)
        code, output = self.package(skill)
        self.assertEqual(1, code, output)
        self.assertIn("references assets/starter.zip, but the zip leaves it out (.zip files never ship)", output)
        self.assertIn("references references/node_modules/notes.md, but the zip leaves it out", output)
        self.assertNotIn("assets/.env.example, but", output)
        self.assertNotIn("scripts/evals/score.py, but", output)
        self.assertNotIn("evals/evals.json, but", output)

    def test_local_env_reference_warns_but_packages(self):
        body = CLEAN_BODY.replace(
            "4. Verify:",
            "4. Read the API key from `scripts/.env`, which each user creates; never ship it.\n5. Verify:",
        )
        skill = make_skill(self.tmp / "src", body=body)
        write_file(skill / "scripts" / ".env", "API_KEY=local\n")
        security_scan.create_security_marker(skill)
        code, output = self.package(skill)
        self.assertEqual(0, code, output)
        self.assertIn("[WARN] SKILL.md:", output)
        self.assertIn("references scripts/.env, but the zip leaves it out", output)
        with zipfile.ZipFile(self.tmp / "dist" / f"{skill.name}.zip") as archive:
            self.assertFalse(any(name.endswith("/.env") for name in archive.namelist()))

    def test_failed_write_removes_partial_zip(self):
        skill = self.make_packageable()
        out = self.tmp / "dist"
        with mock.patch.object(zipfile.ZipFile, "write", side_effect=OSError(28, "No space left on device")):
            code, output = quietly(package_skill.main, [str(skill), str(out)])
        self.assertEqual(1, code)
        self.assertEqual([], list(out.iterdir()))


class Cp1252Output(TempDirCase):
    """Every script must survive a cp1252 console with non-cp1252 text in its output."""

    ENV = {"PYTHONIOENCODING": "cp1252"}

    def setUp(self) -> None:
        super().setUp()
        self.base = self.tmp / "\u540d\u524d-\u2713"  # Japanese and a check mark: not in cp1252
        self.base.mkdir()

    def assertNoTraceback(self, result, allowed_codes):
        output = result.stdout + result.stderr
        self.assertNotIn("Traceback", output)
        self.assertIn(result.returncode, allowed_codes, output)

    def test_quick_validate(self):
        fm = "name: caf\u00e9-\u540d\u524d\ndescription: Converts \u2713 files. Use when the user asks.\n"
        skill = make_skill(self.base, frontmatter=fm, folder="emoji-skill")
        result = run_script("quick_validate.py", str(skill), env_extra=self.ENV, encoding="cp1252")
        self.assertNoTraceback(result, {1})
        self.assertIn("[M9]", result.stdout)

    def test_init_skill(self):
        result = run_script("init_skill.py", "demo-skill", "--path", str(self.base),
                            env_extra=self.ENV, encoding="cp1252")
        self.assertNoTraceback(result, {0})
        self.assertIn("-?", result.stdout)  # the check mark in the path, replaced instead of crashing

    def test_package_skill(self):
        skill = make_skill(self.base)
        result = run_script("package_skill.py", str(skill), str(self.tmp / "dist"),
                            env_extra=self.ENV, encoding="cp1252")
        self.assertNoTraceback(result, {1})  # no security marker yet
        self.assertIn("-?", result.stdout)

    def test_security_scan(self):
        # The folder name and a file name carry the check mark, and both are printed:
        # "Scanning: <folder>" and the --verbose lead line for the file.
        skill = make_skill(self.base, folder="skill-\u2713")
        write_file(skill / "scripts" / "\u2713run.py", "import os\nos.system('ls')\n")
        empty_path = self.tmp / "empty-bin"
        empty_path.mkdir()
        env = dict(self.ENV, PATH=str(empty_path))  # no gitleaks can be found, so the exit code is fixed at 3
        result = run_script("security_scan.py", str(skill), "--verbose", "--no-marker",
                            env_extra=env, encoding="cp1252")
        self.assertNoTraceback(result, {3})
        self.assertIn("Scanning: skill-?", result.stdout)
        self.assertIn("[M10] major check scripts/?run.py:2", result.stdout)
        self.assertEqual("RESULT secrets=0 leads=1", last_line(result.stdout))
        self.assertFalse((skill / security_scan.MARKER_NAME).exists())

    def test_help_for_every_script(self):
        for script in SCRIPT_NAMES:
            result = run_script(script, "--help", env_extra=self.ENV, encoding="cp1252")
            self.assertNoTraceback(result, {0})
            self.assertIn(f"scripts/{script}", result.stdout)


class NoBytecodeInSkillsTree(TempDirCase):
    def test_no_pycache_under_create_skill_scripts(self):
        self.assertFalse((_helpers.SCRIPTS / "__pycache__").exists())

    def test_scripts_never_write_bytecode_on_their_own(self):
        # Without -B and with the bytecode variables removed, only the scripts' own
        # sys.dont_write_bytecode lines keep __pycache__ out of the folder.
        copy = self.tmp / "scripts"
        shutil.copytree(_helpers.SCRIPTS, copy, ignore=shutil.ignore_patterns("__pycache__"))
        env = {key: value for key, value in os.environ.items()
               if key not in ("PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX")}
        for script in SCRIPT_NAMES:
            result = subprocess.run(
                [sys.executable, str(copy / script), "--help"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                env=env, timeout=_helpers.SUBPROCESS_TIMEOUT_SECONDS,
            )
            self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([], [p.relative_to(copy).as_posix() for p in copy.rglob("__pycache__")])


if __name__ == "__main__":
    unittest.main()
