#!/usr/bin/env python3
"""Scan a skill for secrets (gitleaks) and risky patterns before packaging.

A clean gitleaks scan writes .security-scan-passed, holding a content hash, into
the skill directory; package_skill.py refuses to package without a matching
marker. --no-marker reports only and never writes into the target.

The scanned skill cannot weaken its own scan. gitleaks runs from an absolute
path found on PATH (never from the current folder or from inside the skill),
from an empty temporary working folder, and with --ignore-gitleaks-allow, and
it scans a temporary copy that holds only the skill's regular files, so links
are never followed. When the skill holds a gitleaks config (.gitleaks.toml,
.gitleaksignore, or gitleaks.toml, as a file or a link) at any depth, the script
prints an [M10] major check line for it and leaves it out of the copy.

Usage:
    python scripts/security_scan.py <skill-dir> [--verbose] [--no-marker]

Output: one line per finding ("[M10] major definitive", "[M10] major check",
"[m11] minor check", or "[info]"), then a final "RESULT secrets=<n> leads=<n>".

Exit codes: 0 clean, 1 high-severity secrets, 2 critical secrets, 3 gitleaks not
installed, 4 scan error (including usage and internal errors). Leads never
change the exit code.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # importing the sibling validator must not leave __pycache__ in the skill tree

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import stat  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

EXIT_CLEAN = 0
EXIT_HIGH = 1
EXIT_CRITICAL = 2
EXIT_NO_GITLEAKS = 3
EXIT_SCAN_ERROR = 4

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

try:
    from quick_validate import PLACEHOLDER_USER_NAMES  # noqa: E402
except (ImportError, SyntaxError) as _exc:  # a traceback would exit 1, which reads as "secrets found"
    print(f"[ERROR] cannot import quick_validate.py from {_SCRIPTS_DIR} ({_exc}); reinstall create-skill",
          file=sys.stderr)
    sys.exit(EXIT_SCAN_ERROR)

# --- Files shared by hashing and packaging --------------------------------------

MARKER_NAME = ".security-scan-passed"
EXCLUDED_DIR_NAMES = frozenset({".git", "__pycache__", "node_modules", ".venv", "venv"})  # at any depth
EVALS_DIR_NAME = "evals"  # authoring-only, top level only; packaging strips it, so the hash ignores it too
EXCLUDED_FILE_NAMES = frozenset({MARKER_NAME, ".ds_store", "thumbs.db"})  # compared in lower case
EXCLUDED_SUFFIXES = (".pyc", ".zip")
ENV_PREFIX = ".env"  # .env, .env.local, .envrc, and .env/ folders hold local secrets and never ship
KEPT_ENV_NAMES = frozenset({".env.example"})  # a template without secrets, which SKILL.md may tell users to copy

# --- gitleaks -----------------------------------------------------------------------

GITLEAKS_CONFIG_NAMES = frozenset({".gitleaks.toml", ".gitleaksignore", "gitleaks.toml"})  # lower case
IGNORE_ALLOW_FLAG = "--ignore-gitleaks-allow"  # gitleaks v8: inline "gitleaks:allow" comments no longer hide lines
GITLEAKS_TIMEOUT_SECONDS = 120  # a skill-sized scan takes seconds; the margin covers cold starts and antivirus
GITLEAKS_PROBE_TIMEOUT_SECONDS = 30  # "gitleaks dir --help" only starts the binary
GITLEAKS_LEAKS_EXIT_CODE = 2  # passed as --exit-code so "leaks found" differs from gitleaks' own error code 1

# --- Limits ------------------------------------------------------------------------

MAX_SIMPLE_FINDINGS = 5  # the packaging gate lists a few secrets; --verbose lists them all
MAX_VERBOSE_PER_PATTERN = 10  # keeps verbose output readable when one pattern repeats across many files
MATCH_PREVIEW_CHARS = 80  # enough to recognise a match without dumping a long line
# A gitleaks rule ID that contains one of these words is CRITICAL (exit 2); any other is HIGH (exit 1).
CRITICAL_RULE_WORDS = ("api", "key", "token", "password", "secret", "credential")
TEXT_SNIFF_BYTES = 8000  # git's binary test: a NUL byte in the first 8000 bytes means binary
HASH_LENGTH_BYTES = 8  # every hashed field is prefixed with its length as an 8-byte big-endian integer
IO_REPARSE_TAG_MOUNT_POINT = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)  # junction tag (winnt.h)

TEXT_SUFFIXES = frozenset({
    ".py", ".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".sh", ".bash", ".ps1",
    ".md", ".yml", ".yaml", ".json", ".toml",
})

INSTALL_HINTS = (
    "  macOS:    brew install gitleaks",
    "  Windows:  winget install gitleaks   (or: scoop install gitleaks)",
    "  Linux:    download the release tarball from https://github.com/gitleaks/gitleaks/releases/latest,",
    "            extract it, and move the gitleaks binary onto your PATH (for example /usr/local/bin/)",
)

LEAD_MAJOR = "[M10] major check"
LEAD_MINOR = "[m11] minor check"
INFO = "[info]"
SECRET = "[M10] major definitive"


class ScanError(Exception):
    """gitleaks could not complete the scan, or its result cannot be trusted."""


@dataclass(frozen=True)
class PatternRule:
    rule: str  # LEAD_MAJOR, LEAD_MINOR, or INFO
    name: str
    patterns: tuple[re.Pattern, ...]
    fix: str
    exceptions: tuple[str, ...] = ()
    name_group: bool = False  # True when the match carries a user name to compare with placeholders


@dataclass(frozen=True)
class PatternIssue:
    rule: str
    file: str
    line: int
    name: str
    matched: str
    fix: str

    @property
    def is_lead(self) -> bool:
        return self.rule != INFO

    def format(self) -> str:
        return f"{self.rule} {self.file}:{self.line} {self.name}: {self.matched} -- {self.fix}"


@dataclass(frozen=True)
class GitleaksLookup:
    path: str | None  # absolute path of the gitleaks to run, or None when none can be trusted
    refused: tuple[str, ...] = ()  # executables ignored because they sit in the current folder or the skill


PATTERN_RULES = (
    PatternRule(
        rule=LEAD_MAJOR,
        name="Network call",
        patterns=tuple(re.compile(p) for p in (
            r"\brequests\.(?:get|post|put|delete|patch)\s*\(",
            r"\burllib\.request\b",
            r"\bhttp\.client\b",
            r"\bsocket\.",
            r"\bcurl\s",
            r"\bwget\s",
            r"\bfetch\(",
        )),
        fix="disclose the network use and its purpose in SKILL.md",
    ),
    PatternRule(
        rule=LEAD_MAJOR,
        name="Dangerous code",
        patterns=tuple(re.compile(p) for p in (
            r"\bos\.system\s*\(",
            r"subprocess\.[a-z_]+\([^)]*shell\s*=\s*True",
            r"\bimport\s+pickle\b",
            r"\bpickle\.loads?\b",
        )),
        fix="use subprocess.run with a list of arguments, and JSON instead of pickle",
    ),
    PatternRule(
        rule=LEAD_MINOR,
        name="User-specific path",
        patterns=tuple(re.compile(p) for p in (
            r"/home/(?P<name>[A-Za-z0-9_][A-Za-z0-9_.-]*)/",
            r"/Users/(?P<name>[A-Za-z0-9_][A-Za-z0-9_.-]*)/",
            r"\b[A-Za-z]:[\\/]+[Uu]sers[\\/]+(?P<name>[A-Za-z0-9_][A-Za-z0-9_.-]*)",
        )),
        fix="use a path relative to the skill, Path(__file__).parent, or ~",
        name_group=True,
    ),
    PatternRule(
        rule=INFO,
        name="Email address",
        patterns=(re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),),
        fix="use a placeholder such as user@example.com",
        exceptions=("example.com", "example.org", "test.com", "localhost", "noreply@anthropic.com",
                    "users.noreply.github.com"),
    ),
    PatternRule(
        rule=INFO,
        name="Plain-HTTP URL",
        patterns=(re.compile(r"http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]|example\.(?:com|org))"),),
        fix="use https:// for external resources",
    ),
)


class _Palette:
    """ANSI colours, enabled only when stdout is a terminal."""

    def __init__(self, enabled: bool) -> None:
        self.red = "\033[91m" if enabled else ""
        self.yellow = "\033[93m" if enabled else ""
        self.green = "\033[92m" if enabled else ""
        self.reset = "\033[0m" if enabled else ""


def _palette(stream=None) -> _Palette:
    """Colours only when the stream the text goes to (stdout by default) is a terminal."""
    stream = sys.stdout if stream is None else stream
    return _Palette(hasattr(stream, "isatty") and stream.isatty())


def _inside(path: Path, directory: Path) -> bool:
    return path == directory or directory in path.parents


# --- File iteration and hashing ------------------------------------------------------

def is_link(path: Path) -> bool:
    """True for a symlink or a Windows junction; neither is ever followed out of the skill."""
    if path.is_symlink():
        return True
    isjunction = getattr(os.path, "isjunction", None)  # Python 3.12+
    if isjunction is not None:
        return isjunction(path)
    try:
        return getattr(os.lstat(path), "st_reparse_tag", 0) == IO_REPARSE_TAG_MOUNT_POINT
    except OSError:
        return False  # the entry vanished during the walk, so there is nothing to follow


def exclusion_reason(rel, include_evals: bool = False) -> str | None:
    """Why packaging leaves out this skill-relative path, or None when it ships."""
    parts = Path(rel).parts
    if not parts:
        return None
    if not include_evals and parts[0] == EVALS_DIR_NAME:
        return "the top-level evals/ folder is authoring-only"
    for part in parts:
        lowered = part.lower()
        if lowered in EXCLUDED_DIR_NAMES:
            return f"{part}/ folders never ship"
        if lowered in EXCLUDED_FILE_NAMES:
            return f"{part} never ships"
        if lowered.endswith(EXCLUDED_SUFFIXES):
            return f"{Path(lowered).suffix} files never ship"
        if lowered.startswith(ENV_PREFIX) and lowered not in KEPT_ENV_NAMES:
            return ".env files and folders never ship (only .env.example does)"
    return None


def _walk(root: Path, skip) -> tuple[list[Path], list[Path]]:
    """Return (regular files, links) under root, each sorted by relative path.

    skip(rel) prunes a file or folder before it is entered. Links (symlinks and
    junctions) are returned separately and never followed.
    """
    files: list[Path] = []
    links: list[Path] = []
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                if skip(path.relative_to(root)):
                    continue
                if is_link(path):
                    links.append(path)
                elif entry.is_dir(follow_symlinks=False):
                    pending.append(path)
                elif entry.is_file(follow_symlinks=False):
                    files.append(path)

    def key(path: Path) -> str:
        return path.relative_to(root).as_posix()

    return sorted(files, key=key), sorted(links, key=key)


def iter_skill_files(skill_path, include_evals: bool = False):
    """Yield the regular files that ship with the skill, sorted by relative path.

    Exclusions use the path relative to the skill, so a skill stored under a
    dot-folder such as ~/.claude/skills/ is still scanned. The top-level evals/
    is skipped unless include_evals is True. Symlinks and junctions are skipped,
    never followed; skill_links() lists them. Raises OSError when a folder
    cannot be read.
    """
    files, _ = _walk(Path(skill_path), lambda rel: exclusion_reason(rel, include_evals) is not None)
    yield from files


def skill_links(skill_path, include_evals: bool = False) -> list[Path]:
    """Symlinks and junctions among the files that would ship; packaging refuses them."""
    _, links = _walk(Path(skill_path), lambda rel: exclusion_reason(rel, include_evals) is not None)
    return links


def _normalised(data: bytes) -> bytes:
    """CRLF to LF for text (git's NUL test), so autocrlf checkouts hash alike in any encoding."""
    if b"\0" in data[:TEXT_SNIFF_BYTES]:
        return data
    return data.replace(b"\r\n", b"\n")


def _length_prefixed(data: bytes) -> bytes:
    return len(data).to_bytes(HASH_LENGTH_BYTES, "big") + data


def calculate_skill_hash(skill_path) -> str:
    """SHA-256 over every shipped file as length-prefixed (POSIX relative path, content) pairs.

    The length prefixes keep file boundaries unambiguous, so no content can
    imitate a different set of files. Text (no NUL in the first 8000 bytes) is
    hashed with CRLF normalised to LF, so a git checkout with autocrlf hashes
    the same on every platform. Raises OSError when a file cannot be read.
    """
    root = Path(skill_path)
    hasher = hashlib.sha256()
    for path in iter_skill_files(root, include_evals=False):
        hasher.update(_length_prefixed(path.relative_to(root).as_posix().encode("utf-8")))
        hasher.update(_length_prefixed(_normalised(path.read_bytes())))
    return hasher.hexdigest()


def create_security_marker(skill_path) -> Path:
    """Write the marker that package_skill.py checks. Raises OSError on failure."""
    root = Path(skill_path)
    marker = root / MARKER_NAME
    marker.write_text(
        "Security scan passed\n"
        f"Scanned at: {datetime.now().isoformat(timespec='seconds')}\n"
        "Tool: gitleaks\n"
        f"Content hash: {calculate_skill_hash(root)}\n",
        encoding="utf-8",
    )
    return marker


# --- Finding gitleaks -------------------------------------------------------------------

def _gitleaks_names() -> tuple[str, ...]:
    return ("gitleaks.exe",) if os.name == "nt" else ("gitleaks",)


def find_gitleaks(skill_path, search_path: str | None = None, cwd=None) -> GitleaksLookup:
    """Find gitleaks on PATH as an absolute path, never in the current folder or the skill.

    Windows starts a bare "gitleaks" from the current folder before PATH, so a
    scanned folder could plant its own. Searching PATH by hand, skipping empty
    and relative entries, and refusing any copy that sits in the current folder
    or inside the skill closes that hole. search_path and cwd default to PATH
    and the current folder.
    """
    current = Path(cwd if cwd is not None else Path.cwd()).resolve()
    skill = Path(skill_path).resolve()
    refused: list[str] = []

    def untrusted(candidate: Path) -> bool:
        for location in (candidate.parent.resolve(), candidate.resolve().parent):
            if location == current or _inside(location, skill):
                return True
        return False

    for name in _gitleaks_names():
        planted = current / name
        if planted.is_file():
            refused.append(str(planted))
    entries = os.environ.get("PATH", "") if search_path is None else search_path
    for entry in entries.split(os.pathsep):
        entry = entry.strip().strip('"')
        if not entry or not os.path.isabs(entry):
            continue  # empty and relative entries depend on the current folder
        for name in _gitleaks_names():
            candidate = Path(entry) / name
            if not candidate.is_file() or not os.access(candidate, os.X_OK):
                continue
            if untrusted(candidate):
                if str(candidate) not in refused:
                    refused.append(str(candidate))
                continue
            return GitleaksLookup(str(candidate.resolve()), tuple(refused))
    return GitleaksLookup(None, tuple(refused))


def find_gitleaks_config(skill_path) -> list[Path]:
    """gitleaks config files or links at any depth; a target could use them to silence its own scan."""
    files, links = _walk(Path(skill_path), lambda rel: rel.name == ".git")
    return [path for path in (*files, *links) if path.name.lower() in GITLEAKS_CONFIG_NAMES]


# --- Running gitleaks -------------------------------------------------------------------

def _gitleaks_has_dir_command(gitleaks: str) -> bool:
    try:
        probe = subprocess.run(
            [gitleaks, "dir", "--help"], capture_output=True, stdin=subprocess.DEVNULL,
            timeout=GITLEAKS_PROBE_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False  # older gitleaks without "dir", or a probe failure: the scan falls back to "detect"
    return probe.returncode == 0


def _gitleaks_command(gitleaks: str, source: Path, report_path: str, use_dir: bool,
                      ignore_allow: bool = True) -> list[str]:
    if use_dir:
        command = [gitleaks, "dir", str(source), "--report-format", "json", "--report-path", report_path,
                   "--exit-code", str(GITLEAKS_LEAKS_EXIT_CODE), "--no-banner"]
    else:
        command = [gitleaks, "detect", "--no-git", "--source", str(source), "--report-format", "json",
                   "--report-path", report_path, "--exit-code", str(GITLEAKS_LEAKS_EXIT_CODE)]
    return command + ([IGNORE_ALLOW_FLAG] if ignore_allow else [])


def _run_gitleaks_once(command: list[str], work: Path) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL, cwd=str(work), timeout=GITLEAKS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise ScanError(f"gitleaks did not finish within {GITLEAKS_TIMEOUT_SECONDS} seconds") from exc
    except OSError as exc:
        raise ScanError(f"could not start gitleaks at {command[0]} ({exc.strerror or exc})") from exc


def _rejected_flag(result: subprocess.CompletedProcess, flag: str) -> bool:
    output = f"{result.stderr or ''}\n{result.stdout or ''}"
    return result.returncode not in (0, GITLEAKS_LEAKS_EXIT_CODE) and flag in output and "unknown flag" in output


def _read_report(report: Path) -> list[dict]:
    """The findings gitleaks wrote; anything but a non-empty list of findings is a scan error."""
    try:
        findings = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScanError(f"gitleaks reported leaks, but its report could not be read ({exc})") from exc
    if not isinstance(findings, list) or not findings or not all(isinstance(f, dict) for f in findings):
        raise ScanError(f"gitleaks reported leaks (exit {GITLEAKS_LEAKS_EXIT_CODE}), but its report holds "
                        "no list of findings, so the result cannot be trusted; run the scan again")
    return findings


def _relative_file(finding: dict, scan_root: Path) -> dict:
    raw = str(finding.get("File", "unknown"))
    try:
        rel = Path(raw).resolve().relative_to(scan_root.resolve()).as_posix()
    except (OSError, ValueError):
        rel = raw.replace("\\", "/")
    return {**finding, "File": rel}


def _copy_without(root: Path, destination: Path, omit: set[Path]) -> None:
    """Copy the skill's regular files except omit, leaving out links and .git/."""
    files, _ = _walk(root, lambda rel: rel.name == ".git")
    for path in files:
        if path in omit:
            continue
        target = destination / path.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def run_gitleaks(skill_path, gitleaks: str, omit=()) -> list[dict]:
    """Return gitleaks findings ([] when clean), with File relative to the skill.

    gitleaks always scans a temporary copy that holds only the skill's regular
    files: links are never followed, and the files in omit (the skill's gitleaks
    configs) are left out, so the skill cannot configure or silence its own scan.
    gitleaks runs from an empty temporary folder, so no .gitleaksignore in the
    current folder is loaded either. Raises ScanError when gitleaks fails or its
    report cannot be trusted.
    """
    skill_path = Path(skill_path)
    work = Path(tempfile.mkdtemp(prefix="skill-scan-"))
    try:
        scan_root = work / "copy" / skill_path.name
        try:
            _copy_without(skill_path, scan_root, {Path(p) for p in omit})
        except OSError as exc:
            raise ScanError(f"could not copy the skill for scanning ({exc})") from exc
        report = work / "gitleaks-report.json"
        use_dir = _gitleaks_has_dir_command(gitleaks)
        result = _run_gitleaks_once(_gitleaks_command(gitleaks, scan_root, str(report), use_dir), work)
        if _rejected_flag(result, IGNORE_ALLOW_FLAG):
            print(f"[WARN] this gitleaks does not accept {IGNORE_ALLOW_FLAG}, so inline gitleaks:allow "
                  "comments were honoured; upgrade gitleaks to its latest release")
            result = _run_gitleaks_once(
                _gitleaks_command(gitleaks, scan_root, str(report), use_dir, ignore_allow=False), work)
        if result.returncode == 0:
            return []
        if result.returncode != GITLEAKS_LEAKS_EXIT_CODE:
            detail = " ".join((result.stderr or result.stdout or "").split()) or "no output"
            raise ScanError(f"gitleaks exited with code {result.returncode}: {detail}")
        return [_relative_file(finding, scan_root) for finding in _read_report(report)]
    finally:
        shutil.rmtree(work, ignore_errors=True)
        if work.exists():
            print(f"[WARN] could not remove the temporary folder {work}; delete it by hand", file=sys.stderr)


# --- Pattern leads ----------------------------------------------------------------------

def scan_skill_patterns(skill_path) -> list[PatternIssue]:
    """Regex leads over text files, evals included; unreadable files are reported, not skipped."""
    root = Path(skill_path)
    issues: list[PatternIssue] = []
    for path in iter_skill_files(root, include_evals=True):
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(PatternIssue(INFO, rel, 0, "Unreadable file", str(exc)[:MATCH_PREVIEW_CHARS],
                                       "save it as UTF-8 so it can be scanned"))
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for rule in PATTERN_RULES:
                for pattern in rule.patterns:
                    for match in pattern.finditer(line):
                        matched = match.group(0)
                        if any(exception in matched for exception in rule.exceptions):
                            continue
                        if rule.name_group and match.group("name").lower() in PLACEHOLDER_USER_NAMES:
                            continue
                        issues.append(PatternIssue(rule.rule, rel, number, rule.name,
                                                   matched[:MATCH_PREVIEW_CHARS], rule.fix))
    return issues


def config_issues(skill_path: Path, configs: list[Path]) -> list[PatternIssue]:
    return [
        PatternIssue(LEAD_MAJOR, path.relative_to(skill_path).as_posix(), 0, "Gitleaks config shipped in the skill",
                     "left out of the gitleaks scan",
                     "remove it; a skill must not configure its own secret scan")
        for path in configs
    ]


def link_issues(skill_path: Path, links: list[Path]) -> list[PatternIssue]:
    return [
        PatternIssue(INFO, path.relative_to(skill_path).as_posix(), 0, "Link not followed",
                     "symlink or junction", "its target was not scanned; replace the link with the real files")
        for path in links
    ]


def categorize_gitleaks_severity(rule_id: str) -> str:
    lowered = rule_id.lower()
    return "CRITICAL" if any(word in lowered for word in CRITICAL_RULE_WORDS) else "HIGH"


# --- Reporting ---------------------------------------------------------------------------

def _display_path(raw: str, skill_path: Path) -> str:
    candidate = Path(raw)
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(skill_path.resolve()).as_posix()
        except (OSError, ValueError):
            return raw.replace("\\", "/")  # outside the skill: show the path gitleaks gave
    return raw.replace("\\", "/")


def _secret_line(finding: dict, skill_path: Path) -> str:
    rule_id = finding.get("RuleID", "unknown")
    path = _display_path(str(finding.get("File", "unknown")), skill_path)
    line = finding.get("StartLine", 0)
    return f"{SECRET} {path}:{line} {rule_id} ({categorize_gitleaks_severity(rule_id)})"


def report_secrets(findings: list[dict], skill_path: Path, verbose: bool) -> int:
    colours = _palette()
    if not findings:
        print(f"{colours.green}[PASS] gitleaks: no secrets detected{colours.reset}")
        return EXIT_CLEAN
    critical = sum(1 for f in findings if categorize_gitleaks_severity(f.get("RuleID", "")) == "CRITICAL")
    print(f"{colours.red}[FAIL] gitleaks: {len(findings)} secret(s) found "
          f"(critical {critical}, high {len(findings) - critical}){colours.reset}")
    shown = findings if verbose else findings[:MAX_SIMPLE_FINDINGS]
    for finding in shown:
        print(_secret_line(finding, skill_path))
        if verbose and finding.get("Description"):
            print(f"    {finding['Description']}")
    if len(findings) > len(shown):
        print(f"... and {len(findings) - len(shown)} more (run with --verbose to list all)")
    print("Fix: move each secret to an environment variable (os.environ['KEY_NAME']), then re-run this scan.")
    return EXIT_CRITICAL if critical else EXIT_HIGH


def report_issues(issues: list[PatternIssue]) -> None:
    for issue in issues:
        print(issue.format())


def report_patterns(issues: list[PatternIssue]) -> None:
    if not issues:
        print("[PASS] patterns: no leads")
        return
    leads = sum(1 for issue in issues if issue.is_lead)
    print(f"[WARN] patterns: {leads} lead(s) and {len(issues) - leads} info note(s); "
          "confirm each lead before reporting it (they do not change the exit code)")
    shown_per_name: dict[str, int] = {}
    for issue in issues:
        shown_per_name[issue.name] = shown_per_name.get(issue.name, 0) + 1
        if shown_per_name[issue.name] <= MAX_VERBOSE_PER_PATTERN:
            print(issue.format())
    for name, count in shown_per_name.items():
        if count > MAX_VERBOSE_PER_PATTERN:
            print(f"... and {count - MAX_VERBOSE_PER_PATTERN} more '{name}' lead(s)")


def print_gitleaks_installation() -> None:
    """The error and its install hints go to stderr; stdout keeps the leads and the RESULT line."""
    colours = _palette(sys.stderr)
    print(f"{colours.yellow}[ERROR] gitleaks is not installed; secrets were not scanned.{colours.reset}",
          file=sys.stderr)
    print("Install it, then run this script again:", file=sys.stderr)
    for hint in INSTALL_HINTS:
        print(hint, file=sys.stderr)


def result_line(secrets: int, leads: int) -> str:
    return f"RESULT secrets={secrets} leads={leads}"


# --- CLI -------------------------------------------------------------------------------------

def _configure_output() -> None:
    """Replace unencodable characters instead of crashing on cp1252 consoles and pipes."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")


class _Parser(argparse.ArgumentParser):
    """Usage errors exit 4 (scan error), because 2 already means critical secrets."""

    def error(self, message: str):
        self.print_usage(sys.stderr)
        self.exit(EXIT_SCAN_ERROR, f"{self.prog}: error: {message}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="scripts/security_scan.py",
        description="Scan a skill for secrets with gitleaks and, with --verbose, for risky code patterns.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Findings map to rules.md: secrets are [M10] major definitive; network calls, dangerous code,\n"
            "and gitleaks configs shipped in the skill are [M10] major check; user-specific paths are\n"
            "[m11] minor check; emails, plain-HTTP URLs, and links are [info]. The last line reads\n"
            "RESULT secrets=<n> leads=<n>; treat exit 1 or 2 as secrets only when secrets is above 0.\n\n"
            "gitleaks is taken from PATH, never from the current folder or the skill, and runs with\n"
            "--ignore-gitleaks-allow; a gitleaks config inside the skill is left out of the scan.\n\n"
            "Exit codes:\n"
            "  0  clean (the marker is written unless --no-marker)\n"
            "  1  high-severity secrets\n"
            "  2  critical secrets\n"
            "  3  gitleaks not installed\n"
            "  4  scan error, including usage and internal errors\n"
            "Leads never change the exit code."
        ),
    )
    parser.add_argument("skill_dir", help="path to the skill directory")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="also list every secret and run the pattern checks")
    parser.add_argument("--no-marker", action="store_true",
                        help="report only: never write .security-scan-passed into the skill")
    return parser


def _scan(args: argparse.Namespace) -> int:
    skill_path = Path(args.skill_dir).resolve()
    if not skill_path.is_dir():
        print(f"[ERROR] not a skill directory: {skill_path}", file=sys.stderr)
        return EXIT_SCAN_ERROR

    print(f"Scanning: {skill_path.name}")
    leads = 0

    def finish(code: int, secrets: int = 0) -> int:
        print(result_line(secrets, leads))
        return code

    try:
        configs = find_gitleaks_config(skill_path)
        links = skill_links(skill_path, include_evals=True)
        early = config_issues(skill_path, configs) + link_issues(skill_path, links)
        patterns = scan_skill_patterns(skill_path) if args.verbose else []
    except OSError as exc:
        print(f"[ERROR] cannot read the skill files ({exc}); check the folder permissions", file=sys.stderr)
        return finish(EXIT_SCAN_ERROR)
    leads = sum(1 for issue in early + patterns if issue.is_lead)
    report_issues(early)
    if args.verbose:
        report_patterns(patterns)

    lookup = find_gitleaks(skill_path)
    for path in lookup.refused:
        print(f"[WARN] ignored {path}: a gitleaks in the current folder or inside the scanned skill is never run")
    if lookup.path is None:
        print_gitleaks_installation()
        return finish(EXIT_NO_GITLEAKS)
    try:
        findings = run_gitleaks(skill_path, lookup.path, omit=configs)
    except ScanError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return finish(EXIT_SCAN_ERROR)

    exit_code = report_secrets(findings, skill_path, args.verbose)
    if exit_code != EXIT_CLEAN:
        return finish(exit_code, len(findings))
    if args.no_marker:
        print("[INFO] --no-marker: .security-scan-passed was not written")
        return finish(exit_code)
    try:
        marker = create_security_marker(skill_path)
    except OSError as exc:
        print(f"[ERROR] could not write {MARKER_NAME} ({exc.strerror or exc})", file=sys.stderr)
        return finish(EXIT_SCAN_ERROR)
    print(f"[OK] Security marker written: {marker.name}")
    return finish(exit_code)


def main(argv: list[str] | None = None) -> int:
    _configure_output()
    args = build_parser().parse_args(argv)
    try:
        return _scan(args)
    except Exception as exc:  # last resort: a traceback would exit 1, which reads as "secrets found"
        detail = " ".join(f"{type(exc).__name__}: {exc}".split())
        print(f"[ERROR] internal error in security_scan.py ({detail}); the scan result is unknown",
              file=sys.stderr)
        return EXIT_SCAN_ERROR


if __name__ == "__main__":
    sys.exit(main())
