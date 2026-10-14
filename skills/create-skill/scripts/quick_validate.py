#!/usr/bin/env python3
"""Validate a skill directory against the Repertoire rule catalog.

Implements the definitive checks in review-skill/references/rules.md and prints
heuristic leads as "check" lines. Every check is read-only.

Usage:
    python scripts/quick_validate.py <skill-dir> [--portable]

Output, one line per finding, then a summary line:
    [<ID>] <major|minor|style> <definitive|check> <file>:<line> <message>
    RESULT major=<n> minor=<n> style=<n> checks=<n>

Exit codes: 0 no definitive Major or Minor, 1 a definitive Major (F counts as
Major), 2 usage error, 3 environment error (including any internal error),
4 definitive Minor only. Check lines and Style findings never change the exit
code.

Requires Python 3.8 or later and PyYAML: python -m pip install pyyaml
(the m13 import check also needs Python 3.10 or later; older versions print a
check line instead).
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import posixpath
import re
import sys
import unicodedata
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # main() reports this as an environment error (exit 3)
    yaml = None


# --- Contract ---------------------------------------------------------------

EXIT_OK = 0
EXIT_MAJOR = 1
EXIT_USAGE = 2  # argparse's own exit code for usage errors
EXIT_ENV = 3
EXIT_MINOR = 4

MAJOR, MINOR, STYLE = "major", "minor", "style"
DEFINITIVE, CHECK = "definitive", "check"

PYYAML_HINT = "[env] PyYAML is required: python -m pip install pyyaml"
SKILL_FILE = "SKILL.md"

# Output order: rule IDs in the order rules.md lists them.
RULE_ORDER = (
    "F", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12",
    "m1", "m2", "m3", "m4", "m9", "m10", "m11", "m12", "m13", "m14", "m15",
    "S1", "S2", "S3", "S4", "S5", "S6", "S7",
)
_RULE_RANK = {rule_id: rank for rank, rule_id in enumerate(RULE_ORDER)}
_SEVERITY_RANK = {MAJOR: 0, MINOR: 1, STYLE: 2}
_CONFIDENCE_RANK = {DEFINITIVE: 0, CHECK: 1}

# --- Thresholds (each mirrors a number in rules.md) -------------------------

MAX_SKILL_LINES = 500  # M1: Anthropic's and the spec's ceiling for SKILL.md
STYLE_MAX_LINES = 400  # S3: house target that leaves headroom under the M1 ceiling
STYLE_MAX_CHARS = 20000  # S3: about 5k tokens at roughly 4 characters per token, counted with LF endings
MAX_NAME_LENGTH = 64  # M9: Agent Skills spec limit for name
MAX_DESCRIPTION_LENGTH = 1024  # M9: spec limit for description
MAX_LISTING_LENGTH = 1536  # m12: Claude Code truncates description + when_to_use here
MAX_COMPATIBILITY_LENGTH = 500  # M9 (portable): spec limit for compatibility
REFERENCE_TOC_MIN_LINES = 100  # m9: references longer than this need a table of contents
REFERENCE_TOC_WINDOW = 30  # m9: the contents heading must appear within this many lines
WEAK_VERB_THRESHOLD = 3  # M7: three or more weak directives make a lead
EMPHASIS_THRESHOLD = 3  # m15: three or more shouted directives make a lead
MIN_EXAMPLES = 3  # S2: house minimum of <example> blocks
MAX_EXAMPLES = 5  # S2: house maximum before examples belong in references/
MIN_EVAL_CASES = 3  # S5: Anthropic's checklist asks for at least three evaluations
NEGATION_WINDOW = 120  # M2: characters before a match searched for a negation (the clause bounds it further)
MAX_LISTED_LINES = 8  # message length cap when a finding lists extra line numbers
FRONTMATTER_FIRST_LINE = 2  # YAML reports 0-based lines; its line 0 is file line 2, after the opening ---

# --- Vocabularies -------------------------------------------------------------

# \Z, not $: "$" also matches before a final newline, so "demo\n" would pass.
NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
RESERVED_NAME_WORDS = ("anthropic", "claude")
RESERVED_FOLDER = "synced"
RESERVED_FOLDER_PREFIX = "anthropic-skills"
TEMPLATE_MARKER = "[TODO"
INIT_PLACEHOLDER_FILES = ("scripts/example.py", "references/api_reference.md", "assets/example_asset.txt")

CLAUDE_CODE_KEYS = frozenset({
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "disable-model-invocation", "user-invocable", "allowed-tools", "disallowed-tools",
    "model", "effort", "context", "agent", "background", "hooks", "paths", "shell",
    "metadata", "license", "compatibility",
})
PORTABLE_KEYS = frozenset({"name", "description", "license", "compatibility", "metadata", "allowed-tools"})
FORK_ONLY_KEYS = ("agent", "background")  # m12: dead keys without context: fork
READ_ONLY_AGENTS = frozenset({"Explore", "Plan"})

ALLOWED_ROOT_DIRS = frozenset({"scripts", "references", "assets", "evals", "tests"})
LICENSE_PREFIX = "LICENSE"
BUNDLED_DIRS = ("scripts", "references", "assets", "evals")
SHELL_FENCE_TAGS = frozenset({"powershell", "ps1", "pwsh", "cmd", "bat"})
INSTRUCTIONS_TAG = "<instructions>"

WEAK_VERBS = (
    "consider", "ensure", "handle appropriately", "handle properly",
    "as needed", "as appropriate", "if applicable", "where relevant",
)
EMPHASIS_WORDS = ("MUST", "NEVER", "ALWAYS", "CRITICAL", "IMPORTANT", "REQUIRED", "MANDATORY")

# m11: generic names that are not a real person's home folder. Shared and Public
# are system folders on macOS and Windows.
PLACEHOLDER_USER_NAMES = frozenset({
    "username", "user", "you", "your-name", "name", "me", "example", "shared", "public",
})
PLACEHOLDER_NAME_STARTS = ("<", "{", "$", "%")

# S6: capitalised words ending in "s" that are not third-person verbs.
S6_NON_VERBS = frozenset({
    "Its", "Has", "Does", "Always", "Perhaps", "Sometimes", "Various", "Docs", "Tools",
    "Utils", "Utilities", "Helpers", "Tips", "Notes", "Rules", "Guidelines",
    "Instructions", "Settings", "Series", "News", "Lots", "Yes", "Hers", "Ours",
    "Yours", "Theirs", "Towards", "Besides",
})
S6_NON_VERB_ENDINGS = ("ss", "us", "is", "as")  # Class, Status, This/Analysis, Was/Canvas

# M8: words before a capital "I" that make it a roman numeral, not the pronoun.
ROMAN_NUMERAL_CONTEXT_RE = re.compile(
    r"\b(?:phase|part|type|class|level|tier|stage|grade|chapter|section|volume|appendix|act|book|war)\s+$",
    re.IGNORECASE,
)

# m13: import names whose pip package name differs.
PIP_NAMES = {
    "yaml": "pyyaml", "PIL": "pillow", "cv2": "opencv-python", "bs4": "beautifulsoup4",
    "docx": "python-docx", "pptx": "python-pptx", "sklearn": "scikit-learn",
    "dateutil": "python-dateutil", "fitz": "pymupdf", "dotenv": "python-dotenv",
}

# M6: interactive input in Python scripts.
INPUT_BUILTINS = ("input", "raw_input")
STDIN_READ_METHODS = frozenset({"read", "readline", "readlines"})

# --- Patterns -----------------------------------------------------------------

FRONTMATTER_RE = re.compile(
    r"\A\ufeff?---[ \t]*\r?\n(.*?)(?:\r?\n)?^---[ \t]*\r?$", re.DOTALL | re.MULTILINE
)
# Any indent, so a fence nested in a list item still counts. A backtick fence's
# info string cannot contain a backtick (CommonMark), so "```csv``` is ..." is inline code.
FENCE_OPEN_RE = re.compile(r"^[ \t]*(`{3,}(?=[^`]*$)|~{3,})[ \t]*([^\s`]*)")
EXAMPLE_OPEN_RE = re.compile(r"^\s*<example>")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
IDENTIFIER_CODE_RE = re.compile(r"`([A-Za-z_][\w:.]*)`")
QUOTE_RE = re.compile(
    r"\"[^\"\n]*\"|\u201c[^\u201d\n]*\u201d|(?<!\w)'[^'\n]+'(?!\w)|\u2018[^\u2019\n]*\u2019"
)
# The scheme must start a word and is at most 32 characters, so a long run such as
# "a-a-a-..." costs linear time instead of rescanning from every position.
URL_RE = re.compile(r"(?<![\w+.-])[a-zA-Z][\w+.-]{0,31}://[^\s)>\]\"'`]*")

_CURLY_AND_DASHES = "\u2018\u2019\u201c\u201d\u2013\u2014"
_PATH_BOUNDARY = r"(?:^|(?<=[\s'\"`(\[=:*" + _CURLY_AND_DASHES[:4] + r"]))"
_PATH_CHAR = r"[^\s'\"`()\[\]|,;" + _CURLY_AND_DASHES + r"]"
BUNDLED_PATH_RE = re.compile(
    _PATH_BOUNDARY
    + r"(?P<root>\$\{CLAUDE_SKILL_DIR\}/|\$CLAUDE_SKILL_DIR/|\./)?"
    + r"(?:\.\./(?P<sibling>[A-Za-z0-9][\w.-]*)/)?"
    + r"(?P<path>(?:" + "|".join(BUNDLED_DIRS) + r")/(?:[\w.{}<>*$-]" + _PATH_CHAR + r"*)?)",
    re.MULTILINE,
)
# "_scripts/x.py_" (Markdown emphasis): the underscore that opens a word is not part of the path.
EMPHASIS_UNDERSCORE_RE = re.compile(r"(?<![^\s(\[])_(?=(?:" + "|".join(BUNDLED_DIRS) + r")/)")
PATH_TRAILING_CHARS = ".,;:)]*!?'\"_" + _CURLY_AND_DASHES
PATH_SUFFIX_RE = re.compile(r"(?::\d+(?:-\d+)?(?::\d+)?|::?[A-Za-z_][\w.]*(?:\(\))?)$")  # :10-20, :main
PATH_PLACEHOLDER_CHARS = "<>{}*$"
MARKDOWN_LINK_RE = re.compile(r"\]\(([^)\s\[\]()]+)\)")

# "the user" or "user" with no article ("ask user for confirmation"); not "user-facing".
_THE_USER = r"(?:the\s+)?user(?![\w-])"
ASK_USER_RE = re.compile(
    "|".join((
        r"\bAskUserQuestion\b",
        r"\bask(?:s|ing)?\s+" + _THE_USER,
        r"\basks\s+for\s+(?:confirmation|approval|permission|clarification|input)\b",
        r"\b(?:confirm|check)(?:s|ing)?\s+with\s+" + _THE_USER,
        r"\bprompt(?:s|ing)?\s+" + _THE_USER,
        r"\bwait(?:s|ing)?\s+for\s+(?:the\s+)?user(?:'s|\u2019s)?\b",
        r"\bwait(?:s|ing)?\s+for\s+(?:your|their)\s+"
        r"(?:confirmation|approval|permission|response|reply|input|answer)\b",
        r"\bwait(?:s|ing)?\s+for\s+(?:confirmation|approval|permission|a\s+reply|a\s+response|an\s+answer)\b",
        r"\bhave\s+the\s+user\s+(?:choose|pick|select|decide|confirm|approve)\b",
        r"\b(?:get|obtain|request)s?\s+the\s+user(?:'s|\u2019s)\s+(?:confirmation|approval)\b",
        r"\b(?:after|once|when|if|until|before|unless)\s+" + _THE_USER + r"\s+"
        r"(?:confirms|approves|responds|replies|agrees|answers)\b",
        # Not "unless the user selects otherwise", which names a default rather than a wait.
        r"\b(?:after|once|when|if|until)\s+" + _THE_USER + r"\s+(?:chooses|selects)\b",
        # "After user approval", "get user approval", "the user's confirmation"; the time
        # word is part of the match so that TEMPORAL_ASK_RE sees it. Not a UI element
        # being built ("a user confirmation dialog").
        r"\b(?:(?:after|once|when|until|upon|pending|before|unless)\s+)?(?:the\s+)?"
        r"user(?:'s|\u2019s)?\s+(?:approval|confirmation)\b"
        r"(?!\s+(?:dialog|modal|screen|page|form|button|flow|component|endpoint)s?\b)",
    )),
    re.IGNORECASE,
)
# Generic asking verbs count only as an instruction, so that descriptive prose such as
# "Users often ask for CSV summaries" or "if the request gets approval" is not a pause.
IMPERATIVE_ASK_RE = re.compile(
    "|".join((
        r"\bask\s+(?:which|whether|what|for)\b",
        r"\b(?:get|obtain|request)\s+(?:confirmation|approval)\b",
        # A questionnaire: "Ask all 10 questions", "ask clarifying questions". Not
        # "ask yourself these questions", a self-check, or "ask each subagent ...".
        r"\bask\s+(?:(?:all|the|these|those|following|clarifying|follow-up|a|few|some|any|more|several"
        r"|key|quick|short|targeted|intake|up|to|\d+(?:-\d+)?)\s+){0,4}questions?\b",
    )),
    re.IGNORECASE,
)
# What may precede an instruction on its line: nothing, a list marker or step label,
# emphasis, sentence or clause punctuation, or a joining word ("then ask which ...",
# "If the path is missing, ask for it").
IMPERATIVE_PREFIX_RE = re.compile(
    r"(?:^|[.:;!?,]|\b(?:then|and|or|first|next|always|please|to)\b|^\s*(?:[-*+]|\d+[.)])"
    r"|\*\*|__)\s*$",
    re.IGNORECASE,
)
# An explicit choice prompt: a question followed by options in square brackets separated
# by slashes ("Apply these changes? [All / Select / Cancel]"), or by "(y/n)". It is
# searched in code blocks too, because a skill shows the prompt it prints as literal output.
# Not a Markdown link ("Questions? [docs/faq](faq.md)").
_CHOICE = r"[A-Za-z][\w'-]*(?:[ \t]+[A-Za-z][\w'-]*){0,2}"
CHOICE_PROMPT_RE = re.compile(
    r"\?[ \t]*(?:\*\*|`)?"
    r"(?:\[[ \t]*" + _CHOICE + r"(?:[ \t]*/[ \t]*" + _CHOICE + r")+[ \t]*\](?!\()"
    r"|(?i:\((?:y|yes)[ \t]*/[ \t]*(?:n|no)\)))"
)
# Where the question of a choice prompt starts: after a sentence end or an opening quote.
QUESTION_START_RE = re.compile(r"[.!?](?=\s)|[\"'`\u201c\u2018>|]")
# A match that is itself a time or condition clause ("until the user approves")
# is not negated by a negation that governs another verb ("Do not proceed until ...").
TEMPORAL_ASK_RE = re.compile(r"(?:after|once|when|if|until|before|unless|upon|pending)\b", re.IGNORECASE)
# "without" cancels against an earlier negation in its clause: "never edit files
# without user approval" still waits for the user.
DOUBLE_NEGATION_RE = re.compile(r"\b(?:not|never|cannot|no|nothing|nobody)\b|n't\b|n\u2019t\b", re.IGNORECASE)
# M2: a reference SKILL.md sends Claude to as a step, so its pauses are the skill's
# own: named on a numbered step line, or on a line that says to read it first.
READ_VERB_RE = re.compile(r"\b(?:read|load|open|follow|use|consult|review|study)\b", re.IGNORECASE)
READ_FIRST_RE = re.compile(r"\b(?:first|before)\b|\b(?:start|begin)\s+(?:with|by)\b", re.IGNORECASE)
# M2 clauses run to sentence or clause punctuation, a paragraph or block break,
# or a table cell; a single newline inside a paragraph is a soft wrap.
CLAUSE_BREAK_RE = re.compile(
    r"[.!?;:,](?=\s|$)"
    r"|[\u2013\u2014]"
    r"|\n[ \t]*\n"
    r"|\n(?=[ \t]*(?:[-*+][ \t]|\d+[.)][ \t]|#|>|\||<))"
    r"|\|"
)
CONJUNCTION_RE = re.compile(r"\b(?:and|but|so|then)\b", re.IGNORECASE)
CONDITION_RE = re.compile(
    r"\b(?:if|when|whenever|unless|once|until|while|where|wherever|after|before|because|since|in\s+case)\b",
    re.IGNORECASE,
)
# Negations that govern the whole clause when no condition precedes them.
CLAUSE_NEGATION_RE = re.compile(r"\b(?:not|never|cannot|nor)\b|n't\b|n\u2019t\b", re.IGNORECASE)
_NEGATION_FILLERS = (
    "ever", "even", "directly", "explicitly", "interactively", "first", "yet", "again", "once", "then",
    "to", "try", "attempt", "need", "needs", "have", "has", "be", "able", "allowed", "required",
    "necessary", "should", "must", "will", "can", "you", "we", "they", "it", "is", "are", "of", "any",
    "circumstances", "point", "time", "bother", "go", "and", "or", "wait", "pause", "stop",
    "get", "getting", "obtain", "obtaining", "request", "requesting", "seek", "seeking", "explicit", "prior",
)
_NEGATORS = (  # "subagents lose AskUserQuestion" negates it too
    r"(?:\b(?:not|never|cannot|nor|no|without|avoid|avoiding|refrain\s+from|instead\s+of|rather\s+than"
    r"|lose|loses|lack|lacks)"
    r"|n't|n\u2019t)"
)


def _adjacent_negation(fillers: tuple[str, ...]) -> re.Pattern:
    """A negator followed only by filler words up to the match ("do not ever ask")."""
    return re.compile(
        _NEGATORS + r"(?:\s+(?:" + "|".join(fillers) + r")\b)*\s*$", re.IGNORECASE
    )


ADJACENT_NEGATION_RE = _adjacent_negation(_NEGATION_FILLERS)
TEMPORAL_ADJACENT_NEGATION_RE = _adjacent_negation(tuple(w for w in _NEGATION_FILLERS if w != "stop"))
_NOT = r"(?:\s+not|\s+never|n't|n\u2019t)"
POST_NEGATION_RE = re.compile(  # "`AskUserQuestion` is not available"
    r"\s*(?:tool\s+)?(?:"
    r"(?:is|are|was|were)" + _NOT + r"\s+(?:\w+\s+)?"
    r"(?:available|allowed|permitted|possible|supported|usable|an\s+option|required|needed|necessary)\b"
    r"|(?:is|are)\s+(?:unavailable|disabled|forbidden)\b"
    r"|(?:cannot|can't|can\u2019t|won't|won\u2019t|(?:will|must|may|should)" + _NOT + r")\s+be\s+"
    r"(?:used|called|available|asked)\b"
    r"|(?:does|do)" + _NOT + r"\s+(?:exist|work|apply)\b"
    r")",
    re.IGNORECASE,
)
WORKFLOW_TOOL_RE = re.compile(r"\bWorkflow\s+tool\b|`Workflow`|\bWorkflow\(")
CONVERSATION_RE = re.compile(
    r"\bthis conversation\b|\bearlier in the conversation\b|\bthe conversation so far\b"
    r"|\bwe are discussing\b|\bwe're discussing\b|\bwe\u2019re discussing\b|\bprevious message\b",
    re.IGNORECASE,
)
NUMBERED_STEP_RE = re.compile(r"^\s*\d+[.)]\s+\S")
STEP_HEADING_RE = re.compile(r"^#{1,6}\s*Step\s+\d+", re.IGNORECASE)
WRITE_STEP_RE = re.compile(
    r"\b(?:Write|Edit|MultiEdit|NotebookEdit)\b"
    r"|(?i:\b(?:write|edit|modify|overwrite|delete|create)s?\s+(?:the\s+|a\s+|an\s+|each\s+|every\s+)?"
    r"(?:\w+\s+)?files?\b)"
)
# M8 trigger clauses, exactly as rules.md lists them.
TRIGGER_RES = tuple(re.compile(pattern, re.IGNORECASE) for pattern in (
    r"\buse\s+(?:this\s+skill\s+)?(?:when|whenever|for|if)\b",
    r"\buse\s+it\s+when\b",
    r"\btriggers\s+(?:on|when)\b",
    r"\binvoke\s+(?:this\s+skill\s+)?when\b",
    r"\bactivates\s+when\b",
    r"\bwhen\s+(?:the\s+users?|users)\b",
))
# M8 first and second person, exactly as rules.md lists them: I, I'm, we, our,
# Let me, you, your, you're. "I" must stand alone, so "I/O" and "I-beam" pass.
PERSON_RE = re.compile(
    r"(?<![\w/.+-])I(?:'m|\u2019m)?(?![\w/+&-]|\.\w)"
    r"|(?i:\blet\s+me\b|\byou(?:'re|\u2019re)|\b(?:we|our|you|your)\b)"
)
_SOFT_SPACE = r"(?:[ \t]*\n[ \t]*|[ \t]+)"  # spaces, or one soft line wrap
WEAK_VERB_RE = re.compile(
    r"\bhandle(?:" + _SOFT_SPACE + r"[\w'-]+){0,3}?" + _SOFT_SPACE + r"(?:appropriately|properly)\b"
    r"|\b(?:consider|ensure|as" + _SOFT_SPACE + r"needed|as" + _SOFT_SPACE + r"appropriate"
    r"|if" + _SOFT_SPACE + r"applicable|where" + _SOFT_SPACE + r"relevant)\b",
    re.IGNORECASE,
)
EMPHASIS_RE = re.compile(r"\b(?:" + "|".join(EMPHASIS_WORDS) + r")\b")
# The two forms of dynamic context injection Claude Code runs. The fence form is
# written without overlapping quantifiers so an unclosed "```!" costs linear time.
INJECTION_INLINE_RE = re.compile(r"(?:^|(?<=\s))!`[^`]+`", re.MULTILINE)
INJECTION_FENCE_RE = re.compile(r"```![\s\S]*?```")
ARGUMENT_TOKEN_RE = re.compile(r"(?<!\\)\$(?:ARGUMENTS(?:\[\d+\])?|\d)")
TOC_HEADING_RE = re.compile(r"^#{1,6}\s*(?:table of )?contents\b", re.IGNORECASE)
DRIVE_BACKSLASH_RE = re.compile(r"\b[A-Za-z]:\\")
BUNDLED_BACKSLASH_RE = re.compile(r"\b(?:scripts|references|assets)\\")
_USER_PATH_BOUNDARY = r"(?:^|(?<=[\s'\"`(=:\[]))"
USER_DIR_RE = re.compile(
    _USER_PATH_BOUNDARY + r"(?:/mnt/[a-z])?/(?:Users|home)/(?P<unix>[^/\\\s`'\"|)\]]+)"
    r"|\b[A-Za-z]:[\\/]+[Uu]sers[\\/]+(?P<win>[^/\\\s`'\"|)\]]+)"
)
REAL_NAME_RE = re.compile(r"^[\w.-]+$")
SHELL_READ_RE = re.compile(
    r"(?:^|[;&|(]|\bthen\b|\bdo\b|\belse\b)\s*read\s+(?:-\w*p\w*\b|[A-Za-z_]\w*\s*(?:$|[;&|)]))"
)
_TRY_NODES = tuple({ast.Try, getattr(ast, "TryStar", ast.Try)})


class ValidatorEnvironmentError(Exception):
    """The validator cannot run here (PyYAML missing, SKILL.md unreadable)."""


def _one_line(text: str) -> str:
    """Collapse whitespace, so a finding never spans more than one output line."""
    return " ".join(str(text).split())


@dataclass(frozen=True)
class Finding:
    """One validator finding, printed in the rules.md contract format."""

    rule_id: str
    severity: str  # major | minor | style
    confidence: str  # definitive | check
    file: str  # POSIX path relative to the skill directory
    line: int  # 1-based; 0 when the finding has no line
    message: str

    def format(self) -> str:
        return (f"[{self.rule_id}] {self.severity} {self.confidence} "
                f"{_one_line(self.file)}:{self.line} {_one_line(self.message)}")


def severity_of(rule_id: str) -> str:
    """F and M* are Major, m* Minor, S* Style."""
    if rule_id == "F" or rule_id.startswith("M"):
        return MAJOR
    if rule_id.startswith("m"):
        return MINOR
    return STYLE


def _sort_key(finding: Finding) -> tuple:
    return (
        _SEVERITY_RANK[finding.severity],
        _CONFIDENCE_RANK[finding.confidence],
        _RULE_RANK.get(finding.rule_id, len(RULE_ORDER)),
        finding.file,
        finding.line,
    )


class _Collector:
    def __init__(self) -> None:
        self.items: list[Finding] = []

    def add(self, rule_id: str, confidence: str, file: str, line: int, message: str) -> None:
        self.items.append(Finding(rule_id, severity_of(rule_id), confidence, file, line, _one_line(message)))

    def sorted(self) -> list[Finding]:
        return sorted(self.items, key=_sort_key)


class _View:
    """Lines joined into one string, with offsets mapped back to file line numbers."""

    def __init__(self, lines: list[str], first_line: int) -> None:
        self.text = "\n".join(lines)
        self.first_line = first_line
        self._starts = []
        position = 0
        for line in lines:
            self._starts.append(position)
            position += len(line) + 1

    def line_of(self, offset: int) -> int:
        return self.first_line + bisect_right(self._starts, offset) - 1


@dataclass
class _Skill:
    root: Path
    raw: str  # SKILL.md as decoded, for the splitlines() counts of M1 and S3
    lines: list[str]  # SKILL.md with the BOM removed and newlines normalised to \n
    meta: dict
    body_index: int  # 0-based index of the first body line
    portable: bool

    @property
    def body_lines(self) -> list[str]:
        return self.lines[self.body_index:]

    @property
    def body_first_line(self) -> int:
        return self.body_index + 1


# --- Shared helpers -----------------------------------------------------------

def name_errors(name: str) -> list[str]:
    """Spec problems with a skill name (M9). Also used by init_skill.py."""
    problems = []
    if not NAME_PATTERN.fullmatch(name):
        problems.append(
            "use lowercase letters, digits, and single hyphens, with no leading or trailing hyphen"
        )
    if len(name) > MAX_NAME_LENGTH:
        problems.append(f"is {len(name)} characters; the limit is {MAX_NAME_LENGTH}")
    return problems


def folder_name_errors(folder: str) -> list[str]:
    """Reserved folder names that Claude Code will not load (M9)."""
    lowered = folder.lower()
    if lowered == RESERVED_FOLDER:
        return [f"the folder name '{folder}' is reserved by Claude Code"]
    if lowered.startswith(RESERVED_FOLDER_PREFIX):
        return [f"folder names starting with '{RESERVED_FOLDER_PREFIX}' are reserved"]
    return []


def _blank(match: re.Match) -> str:
    return re.sub(r"[^\n]", " ", match.group(0))


def _mask(pattern: re.Pattern, text: str) -> str:
    """Replace each match with spaces so offsets and line numbers stay valid."""
    return pattern.sub(_blank, text)


def _mask_inline_code(text: str, keep_identifiers: bool = False) -> str:
    if keep_identifiers:
        text = IDENTIFIER_CODE_RE.sub(lambda m: " " + m.group(1) + " ", text)
    return _mask(INLINE_CODE_RE, text)


def _fence_tags(lines: list[str]) -> list[str | None]:
    """Per line: None outside fenced code, else the fence's info tag ('' when untagged)."""
    tags: list[str | None] = []
    marker = None
    tag = None
    for line in lines:
        if marker is None:
            match = FENCE_OPEN_RE.match(line)
            if match:
                marker, tag = match.group(1), match.group(2).lower()
                tags.append(tag)
            else:
                tags.append(None)
            continue
        tags.append(tag)
        stripped = line.strip()
        if stripped and set(stripped) == {marker[0]} and len(stripped) >= len(marker):
            marker = None
    return tags


def _example_mask(lines: list[str]) -> list[bool]:
    """Per line: True inside an <example> block whose opening tag starts a line."""
    inside = False
    mask = []
    for line in lines:
        if not inside and EXAMPLE_OPEN_RE.match(line):
            inside = True
        mask.append(inside)
        if inside and "</example>" in line:
            inside = False
    return mask


def _read_error(exc: Exception) -> str:
    """Say why a file could not be read: the OS error text, or where the UTF-8 decoding failed."""
    if isinstance(exc, UnicodeDecodeError):
        return f"is not valid UTF-8 (byte offset {exc.start})"
    if isinstance(exc, OSError):
        return f"could not be read ({exc.strerror or exc})"
    return f"could not be read ({type(exc).__name__}: {exc})"


def _read_text_or_error(path: Path) -> tuple[str | None, str]:
    """Read a bundled text file as UTF-8: (text, '') or (None, why it failed)."""
    try:
        return path.read_text(encoding="utf-8-sig"), ""
    except (OSError, UnicodeDecodeError) as exc:
        return None, _read_error(exc)


def _read_text(path: Path) -> str | None:
    """Read a bundled text file as UTF-8, or return None when it cannot be read."""
    return _read_text_or_error(path)[0]


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _iter_files(directory: Path, pattern: str):
    skipped = {"__pycache__", "node_modules", ".git"}
    if not directory.is_dir():
        return
    for path in sorted(directory.rglob(pattern)):
        if path.is_file() and not skipped.intersection(path.relative_to(directory).parts):
            yield path


def _line_list(lines: list[int]) -> str:
    shown = ", ".join(str(n) for n in lines[:MAX_LISTED_LINES])
    return shown + (", ..." if len(lines) > MAX_LISTED_LINES else "")


def _key_line(skill: _Skill, key: str) -> int:
    pattern = re.compile(rf"^{re.escape(key)}\s*:")
    for index in range(1, skill.body_index):
        if pattern.match(skill.lines[index]):
            return index + 1
    return 1


def _folder_name(root: Path) -> str:
    """The skill's directory name as Claude Code sees it.

    os.path.abspath normalises "." and ".." without following links, so a skill
    installed through a symlink or junction keeps the link's name.
    """
    return Path(os.path.abspath(root)).name


def extract_bundled_paths(lines: list[str], first_line: int = 1) -> list[tuple[int, str | None, str]]:
    """Find this skill's bundled-path mentions: (line, sibling skill or None, path).

    Skips URLs, <example> blocks whose tags start a line, and placeholder tokens.
    A path ending in "/" names a directory.
    """
    found = []
    examples = _example_mask(lines)
    for offset, line in enumerate(lines):
        if examples[offset]:
            continue
        masked = EMPHASIS_UNDERSCORE_RE.sub(" ", _mask(URL_RE, line))
        for match in BUNDLED_PATH_RE.finditer(masked):
            token = _clean_path_token(match.group("path"))
            if token is None:
                continue
            found.append((first_line + offset, match.group("sibling"), token))
    return found


def _clean_path_token(token: str) -> str | None:
    """Strip what rules.md M5 says is not part of a path; None when the token is not a file reference."""
    token = re.split(r"[#?]", token, maxsplit=1)[0]
    token = token.rstrip(PATH_TRAILING_CHARS)
    token = PATH_SUFFIX_RE.sub("", token).rstrip(PATH_TRAILING_CHARS)  # :10-20 line ranges, :function
    if any(char in token for char in PATH_PLACEHOLDER_CHARS):
        return None
    if "xxx" in token.lower() or "..." in token or "\u2026" in token:
        return None
    head, _, rest = token.partition("/")
    if not rest.strip("/"):
        return head + "/"  # a bare "references/" mention names a directory
    # Filename-ish: an extension, a trailing slash (directory), or a nested path.
    # Prose such as "scripts/commands" (meaning "scripts or commands") has none.
    if "." not in rest.rsplit("/", 1)[-1] and not token.endswith("/") and "/" not in rest.rstrip("/"):
        return None
    return token


def _find_on_disk(base: Path, rel: str, want_dir: bool, listings: dict) -> tuple[bool, str | None]:
    """Look up rel under base one segment at a time, comparing names case-sensitively.

    Returns (found, spelling): found is True when rel exists with exactly this
    letter case; spelling is the on-disk name when only the case differs, which a
    case-insensitive file system (Windows, default macOS) would otherwise hide.
    """
    target = base / rel
    plain = target.is_dir() if want_dir else target.exists()
    normalised = posixpath.normpath(rel)
    parts = [part for part in normalised.split("/") if part not in ("", ".")]
    if not parts or parts[0] == "..":
        return plain, None
    current = base
    spelled = []
    case_differs = False
    for part in parts:
        key = str(current)
        if key not in listings:
            try:  # NFC, so a name stored decomposed (macOS) still compares equal
                listings[key] = [unicodedata.normalize("NFC", name) for name in os.listdir(current)]
            except OSError:
                listings[key] = None
        names = listings[key]
        if names is None:
            return plain, None  # an unlistable folder: fall back to the plain existence check
        part = unicodedata.normalize("NFC", part)
        if part in names:
            actual = part
        else:
            folded = [name for name in names if name.casefold() == part.casefold()]
            if not folded:
                return False, None
            actual = folded[0]
            case_differs = True
        spelled.append(actual)
        current = current / actual
    if want_dir and not current.is_dir():
        return False, None
    if case_differs:
        return False, "/".join(spelled)
    return True, None


# --- Parsing ------------------------------------------------------------------

def _read_skill_md(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ValidatorEnvironmentError(f"[env] cannot read {path}: {exc.strerror or exc}") from exc
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidatorEnvironmentError(
            f"[env] {path} is not valid UTF-8 (byte offset {exc.start}); re-save it as UTF-8"
        ) from exc


def _parse(root: Path, raw: str, out: _Collector, portable: bool) -> _Skill | None:
    text = raw.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    match = FRONTMATTER_RE.match(text)
    if not match:
        out.add("F", DEFINITIVE, SKILL_FILE, 1,
                "no YAML frontmatter: start the file with a '---' line and close the block with another '---' line")
        return None
    try:
        meta = yaml.safe_load(match.group(1))
    except (yaml.YAMLError, ValueError) as exc:
        mark = getattr(exc, "problem_mark", None)
        line = mark.line + FRONTMATTER_FIRST_LINE if mark is not None else 1
        problem = getattr(exc, "problem", None) or str(exc).splitlines()[0]
        out.add("F", DEFINITIVE, SKILL_FILE, line,
                f"frontmatter is not valid YAML ({problem}); quote values that contain ': ' or start with '[' or '{{'")
        return None
    except (RecursionError, MemoryError) as exc:
        out.add("F", DEFINITIVE, SKILL_FILE, 1,
                f"frontmatter is nested too deeply to parse ({type(exc).__name__}); flatten it")
        return None
    if not isinstance(meta, dict):
        out.add("F", DEFINITIVE, SKILL_FILE, 1, "frontmatter must be a mapping of keys to values")
        return None
    body_index = text.count("\n", 0, match.end()) + 1
    return _Skill(root, raw, text.split("\n"), meta, body_index, portable)


# --- Checks -------------------------------------------------------------------

def _check_f_triggers(skill: _Skill, out: _Collector) -> bool:
    """Report missing description or empty body; return True when the description is usable."""
    description = skill.meta.get("description")
    usable = False
    if "description" not in skill.meta:
        out.add("F", DEFINITIVE, SKILL_FILE, 1, "description is missing from the frontmatter")
    elif description is None or (isinstance(description, str) and not description.strip()):
        out.add("F", DEFINITIVE, SKILL_FILE, _key_line(skill, "description"), "description is empty")
    elif not isinstance(description, str):
        out.add("F", DEFINITIVE, SKILL_FILE, _key_line(skill, "description"),
                f"description must be a string (YAML read it as {type(description).__name__}); quote it")
    else:
        usable = True
    if not "\n".join(skill.body_lines).strip():
        out.add("F", DEFINITIVE, SKILL_FILE, skill.body_first_line,
                "the body is empty: add the instructions after the frontmatter")
    return usable


def _check_size(skill: _Skill, out: _Collector) -> None:
    line_count = len(skill.raw.splitlines())
    if line_count > MAX_SKILL_LINES:
        out.add("M1", DEFINITIVE, SKILL_FILE, 0,
                f"SKILL.md has {line_count} lines (limit {MAX_SKILL_LINES}); move detail into references/")
    char_count = len("\n".join(skill.lines))  # LF line endings, so a CRLF checkout counts the same
    if line_count > STYLE_MAX_LINES or char_count > STYLE_MAX_CHARS:
        out.add("S3", DEFINITIVE, SKILL_FILE, 0,
                f"SKILL.md has {line_count} lines and {char_count} characters "
                f"(house limits {STYLE_MAX_LINES} lines, {STYLE_MAX_CHARS} characters)")


def _governs_clause(prefix: str, negation: re.Pattern = CLAUSE_NEGATION_RE) -> bool:
    """True when a negation in prefix governs the clause that ends at the mention.

    A condition in the prefix stops it: a negation inside the condition ("If the
    format is not given ask the user") or before it ("Do not proceed until you
    ask the user") governs another verb.
    """
    conjunctions = list(CONJUNCTION_RE.finditer(prefix))
    if conjunctions:
        prefix = prefix[conjunctions[-1].end():]
    return CONDITION_RE.search(prefix) is None and negation.search(prefix) is not None


def _is_negated(text: str, start: int, end: int) -> bool:
    """True when the ask or wait at text[start:end] is negated in its own clause (rules.md M2).

    A negation counts when it follows the mention ("`AskUserQuestion` is not
    available"), when it sits right before it with only filler words between
    ("do not ever ask the user"), or when it governs the clause and the clause
    has no condition before the mention ("The subagent cannot reach or ask the
    user"). A negation inside or before a condition ("If the format is not given
    ask the user") does not count, and two negations cancel ("never edit without
    user approval").
    """
    if POST_NEGATION_RE.match(text, end):
        return True
    prefix = text[max(0, start - NEGATION_WINDOW):start]
    breaks = list(CLAUSE_BREAK_RE.finditer(prefix))
    if breaks:
        prefix = prefix[breaks[-1].end():]
    temporal = TEMPORAL_ASK_RE.match(text, start) is not None
    adjacent = (TEMPORAL_ADJACENT_NEGATION_RE if temporal else ADJACENT_NEGATION_RE).search(prefix)
    if adjacent:
        return not (adjacent.group(0).lower().startswith("without")
                    and _governs_clause(prefix[:adjacent.start()], DOUBLE_NEGATION_RE))
    if temporal:
        return False
    return _governs_clause(prefix)


def _find_pauses(lines: list[str], first_line: int) -> list[tuple[int, str]]:
    """Where Markdown lines ask or wait for the user (rules.md M2): sorted (line, quoted text), one per line."""
    tags = _fence_tags(lines)
    prose = ["" if tag is not None else line for line, tag in zip(lines, tags)]
    asking = _View([_mask_inline_code(line, keep_identifiers=True) for line in prose], first_line)
    text = asking.text
    imperative = [
        match for match in IMPERATIVE_ASK_RE.finditer(text)
        if IMPERATIVE_PREFIX_RE.search(text[text.rfind("\n", 0, match.start()) + 1:match.start()])
    ]
    found: dict[int, str] = {}
    for match in [*ASK_USER_RE.finditer(text), *imperative]:
        if not _is_negated(text, match.start(), match.end()):
            found.setdefault(asking.line_of(match.start()), match.group(0))
    for offset, line in enumerate(lines):  # choice prompts, code blocks included
        for match in CHOICE_PROMPT_RE.finditer(line):
            starts = list(QUESTION_START_RE.finditer(line, 0, match.start()))
            start = starts[-1].end() if starts else 0
            if not _is_negated(line, start, match.end()):
                found.setdefault(first_line + offset, line[start:match.end()].strip())
                break
    return sorted(found.items())


def _step_references(skill: _Skill, nofence: list[str]) -> list[tuple[str, int]]:
    """References SKILL.md sends Claude to as a step: (path, SKILL.md line), first mention of each.

    A reference counts when a prose line names it and is a numbered step
    ("1. **Intake**: use `references/intake.md`") or says to read it first
    ("Read `references/api.md` before writing code"). A numbered item that
    opens with the file ("1. `references/api.md`: endpoints") lists files, not steps.
    """
    steps: dict[str, int] = {}
    first = skill.body_first_line
    for line, sibling, token in extract_bundled_paths(skill.body_lines, first):
        text = nofence[line - first]
        if sibling or not token.startswith("references/") or not token.endswith(".md") or not text:
            continue
        marker = NUMBERED_STEP_RE.match(text)
        item = text[marker.end() - 1:].lstrip("*_[`(") if marker else ""
        step = marker is not None and not item.startswith((token, "./" + token, posixpath.basename(token)))
        if step or (READ_VERB_RE.search(text) and READ_FIRST_RE.search(text)):
            rel = posixpath.normpath(token)
            if rel.startswith("references/") and (skill.root / rel).is_file():
                steps.setdefault(rel, line)
    return list(steps.items())


def _reference_pauses(skill: _Skill, rel: str) -> list[tuple[int, str]]:
    text = _read_text(skill.root / rel)
    return [] if text is None else _find_pauses(text.splitlines(), 1)  # M5 reports an unreadable file


def _check_fork(skill: _Skill, out: _Collector, nofence: list[str]) -> None:
    if skill.meta.get("context") != "fork":
        return
    first = skill.body_first_line
    for line, quoted in _find_pauses(skill.body_lines, first):
        out.add("M2", DEFINITIVE, SKILL_FILE, line,
                f"context: fork is set but the body asks or waits for the user ('{_one_line(quoted)}'); "
                "a forked subagent cannot ask, so remove context: fork")
    steps = dict(_step_references(skill, nofence))
    for rel, step_line in steps.items():
        for line, quoted in _reference_pauses(skill, rel):
            out.add("M2", DEFINITIVE, rel, line,
                    f"context: fork is set but {rel}, which SKILL.md:{step_line} sends Claude to as a step, "
                    f"asks or waits for the user ('{_one_line(quoted)}'); "
                    "a forked subagent cannot ask, so remove context: fork")
    for rel in sorted(_linked_references(skill) - steps.keys()):
        if not (rel.startswith("references/") and rel.endswith(".md") and (skill.root / rel).is_file()):
            continue
        pauses = _reference_pauses(skill, rel)
        if pauses:
            also = f" (also lines {_line_list([line for line, _ in pauses[1:]])})" if len(pauses) > 1 else ""
            out.add("M2", CHECK, rel, pauses[0][0],
                    f"forked skill links {rel}, which asks or waits for the user ('{_one_line(pauses[0][1])}'){also}; "
                    "confirm whether the skill reads it on a path it takes")

    for offset, line in enumerate(nofence):
        if WORKFLOW_TOOL_RE.search(line):
            out.add("M2", CHECK, SKILL_FILE, first + offset,
                    "forked skill uses the Workflow tool, which subagents do not get")
    prose = _View([_mask_inline_code(line) for line in nofence], first)
    for match in CONVERSATION_RE.finditer(prose.text):
        out.add("M2", CHECK, SKILL_FILE, prose.line_of(match.start()),
                f"forked skill depends on the conversation ('{match.group(0)}'), which a fork does not see")
    if not any(NUMBERED_STEP_RE.match(line) or STEP_HEADING_RE.match(line) for line in nofence):
        out.add("M2", CHECK, SKILL_FILE, 0,
                "forked skill has no numbered steps; confirm it has an explicit task and is not guideline-only")
    agent = skill.meta.get("agent")
    if isinstance(agent, str) and agent in READ_ONLY_AGENTS:
        match = WRITE_STEP_RE.search(prose.text)
        if match:
            out.add("M2", CHECK, SKILL_FILE, prose.line_of(match.start()),
                    f"agent: {agent} is read-only but the body writes or edits files ('{match.group(0)}')")


def _check_bundled_paths(skill: _Skill, out: _Collector) -> None:
    listings: dict = {}
    parents = [Path(os.path.abspath(skill.root)).parent, skill.root.resolve().parent]
    problems: dict[tuple[str | None, str, str | None], list[int]] = {}
    for line, sibling, token in extract_bundled_paths(skill.body_lines, skill.body_first_line):
        want_dir = token.endswith("/")
        rel = token.rstrip("/")
        if sibling:
            results = [_find_on_disk(parent, f"{sibling}/{rel}", want_dir, listings) for parent in parents]
            found = any(result[0] for result in results)
            spelling = next((result[1] for result in results if result[1]), None)
        else:
            found, spelling = _find_on_disk(skill.root, rel, want_dir, listings)
        if not found:
            problems.setdefault((sibling, token, spelling), []).append(line)
    for (sibling, token, spelling), lines in problems.items():
        also = f" (also lines {_line_list(lines[1:])})" if len(lines) > 1 else ""
        kind = "directory" if token.endswith("/") else "file"
        on_disk = (spelling or "") + ("/" if token.endswith("/") else "")
        case_note = f"the name on disk is {on_disk}, so only the letter case differs"
        if sibling:
            state = case_note if spelling else "which is missing"
            out.add("M5", CHECK, SKILL_FILE, lines[0],
                    f"references ../{sibling}/{token}{also}, {state}; "
                    "confirm the sibling skill is a documented optional install")
        elif token.startswith("evals/"):
            state = case_note if spelling else "which is missing"
            out.add("M5", CHECK, SKILL_FILE, lines[0],
                    f"references {token}{also}, {state}; packaging strips evals/, "
                    "so confirm whether this names another skill's evals")
        elif spelling:
            out.add("M5", DEFINITIVE, SKILL_FILE, lines[0],
                    f"references the bundled {kind} {token}{also}, but {case_note}; "
                    "fix the case, because Linux and claude.ai are case-sensitive")
        else:
            out.add("M5", DEFINITIVE, SKILL_FILE, lines[0],
                    f"references the bundled {kind} {token}{also}, which does not exist; fix the path or add it")


def _is_catch_all(node: ast.expr | None) -> bool:
    if isinstance(node, ast.Name):
        return node.id in ("Exception", "BaseException")
    if isinstance(node, ast.Attribute):
        return node.attr in ("Exception", "BaseException")
    if isinstance(node, ast.Tuple):
        return any(_is_catch_all(element) for element in node.elts)
    return False


def _only_pass(body: list[ast.stmt]) -> bool:
    return all(
        isinstance(stmt, ast.Pass)
        or (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis)
        for stmt in body
    )


_FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
_COMPREHENSION_NODES = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def _bound_names(scope: ast.AST) -> set[str]:
    """Names bound directly in one scope (module, class, function, or lambda), not in nested scopes."""
    names: set[str] = set()
    if isinstance(scope, _FUNCTION_NODES):
        args = scope.args
        for arg in (*getattr(args, "posonlyargs", ()), *args.args, *args.kwonlyargs, args.vararg, args.kwarg):
            if arg is not None:
                names.add(arg.arg)
        stack = list(scope.body) if isinstance(scope.body, list) else [scope.body]
    else:
        stack = list(getattr(scope, "body", ()))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
            continue
        if isinstance(node, (ast.Lambda, *_COMPREHENSION_NODES)):
            continue
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            names.add(node.id)
        elif isinstance(node, ast.alias):
            names.add((node.asname or node.name).split(".")[0])
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
        stack.extend(ast.iter_child_nodes(node))
    return names


def _builtin_input_calls(tree: ast.Module) -> list[ast.Call]:
    """Calls to input() or raw_input() that reach the builtin.

    The name is shadowed only when it is bound at module level or in a function
    that encloses the call, the way Python resolves it; a local variable named
    input in another function does not hide a real call.
    """
    calls = []
    # A function that declares "global input" and assigns it rebinds the module name.
    declared_global = {
        name for node in ast.walk(tree) if isinstance(node, ast.Global) for name in node.names
    }
    module_names = frozenset(_bound_names(tree) | (declared_global & set(INPUT_BUILTINS)))
    # Each entry: (node, names visible at this point, names visible to nested functions).
    stack = [(child, module_names, module_names) for child in ast.iter_child_nodes(tree)]
    while stack:
        node, visible, enclosing = stack.pop()
        if isinstance(node, _FUNCTION_NODES):
            inner = enclosing | _bound_names(node)
            body = node.body if isinstance(node.body, list) else [node.body]
            stack.extend((child, inner, inner) for child in body)
            outer = [*getattr(node, "decorator_list", ()), *node.args.defaults,
                     *(d for d in node.args.kw_defaults if d is not None)]
            stack.extend((child, visible, enclosing) for child in outer)
            continue
        if isinstance(node, ast.ClassDef):
            class_names = enclosing | _bound_names(node)
            stack.extend((child, class_names, enclosing) for child in node.body)
            outer = [*node.decorator_list, *node.bases, *node.keywords]
            stack.extend((child, visible, enclosing) for child in outer)
            continue
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in INPUT_BUILTINS and node.func.id not in visible):
            calls.append(node)
        stack.extend((child, visible, enclosing) for child in ast.iter_child_nodes(node))
    return calls


def _interactive_reads(tree: ast.Module) -> tuple[list[tuple[int, str]], list[int]]:
    """getpass() calls (definitive) and sys.stdin reads (leads) in one script.

    Returns ([(line, call name)], [stdin read lines]). A script that calls
    isatty() guards its terminal input, so its stdin reads are not leads.
    """
    sys_names, stdin_names, getpass_modules, getpass_functions = set(), set(), set(), set()
    guarded = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "sys":
                    sys_names.add(alias.asname or "sys")
                elif alias.name == "getpass":
                    getpass_modules.add(alias.asname or "getpass")
        elif isinstance(node, ast.ImportFrom) and not node.level:
            for alias in node.names:
                if node.module == "sys" and alias.name == "stdin":
                    stdin_names.add(alias.asname or "stdin")
                elif node.module == "getpass" and alias.name == "getpass":
                    getpass_functions.add(alias.asname or "getpass")
        elif isinstance(node, ast.Attribute) and node.attr == "isatty":
            guarded = True

    def is_stdin(expr: ast.AST) -> bool:
        if isinstance(expr, ast.Attribute) and expr.attr == "buffer":
            expr = expr.value
        if isinstance(expr, ast.Attribute) and expr.attr == "stdin":
            return isinstance(expr.value, ast.Name) and expr.value.id in sys_names
        return isinstance(expr, ast.Name) and expr.id in stdin_names

    password_calls: list[tuple[int, str]] = []
    stdin_lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if (isinstance(func, ast.Attribute) and func.attr == "getpass"
                    and isinstance(func.value, ast.Name) and func.value.id in getpass_modules):
                password_calls.append((node.lineno, f"{func.value.id}.getpass"))
            elif isinstance(func, ast.Name) and func.id in getpass_functions:
                password_calls.append((node.lineno, func.id))
            elif isinstance(func, ast.Attribute) and func.attr in STDIN_READ_METHODS and is_stdin(func.value):
                stdin_lines.append(node.lineno)
            elif any(is_stdin(arg) for arg in node.args):
                stdin_lines.append(node.lineno)
        elif isinstance(node, (ast.For, ast.AsyncFor)) and is_stdin(node.iter):
            stdin_lines.append(node.lineno)
        elif isinstance(node, ast.comprehension) and is_stdin(node.iter):
            stdin_lines.append(getattr(node.iter, "lineno", 0))
    return password_calls, ([] if guarded else sorted(set(stdin_lines)))


def _parse_script(path: Path, rel: str, out: _Collector) -> ast.Module | None:
    source, error = _read_text_or_error(path)
    if source is None:
        out.add("M6", CHECK, rel, 0, f"{error}; review its error handling by hand")
        return None
    try:
        return ast.parse(source, filename=rel)
    except (SyntaxError, ValueError) as exc:
        line = getattr(exc, "lineno", None) or 0
        out.add("M6", CHECK, rel, line,
                f"does not parse as Python 3 ({type(exc).__name__}); review its error handling by hand")
    except (RecursionError, MemoryError) as exc:
        out.add("M6", CHECK, rel, 0,
                f"is too deeply nested to parse ({type(exc).__name__}); review its error handling by hand")
    return None


def _check_python_script(tree: ast.Module, rel: str, out: _Collector) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                out.add("M6", DEFINITIVE, rel, node.lineno,
                        "bare 'except:' hides every error; catch specific exceptions and print how to fix them")
            elif _is_catch_all(node.type) and _only_pass(node.body):
                out.add("M6", DEFINITIVE, rel, node.lineno,
                        "'except Exception: pass' swallows errors; catch specific exceptions and report them")
    for call in _builtin_input_calls(tree):
        out.add("M6", DEFINITIVE, rel, call.lineno,
                f"{call.func.id}() waits for interactive input; take it from arguments or environment variables")
    password_calls, stdin_lines = _interactive_reads(tree)
    for line, name in password_calls:
        out.add("M6", DEFINITIVE, rel, line,
                f"{name}() waits for interactive input; take the secret from an environment variable")
    if stdin_lines:
        also = f" (also lines {_line_list(stdin_lines[1:])})" if len(stdin_lines) > 1 else ""
        out.add("M6", CHECK, rel, stdin_lines[0],
                f"reads sys.stdin{also}; confirm it never waits on an interactive terminal "
                "(check sys.stdin.isatty() or take a file argument)")


def _check_shell_script(path: Path, rel: str, out: _Collector) -> None:
    source, error = _read_text_or_error(path)
    if source is None:
        out.add("M6", CHECK, rel, 0, f"{error}; review it by hand")
        return
    for number, line in enumerate(source.splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        if SHELL_READ_RE.search(line):
            out.add("M6", CHECK, rel, number,
                    "'read' may wait for interactive input; confirm stdin is always piped or take an argument")


def _catches_import_error(handler: ast.ExceptHandler) -> bool:
    names = {"ImportError", "ModuleNotFoundError", "Exception", "BaseException"}
    if handler.type is None:
        return True
    candidates = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
    return any(isinstance(c, ast.Name) and c.id in names for c in candidates)


def _unguarded_imports(tree: ast.Module):
    guarded = set()
    for node in ast.walk(tree):
        if isinstance(node, _TRY_NODES) and any(_catches_import_error(h) for h in node.handlers):
            for statement in node.body:
                guarded.update(id(sub) for sub in ast.walk(statement))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)) and id(node) not in guarded:
            yield node


def _check_scripts(skill: _Skill, out: _Collector) -> None:
    scripts_dir = skill.root / "scripts"
    py_files = list(_iter_files(scripts_dir, "*.py"))
    local_modules = {path.stem for path in py_files}
    if scripts_dir.is_dir():
        local_modules.update(p.name for p in scripts_dir.rglob("*") if p.is_dir())
    local_modules.update(p.name for p in skill.root.iterdir() if p.is_dir())
    skill_text = "\n".join(skill.lines)
    undeclared: dict[str, tuple[str, int]] = {}
    stdlib = getattr(sys, "stdlib_module_names", None)  # Python 3.10 and later
    if stdlib is None and py_files:
        out.add("m13", CHECK, _rel(skill.root, py_files[0]), 0,
                "the import check needs Python 3.10 or later and was skipped; confirm by hand that "
                "SKILL.md names every third-party package the scripts import")

    for path in py_files:
        rel = _rel(skill.root, path)
        tree = _parse_script(path, rel, out)
        if tree is None:
            continue
        _check_python_script(tree, rel, out)
        if stdlib is None:
            continue
        for node in _unguarded_imports(tree):
            if isinstance(node, ast.ImportFrom):
                if node.level or not node.module:
                    continue
                modules = [node.module]
            else:
                modules = [alias.name for alias in node.names]
            for module in modules:
                top = module.split(".")[0]
                if top in stdlib or top in local_modules or top in undeclared:
                    continue
                names = [top] + ([PIP_NAMES[top]] if top in PIP_NAMES else [])
                if any(re.search(rf"\b{re.escape(n)}\b", skill_text, re.IGNORECASE) for n in names):
                    continue
                undeclared[top] = (rel, node.lineno)
    for module, (rel, line) in undeclared.items():
        package = PIP_NAMES.get(module, module)
        out.add("m13", CHECK, rel, line,
                f"imports '{module}', which is not in the standard library and SKILL.md does not name it; "
                f"add 'Requires {package}: pip install {package}'")

    for path in _iter_files(scripts_dir, "*.sh"):
        _check_shell_script(path, _rel(skill.root, path), out)


def _check_weak_verbs_and_emphasis(skill: _Skill, out: _Collector, nofence: list[str]) -> None:
    quiet = _View([_mask(QUOTE_RE, _mask_inline_code(line)) for line in nofence], skill.body_first_line)
    weak = [quiet.line_of(m.start()) for m in WEAK_VERB_RE.finditer(quiet.text)]
    if len(weak) >= WEAK_VERB_THRESHOLD:
        out.add("M7", CHECK, SKILL_FILE, weak[0],
                f"{len(weak)} weak-verb uses (lines {_line_list(weak)}); confirm which are directives "
                "with no concrete action or default")
    shouted = [quiet.line_of(m.start()) for m in EMPHASIS_RE.finditer(quiet.text)]
    if len(shouted) >= EMPHASIS_THRESHOLD:
        out.add("m15", CHECK, SKILL_FILE, shouted[0],
                f"{len(shouted)} all-caps directives (lines {_line_list(shouted)}); "
                "state each rule in plain words with its reason")


def _person_phrases(text: str) -> list[str]:
    """First- and second-person words outside quotes and inline code (M8)."""
    masked = _mask(QUOTE_RE, _mask_inline_code(text))
    phrases = []
    for match in PERSON_RE.finditer(masked):
        if match.group(0).startswith("I") and ROMAN_NUMERAL_CONTEXT_RE.search(masked[:match.start()]):
            continue  # "Phase I", "Type I"
        phrases.append(match.group(0))
    return phrases


def _check_description(skill: _Skill, out: _Collector) -> None:
    description = skill.meta["description"]
    line = _key_line(skill, "description")
    when_to_use = skill.meta.get("when_to_use")
    when_to_use = when_to_use if isinstance(when_to_use, str) else ""
    trigger_text = description if skill.portable else f"{description}\n{when_to_use}"
    if not any(pattern.search(trigger_text) for pattern in TRIGGER_RES):
        where = "description" if skill.portable else "description or when_to_use"
        out.add("M8", DEFINITIVE, SKILL_FILE, line,
                f"no trigger clause in the {where}; add 'Use when ...' with the key use case first")
    fields = [("description", description)]
    if not skill.portable and when_to_use:
        fields.append(("when_to_use", when_to_use))
    for field, value in fields:
        phrases = _person_phrases(value)
        if phrases:
            out.add("M8", DEFINITIVE, SKILL_FILE, _key_line(skill, field),
                    f"{field} uses first or second person ({', '.join(dict.fromkeys(phrases))}); "
                    "write it in the third person")

    if len(description) > MAX_DESCRIPTION_LENGTH:
        out.add("M9", DEFINITIVE, SKILL_FILE, line,
                f"description is {len(description)} characters (limit {MAX_DESCRIPTION_LENGTH})")
    if "<" in description or ">" in description:
        out.add("M9", DEFINITIVE, SKILL_FILE, line, "description contains '<' or '>'; remove the angle brackets")
    if not skill.portable and len(description) + len(when_to_use) > MAX_LISTING_LENGTH:
        out.add("m12", DEFINITIVE, SKILL_FILE, line,
                f"description plus when_to_use is {len(description) + len(when_to_use)} characters; "
                f"the skill listing truncates at {MAX_LISTING_LENGTH}")
    _check_description_opening(description, line, out)


def _check_description_opening(description: str, line: int, out: _Collector) -> None:
    if TEMPLATE_MARKER in description:
        return  # an unfilled template; M9 already reports the placeholder
    match = re.match(r"[^A-Za-z]*([A-Za-z][A-Za-z'-]*)", description)
    word = match.group(1) if match else ""
    third_person = (
        word[:1].isupper()
        and word.endswith("s")
        and not word.lower().endswith(S6_NON_VERB_ENDINGS)
        and word not in S6_NON_VERBS
    )
    if not third_person:
        out.add("S6", DEFINITIVE, SKILL_FILE, line,
                f"description opens with '{word}'; open with a third-person verb such as 'Extracts' or 'Reviews'")


def _check_frontmatter_keys(skill: _Skill, out: _Collector) -> None:
    meta = skill.meta
    name = meta.get("name")
    folder = _folder_name(skill.root)
    if "name" in meta:
        name_line = _key_line(skill, "name")
        if not isinstance(name, str):
            out.add("M9", DEFINITIVE, SKILL_FILE, name_line,
                    f"name must be a string (YAML read it as {type(name).__name__}); quote it")
        else:
            for problem in name_errors(name):
                out.add("M9", DEFINITIVE, SKILL_FILE, name_line, f"name '{name}' {problem}")
            if name != folder:
                out.add("M9", DEFINITIVE, SKILL_FILE, name_line,
                        f"name '{name}' does not match the folder name '{folder}'")
            reserved = [word for word in RESERVED_NAME_WORDS if word in name.lower()]
            if reserved:
                rule = "M9" if skill.portable else "m12"
                out.add(rule, DEFINITIVE, SKILL_FILE, name_line,
                        f"name contains the reserved word '{reserved[0]}', which blocks upload to claude.ai and the API")
    elif skill.portable:
        out.add("M9", DEFINITIVE, SKILL_FILE, 1, "name is missing; the portable target requires it")

    for problem in folder_name_errors(folder):
        out.add("M9", DEFINITIVE, ".", 0, problem)

    known = PORTABLE_KEYS if skill.portable else CLAUDE_CODE_KEYS
    for key in meta:
        if str(key) not in known:
            target = "the portable target" if skill.portable else "Claude Code"
            out.add("M9" if skill.portable else "m12", DEFINITIVE, SKILL_FILE, _key_line(skill, str(key)),
                    f"frontmatter key '{key}' is unknown to {target}; fix the spelling or remove it")

    if not skill.portable and meta.get("context") != "fork":
        for key in FORK_ONLY_KEYS:
            if key in meta:
                out.add("m12", DEFINITIVE, SKILL_FILE, _key_line(skill, key),
                        f"{key} is set without context: fork, so it has no effect; remove it")

    if skill.portable:
        compatibility = meta.get("compatibility")
        if isinstance(compatibility, str) and len(compatibility) > MAX_COMPATIBILITY_LENGTH:
            out.add("M9", DEFINITIVE, SKILL_FILE, _key_line(skill, "compatibility"),
                    f"compatibility is {len(compatibility)} characters (limit {MAX_COMPATIBILITY_LENGTH})")
        metadata = meta.get("metadata")
        if metadata is not None and not (
            isinstance(metadata, dict)
            and all(isinstance(k, str) and isinstance(v, str) for k, v in metadata.items())
        ):
            out.add("M9", DEFINITIVE, SKILL_FILE, _key_line(skill, "metadata"),
                    "metadata must map strings to strings for the portable target")


def _check_leftovers(skill: _Skill, out: _Collector) -> None:
    for index, line in enumerate(skill.lines):
        if TEMPLATE_MARKER in line:
            out.add("M9", DEFINITIVE, SKILL_FILE, index + 1,
                    "template placeholder '[TODO' remains; replace it with real content")
    for placeholder in INIT_PLACEHOLDER_FILES:
        if (skill.root / placeholder).exists():
            out.add("M9", DEFINITIVE, placeholder, 0, "init placeholder file remains; delete it or replace it")
    body = _View(skill.body_lines, skill.body_first_line)
    injected = sorted({
        body.line_of(match.start())
        for pattern in (INJECTION_INLINE_RE, INJECTION_FENCE_RE)
        for match in pattern.finditer(body.text)
    })
    for line in injected:
        out.add("M9", CHECK, SKILL_FILE, line,
                "dynamic context injection syntax runs a command on every invocation; "
                "confirm it is intended or move the demonstration into references/")


def _check_argument_tokens(skill: _Skill, out: _Collector, fence_tags: list[str | None]) -> None:
    examples = _example_mask(skill.body_lines)
    for offset, line in enumerate(skill.body_lines):
        if fence_tags[offset] is None and not examples[offset]:
            continue
        match = ARGUMENT_TOKEN_RE.search(line)
        if match:
            out.add("m12", CHECK, SKILL_FILE, skill.body_first_line + offset,
                    f"'{match.group(0)}' inside an example or code block is substituted at invocation; "
                    "escape it as \\$ or move the example into references/")


def _reference_files(skill: _Skill) -> list[Path]:
    return list(_iter_files(skill.root / "references", "*.md"))


def _check_reference_tocs(skill: _Skill, out: _Collector, references: list[Path]) -> None:
    for path in references:
        rel = _rel(skill.root, path)
        text, error = _read_text_or_error(path)
        if text is None:
            out.add("M5", CHECK, rel, 0, f"reference {error}")
            continue
        lines = text.splitlines()
        if len(lines) > REFERENCE_TOC_MIN_LINES and not any(
            TOC_HEADING_RE.match(line.strip()) for line in lines[:REFERENCE_TOC_WINDOW]
        ):
            out.add("m9", DEFINITIVE, rel, 1,
                    f"{len(lines)} lines with no '## Contents' heading in the first {REFERENCE_TOC_WINDOW} lines")


def _linked_references(skill: _Skill) -> set[str]:
    """The references/ paths SKILL.md names, normalised (rules.md m10 and M2)."""
    return {
        posixpath.normpath(token.rstrip("/"))
        for _, sibling, token in extract_bundled_paths(skill.body_lines, skill.body_first_line)
        if sibling is None and token.startswith("references/")
    }


def _check_reference_chains(skill: _Skill, out: _Collector) -> None:
    linked = _linked_references(skill)
    for rel in sorted(linked):
        path = skill.root / rel
        if path.suffix != ".md" or not path.is_file():
            continue
        text = _read_text(path)
        if text is None:
            continue
        lines = text.splitlines()
        targets: dict[str, int] = {}
        for number, _, token in extract_bundled_paths(lines):
            if token.startswith("references/"):
                targets.setdefault(posixpath.normpath(token.rstrip("/")), number)
        base = posixpath.dirname(rel)
        for number, line in enumerate(lines, 1):
            for match in MARKDOWN_LINK_RE.finditer(_mask(URL_RE, line)):
                link = match.group(1).split("#", 1)[0]
                if not link or link.startswith("/") or ":" in link:
                    continue
                # Resolve the link by its text, not on disk, so a references/ folder that is
                # a symlink or junction to a folder outside the skill still maps back into it.
                target = posixpath.normpath(posixpath.join(base, link))
                if target.startswith("references/"):
                    targets.setdefault(target, number)
        for target, number in targets.items():
            if target == rel or target in linked or not (skill.root / target).is_file():
                continue
            out.add("m10", CHECK, rel, number,
                    f"links {target}, which SKILL.md does not link; link it from SKILL.md if it holds essential content")


def _check_paths_in_markdown(skill: _Skill, out: _Collector, references: list[Path]) -> None:
    documents = [(SKILL_FILE, skill.lines)]
    for path in references:
        text = _read_text(path)
        if text is not None:
            documents.append((_rel(skill.root, path), text.splitlines()))
    for rel, lines in documents:
        tags = _fence_tags(lines)
        for index, line in enumerate(lines):
            if tags[index] in SHELL_FENCE_TAGS:
                continue
            masked = _mask(URL_RE, line)
            problem = None
            if DRIVE_BACKSLASH_RE.search(masked) or BUNDLED_BACKSLASH_RE.search(masked):
                problem = "backslash path; use forward slashes and paths relative to the skill directory"
            else:
                for match in USER_DIR_RE.finditer(masked):
                    user = match.group("unix") or match.group("win")
                    if user.lower() in PLACEHOLDER_USER_NAMES or user.startswith(PLACEHOLDER_NAME_STARTS):
                        continue
                    if REAL_NAME_RE.match(user):
                        problem = (f"user-specific absolute path ('{match.group(0)}'); "
                                   "use a placeholder such as /Users/username/ or a relative path")
                        break
            if problem:
                out.add("m11", DEFINITIVE, rel, index + 1, problem)


def _check_layout(skill: _Skill, out: _Collector, nofence: list[str]) -> None:
    # A mention in inline code ("wrap it in `<instructions>`") is not a block.
    if not any(INSTRUCTIONS_TAG in _mask_inline_code(line) for line in nofence):
        out.add("S1", DEFINITIVE, SKILL_FILE, 0, "no <instructions> block; wrap the workflow in <instructions> tags")
    examples = sum(1 for line in nofence if EXAMPLE_OPEN_RE.match(line))
    if not MIN_EXAMPLES <= examples <= MAX_EXAMPLES:
        out.add("S2", DEFINITIVE, SKILL_FILE, 0,
                f"{examples} <example> blocks; keep {MIN_EXAMPLES}-{MAX_EXAMPLES} short ones in SKILL.md")

    for entry in sorted(skill.root.iterdir()):
        name = entry.name
        if name.startswith(".") or name == SKILL_FILE or name.startswith(LICENSE_PREFIX):
            continue
        if entry.is_dir() and name in ALLOWED_ROOT_DIRS:
            continue
        out.add("S4", DEFINITIVE, name, 0,
                "unexpected entry in the skill root; move it under scripts/, references/, assets/, evals/, or tests/")

    stems = [path.stem for path in _iter_files(skill.root / "references", "*.md")]
    if any("-" in stem for stem in stems) and any("_" in stem for stem in stems):
        out.add("S7", DEFINITIVE, "references", 0,
                "reference filenames mix '-' and '_'; pick one separator")


def _load_json(path: Path):
    """Parse a JSON file: (data, None), or (None, why it failed) with the OS or parser detail."""
    try:
        text = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise
    except (OSError, UnicodeDecodeError) as exc:
        return None, _read_error(exc)
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, f"is not valid JSON (line {exc.lineno} column {exc.colno}: {exc.msg})"
    except (RecursionError, MemoryError) as exc:
        return None, f"is nested too deeply to parse ({type(exc).__name__})"


def _check_evals(skill: _Skill, out: _Collector) -> None:
    evals_file = skill.root / "evals" / "evals.json"
    try:
        data, problem = _load_json(evals_file)
    except FileNotFoundError:
        data, problem = None, "is missing; write it before the skill (see the evals format in rules.md)"
    if problem is None:
        cases = data.get("evals") if isinstance(data, dict) else None
        if not isinstance(cases, list) or len(cases) < MIN_EVAL_CASES:
            count = len(cases) if isinstance(cases, list) else 0
            problem = f"has {count} cases in 'evals'; write at least {MIN_EVAL_CASES}"
    if problem:
        out.add("S5", DEFINITIVE, "evals/evals.json", 0, f"evals/evals.json {problem}")

    queries_file = skill.root / "evals" / "trigger_queries.json"
    try:
        queries, problem = _load_json(queries_file)
    except FileNotFoundError:
        queries, problem = None, "is missing; list about 10 queries, half of them near-misses"
    if problem is None:
        valid = isinstance(queries, list) and queries and all(
            isinstance(q, dict) and isinstance(q.get("query"), str) and isinstance(q.get("should_trigger"), bool)
            for q in queries
        )
        if not valid:
            problem = "must be a non-empty list of {\"query\": str, \"should_trigger\": bool} objects"
    if problem:
        out.add("S5", DEFINITIVE, "evals/trigger_queries.json", 0, f"evals/trigger_queries.json {problem}")


# --- Public API ---------------------------------------------------------------

def collect_findings(skill_path, portable: bool = False) -> list[Finding]:
    """Run every check on one skill directory and return the sorted findings.

    Raises ValidatorEnvironmentError when PyYAML is missing or SKILL.md cannot be read.
    """
    if yaml is None:
        raise ValidatorEnvironmentError(PYYAML_HINT)
    root = Path(skill_path)
    out = _Collector()
    if not root.is_dir():
        out.add("F", DEFINITIVE, ".", 0, f"skill directory not found: {root}")
        return out.sorted()
    try:
        entries = {entry.name for entry in root.iterdir()}
    except OSError as exc:
        raise ValidatorEnvironmentError(f"[env] cannot list {root}: {exc.strerror or exc}") from exc
    if SKILL_FILE not in entries:
        other = next((name for name in entries if name.lower() == SKILL_FILE.lower()), None)
        hint = f" (found {other}; the file name is case-sensitive)" if other else ""
        out.add("F", DEFINITIVE, SKILL_FILE, 0, f"SKILL.md not found{hint}")
        return out.sorted()

    skill = _parse(root, _read_skill_md(root / SKILL_FILE), out, portable)
    if skill is None:
        return out.sorted()

    description_usable = _check_f_triggers(skill, out)
    fence_tags = _fence_tags(skill.body_lines)
    nofence = ["" if tag is not None else line for line, tag in zip(skill.body_lines, fence_tags)]
    references = _reference_files(skill)

    _check_size(skill, out)
    _check_fork(skill, out, nofence)
    _check_bundled_paths(skill, out)
    _check_scripts(skill, out)
    _check_weak_verbs_and_emphasis(skill, out, nofence)
    if description_usable:
        _check_description(skill, out)
    _check_frontmatter_keys(skill, out)
    _check_leftovers(skill, out)
    _check_argument_tokens(skill, out, fence_tags)
    _check_reference_tocs(skill, out, references)
    _check_reference_chains(skill, out)
    _check_paths_in_markdown(skill, out, references)
    _check_layout(skill, out, nofence)
    _check_evals(skill, out)
    return out.sorted()


def exit_code_for(findings: list[Finding]) -> int:
    definitive = [f for f in findings if f.confidence == DEFINITIVE]
    if any(f.severity == MAJOR for f in definitive):
        return EXIT_MAJOR
    if any(f.severity == MINOR for f in definitive):
        return EXIT_MINOR
    return EXIT_OK


def summary_line(findings: list[Finding]) -> str:
    definitive = [f for f in findings if f.confidence == DEFINITIVE]
    counts = {severity: sum(1 for f in definitive if f.severity == severity) for severity in (MAJOR, MINOR, STYLE)}
    checks = sum(1 for f in findings if f.confidence == CHECK)
    return f"RESULT major={counts[MAJOR]} minor={counts[MINOR]} style={counts[STYLE]} checks={checks}"


def internal_error_message(exc: BaseException) -> str:
    """The one-line report for a crash, so callers never mistake it for a finding."""
    return _one_line(f"[env] internal error: {type(exc).__name__}: {exc}")


def validate_skill(skill_path, portable: bool = False) -> tuple[bool, str, list[str]]:
    """Compatibility shim for package_skill.py: (valid, message, warnings).

    valid is False when any definitive Major (including F) is found, and also
    when the validator cannot run; warnings holds every other finding, formatted.
    """
    try:
        findings = collect_findings(skill_path, portable)
    except ValidatorEnvironmentError as exc:
        return False, str(exc), []
    except Exception as exc:  # an internal error must block packaging, not crash it
        return False, internal_error_message(exc), []
    blocking = [f for f in findings if f.severity == MAJOR and f.confidence == DEFINITIVE]
    warnings = [f.format() for f in findings if f not in blocking]
    if blocking:
        return False, "\n".join(f.format() for f in blocking), warnings
    if warnings:
        return True, f"Skill is valid with {len(warnings)} non-blocking finding(s)", warnings
    return True, "Skill is valid", warnings


def _configure_output() -> None:
    """Replace unencodable characters instead of crashing on cp1252 consoles and pipes."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scripts/quick_validate.py",
        description="Validate a skill against review-skill's rules.md and print one line per finding.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Output: [<ID>] <major|minor|style> <definitive|check> <file>:<line> <message>\n"
            "        RESULT major=<n> minor=<n> style=<n> checks=<n>\n\n"
            "Exit codes:\n"
            "  0  no definitive Major or Minor\n"
            "  1  at least one definitive Major (F triggers count as Major)\n"
            "  2  usage error\n"
            "  3  environment error (PyYAML missing: python -m pip install pyyaml; unreadable SKILL.md;\n"
            "     an internal error, printed as '[env] internal error: ...')\n"
            "  4  definitive Minor only\n"
            "Check lines and Style findings never change the exit code."
        ),
    )
    parser.add_argument("skill_dir", help="path to the skill directory (the folder holding SKILL.md)")
    parser.add_argument(
        "--portable", action="store_true",
        help="grade for claude.ai, the Claude API, and other Agent Skills clients instead of Claude Code",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_output()
    parser = build_parser()
    args = parser.parse_args(argv)  # usage errors exit 2 through SystemExit, which is not caught below
    if not Path(args.skill_dir).is_dir():
        parser.error(f"not a directory: {args.skill_dir}")
    try:
        findings = collect_findings(args.skill_dir, portable=args.portable)
        for finding in findings:
            print(finding.format())
        print(summary_line(findings))
        return exit_code_for(findings)
    except ValidatorEnvironmentError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_ENV
    except Exception as exc:  # a crash must exit 3, never 1, which means "definitive Major"
        print(internal_error_message(exc), file=sys.stderr)
        return EXIT_ENV


if __name__ == "__main__":
    sys.exit(main())
