"""Fixture tests for create-skill/scripts/quick_validate.py.

Each test writes a skill into a temporary folder, changes one thing from the
clean baseline in _helpers, and checks which rule IDs the validator reports.
"""

from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import _helpers
from _helpers import (
    CLEAN_BODY, CLEAN_DESCRIPTION, CLEAN_NAME, make_dir_link, make_skill, run_script, write_file,
)

import quick_validate as qv

FINDING_LINE = re.compile(r"^\[(\w+)\] (major|minor|style) (definitive|check) \S+:\d+ \S.*$")
RESULT_LINE = re.compile(r"^RESULT major=\d+ minor=\d+ style=\d+ checks=\d+$")

FORK = f"name: {CLEAN_NAME}\ndescription: {CLEAN_DESCRIPTION}\ncontext: fork\n"


def body_with(extra: str) -> str:
    """The clean body with one extra paragraph before the examples."""
    return CLEAN_BODY.replace("## Examples", f"{extra}\n\n## Examples", 1)


class ValidatorCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def findings(self, skill: Path, portable: bool = False) -> list[qv.Finding]:
        return qv.collect_findings(skill, portable=portable)

    def ids(self, skill: Path, confidence: str | None = None, portable: bool = False) -> set[str]:
        return {
            f.rule_id for f in self.findings(skill, portable)
            if confidence is None or f.confidence == confidence
        }

    def assertClean(self, skill: Path, portable: bool = False) -> None:
        found = [f.format() for f in self.findings(skill, portable)]
        self.assertEqual([], found, "expected zero findings")


class BaselineAndParsing(ValidatorCase):
    def test_clean_baseline_has_no_findings(self):
        self.assertClean(make_skill(self.tmp))

    def test_folded_description(self):
        fm = (f"name: {CLEAN_NAME}\ndescription: >-\n  Converts CSV files into short summary reports.\n"
              "  Use when the user asks to summarise a CSV file.\n")
        self.assertClean(make_skill(self.tmp, frontmatter=fm))

    def test_literal_description(self):
        fm = (f"name: {CLEAN_NAME}\ndescription: |\n  Converts CSV files into short summary reports.\n"
              "  Use when the user asks to summarise a CSV file.\n")
        self.assertClean(make_skill(self.tmp, frontmatter=fm))

    def test_plain_multiline_description(self):
        fm = (f"name: {CLEAN_NAME}\ndescription: Converts CSV files into short summary reports.\n"
              "  Use when the user asks to summarise a CSV file.\n")
        self.assertClean(make_skill(self.tmp, frontmatter=fm))

    def test_quoted_description_with_colon(self):
        fm = f'name: {CLEAN_NAME}\ndescription: "Converts CSV files: summaries. Use when the user asks for one."\n'
        self.assertClean(make_skill(self.tmp, frontmatter=fm))

    def test_crlf_file(self):
        self.assertClean(make_skill(self.tmp, newline="\r\n"))

    def test_bom_file(self):
        self.assertClean(make_skill(self.tmp, bom=True))

    def test_bom_and_crlf_together(self):
        self.assertClean(make_skill(self.tmp, newline="\r\n", bom=True))

    def test_quoted_name(self):
        fm = f'name: "{CLEAN_NAME}"\ndescription: {CLEAN_DESCRIPTION}\n'
        self.assertClean(make_skill(self.tmp, frontmatter=fm))


class FTriggers(ValidatorCase):
    def test_missing_skill_md(self):
        (self.tmp / "empty-skill").mkdir()
        self.assertEqual({"F"}, self.ids(self.tmp / "empty-skill"))

    def test_no_frontmatter(self):
        skill = self.tmp / CLEAN_NAME
        write_file(skill / "SKILL.md", CLEAN_BODY)
        self.assertEqual({"F"}, self.ids(skill))

    def test_yaml_error(self):
        fm = f"name: {CLEAN_NAME}\ndescription: Converts: CSV: files\n  bad: [indent\n"
        self.assertEqual({"F"}, self.ids(make_skill(self.tmp, frontmatter=fm)))

    def test_missing_description(self):
        self.assertIn("F", self.ids(make_skill(self.tmp, frontmatter=f"name: {CLEAN_NAME}\n")))

    def test_empty_body(self):
        self.assertIn("F", self.ids(make_skill(self.tmp, body="\n")))

    def test_f_counts_as_major_for_exit_code(self):
        (self.tmp / "empty-skill").mkdir()
        result = run_script("quick_validate.py", str(self.tmp / "empty-skill"))
        self.assertEqual(1, result.returncode)
        self.assertIn("[F] major definitive", result.stdout)


class NameAndKeys(ValidatorCase):
    def test_name_must_match_folder(self):
        skill = make_skill(self.tmp, folder="other-folder")
        found = [f for f in self.findings(skill) if f.rule_id == "M9"]
        self.assertTrue(any("does not match the folder" in f.message for f in found))

    def test_invalid_name_characters(self):
        fm = f"name: Bad_Name\ndescription: {CLEAN_DESCRIPTION}\n"
        self.assertIn("M9", self.ids(make_skill(self.tmp, frontmatter=fm, folder="Bad_Name")))

    def test_unknown_key_is_m12(self):
        fm = f"name: {CLEAN_NAME}\ndescription: {CLEAN_DESCRIPTION}\ncolour: blue\n"
        self.assertEqual({"m12"}, self.ids(make_skill(self.tmp, frontmatter=fm)))

    def test_unknown_key_is_m9_when_portable(self):
        fm = f"name: {CLEAN_NAME}\ndescription: {CLEAN_DESCRIPTION}\ncontext: fork\n"
        skill = make_skill(self.tmp, frontmatter=fm)
        self.assertIn("M9", self.ids(skill, portable=True))
        self.assertNotIn("m12", self.ids(skill, portable=True))

    def test_agent_without_fork_is_m12(self):
        fm = f"name: {CLEAN_NAME}\ndescription: {CLEAN_DESCRIPTION}\nagent: Explore\n"
        found = [f for f in self.findings(make_skill(self.tmp, frontmatter=fm)) if f.rule_id == "m12"]
        self.assertTrue(any("without context: fork" in f.message for f in found))

    def test_reserved_word_in_name(self):
        name = "claude-helper"
        fm = f"name: {name}\ndescription: {CLEAN_DESCRIPTION}\n"
        skill = make_skill(self.tmp, name=name, frontmatter=fm)
        self.assertEqual({"m12"}, self.ids(skill))
        portable = self.ids(skill, portable=True)
        self.assertIn("M9", portable)
        self.assertNotIn("m12", portable)

    def test_reserved_folder_names(self):
        for folder in ("synced", "anthropic-skills-extra"):
            fm = f"name: {folder}\ndescription: {CLEAN_DESCRIPTION}\n"
            self.assertIn("M9", self.ids(make_skill(self.tmp, name=folder, frontmatter=fm)), folder)

    def test_portable_requires_name(self):
        skill = make_skill(self.tmp, frontmatter=f"description: {CLEAN_DESCRIPTION}\n")
        self.assertNotIn("M9", self.ids(skill))
        self.assertIn("M9", self.ids(skill, portable=True))

    def test_listing_budget(self):
        long_text = "Summarises CSV columns in detail. " * 50  # 1700 characters with the description
        fm = (f"name: {CLEAN_NAME}\ndescription: {CLEAN_DESCRIPTION}\n"
              f"when_to_use: {long_text.strip()}\n")
        found = [f for f in self.findings(make_skill(self.tmp, frontmatter=fm)) if f.rule_id == "m12"]
        self.assertTrue(any("1536" in f.message for f in found))


class Description(ValidatorCase):
    def description_ids(self, description: str) -> set[str]:
        fm = f"name: {CLEAN_NAME}\ndescription: {description}\n"
        return self.ids(make_skill(self.tmp, frontmatter=fm))

    def test_use_this_skill_whenever_has_trigger(self):
        self.assertNotIn("M8", self.description_ids("Use this skill whenever the user wants to edit Word files."))

    def test_create_new_skills_has_trigger(self):
        ids = self.description_ids(
            "Create new skills and improve existing ones. Use when users want to build a skill."
        )
        self.assertNotIn("M8", ids)

    def test_second_person_is_m8(self):
        self.assertIn("M8", self.description_ids("You can use this to edit files."))

    def test_first_person_is_m8(self):
        self.assertIn("M8", self.description_ids("I can summarise CSV files. Use when the user asks."))

    def test_missing_trigger_is_m8(self):
        self.assertIn("M8", self.description_ids("Converts CSV files into reports."))

    def test_when_to_use_satisfies_trigger_in_claude_code_only(self):
        fm = (f"name: {CLEAN_NAME}\ndescription: Converts CSV files into reports.\n"
              "when_to_use: Use when the user asks for a CSV summary.\n")
        skill = make_skill(self.tmp, frontmatter=fm)
        self.assertNotIn("M8", self.ids(skill))
        self.assertIn("M8", self.ids(skill, portable=True))

    def test_angle_brackets_are_m9(self):
        self.assertIn("M9", self.description_ids('"Converts <csv> files. Use when the user asks."'))

    def test_non_verb_opening_is_s6(self):
        self.assertEqual({"S6"}, self.description_ids("CSV summaries for reports. Use when the user asks."))


class ForkRules(ValidatorCase):
    def test_fork_and_ask_the_user_is_definitive_m2(self):
        skill = make_skill(self.tmp, frontmatter=FORK, body=body_with("Ask the user which format to use."))
        self.assertIn("M2", self.ids(skill, confidence=qv.DEFINITIVE))

    def test_fork_and_ask_user_question_tool_in_code_span(self):
        skill = make_skill(self.tmp, frontmatter=FORK, body=body_with("Call `AskUserQuestion` for the format."))
        self.assertIn("M2", self.ids(skill, confidence=qv.DEFINITIVE))

    def test_negated_wait_is_not_m2(self):
        skill = make_skill(self.tmp, frontmatter=FORK, body=body_with("Do not wait for user confirmation."))
        self.assertNotIn("M2", self.ids(skill))

    def test_negation_in_an_earlier_clause_does_not_hide_m2(self):
        skill = make_skill(self.tmp, frontmatter=FORK,
                           body=body_with("If the format is not given, ask the user."))
        self.assertIn("M2", self.ids(skill, confidence=qv.DEFINITIVE))

    def test_fork_with_agent_dispatch_is_not_definitive_m2(self):
        skill = make_skill(self.tmp, frontmatter=FORK,
                           body=body_with("Dispatch one subagent per file with the Agent tool."))
        self.assertNotIn("M2", self.ids(skill, confidence=qv.DEFINITIVE))

    def test_missing_fork_is_never_flagged(self):
        skill = make_skill(self.tmp, body=body_with("Ask the user which format to use."))
        self.assertNotIn("M2", self.ids(skill))

    def test_fork_heuristics_are_checks(self):
        body = body_with("Use the Workflow tool to fan out.\n\nFix the bug we are discussing.")
        found = [f for f in self.findings(make_skill(self.tmp, frontmatter=FORK, body=body)) if f.rule_id == "M2"]
        self.assertGreaterEqual(len(found), 2)
        self.assertTrue(all(f.confidence == qv.CHECK for f in found))

    def test_fork_without_steps_is_a_check(self):
        body = "# Style guide\n\nPrefer short sentences.\n\n<instructions>\nWrite plainly.\n</instructions>\n"
        found = [f for f in self.findings(make_skill(self.tmp, frontmatter=FORK, body=body)) if f.rule_id == "M2"]
        self.assertEqual([qv.CHECK], [f.confidence for f in found])


class BundledPaths(ValidatorCase):
    def test_skill_dir_variable_resolves_to_existing_file(self):
        skill = make_skill(self.tmp, body=body_with("Run `python ${CLAUDE_SKILL_DIR}/scripts/run.py data.csv`."))
        write_file(skill / "scripts" / "run.py", "print('ok')\n")
        self.assertNotIn("M5", self.ids(skill))

    def test_skill_dir_variable_to_missing_file_is_m5(self):
        skill = make_skill(self.tmp, body=body_with("Run `python ${CLAUDE_SKILL_DIR}/scripts/run.py data.csv`."))
        self.assertIn("M5", self.ids(skill, confidence=qv.DEFINITIVE))

    def test_plain_missing_reference_is_m5(self):
        skill = make_skill(self.tmp, body=body_with("Read [the guide](references/guide.md) first."))
        self.assertIn("M5", self.ids(skill, confidence=qv.DEFINITIVE))

    def test_other_tree_paths_are_not_this_skill(self):
        body = body_with(
            "Run `python ooxml/scripts/pack.py out.docx` from the repo.\n\n"
            "See skills/pdf/scripts/fill.py and https://example.com/repo/scripts/tool.py for details."
        )
        self.assertNotIn("M5", self.ids(make_skill(self.tmp, body=body)))

    def test_placeholders_and_example_blocks_are_ignored(self):
        body = body_with(
            "Put helpers in scripts/<name>.py or references/{topic}.md.\n\n"
            "<example>\nRun scripts/missing.py\n</example>"
        )
        skill = make_skill(self.tmp, body=body)
        self.assertNotIn("M5", self.ids(skill))

    def test_prose_slash_is_not_a_path(self):
        skill = make_skill(self.tmp, body=body_with("Detect package scripts/commands and folders."))
        self.assertNotIn("M5", self.ids(skill))

    def test_missing_sibling_skill_is_a_check(self):
        skill = make_skill(self.tmp, body=body_with("Run ../other-skill/scripts/tool.py first."))
        found = [f for f in self.findings(skill) if f.rule_id == "M5"]
        self.assertEqual([qv.CHECK], [f.confidence for f in found])

    def test_existing_sibling_skill_passes(self):
        skill = make_skill(self.tmp, body=body_with("Run ../other-skill/scripts/tool.py first."))
        write_file(self.tmp / "other-skill" / "scripts" / "tool.py", "print('ok')\n")
        self.assertNotIn("M5", self.ids(skill))

    def test_trailing_slash_needs_a_directory(self):
        skill = make_skill(self.tmp, body=body_with("Templates live in assets/templates/."))
        self.assertIn("M5", self.ids(skill))
        (skill / "assets" / "templates").mkdir(parents=True)
        self.assertNotIn("M5", self.ids(skill))


class Scripts(ValidatorCase):
    def test_swallowing_and_interactive_scripts_are_m6(self):
        skill = make_skill(self.tmp)
        write_file(skill / "scripts" / "bad.py", (
            "import json\n"
            "try:\n    json.loads('x')\nexcept:\n    print('failed')\n"
            "try:\n    json.loads('y')\nexcept Exception:\n    pass\n"
            "name = input('Name? ')\n"
        ))
        found = [f for f in self.findings(skill) if f.rule_id == "M6"]
        self.assertEqual(3, len(found))
        self.assertTrue(all(f.confidence == qv.DEFINITIVE and f.file == "scripts/bad.py" for f in found))
        self.assertEqual([4, 8, 10], sorted(f.line for f in found))

    def test_specific_exceptions_are_fine(self):
        skill = make_skill(self.tmp)
        write_file(skill / "scripts" / "good.py",
                   "try:\n    open('x')\nexcept OSError as exc:\n    raise SystemExit(f'cannot open: {exc}')\n")
        self.assertClean(skill)

    def test_syntax_error_is_a_check(self):
        skill = make_skill(self.tmp)
        write_file(skill / "scripts" / "old.py", "print 'python 2'\n")
        found = [f for f in self.findings(skill) if f.rule_id == "M6"]
        self.assertEqual([qv.CHECK], [f.confidence for f in found])

    def test_undeclared_third_party_import_is_m13_check(self):
        skill = make_skill(self.tmp)
        write_file(skill / "scripts" / "chart.py", "import matplotlib\n")
        found = [f for f in self.findings(skill) if f.rule_id == "m13"]
        self.assertEqual([qv.CHECK], [f.confidence for f in found])

    def test_declared_or_sibling_imports_pass(self):
        body = body_with("Requires pyyaml: `pip install pyyaml`.")
        skill = make_skill(self.tmp, body=body)
        write_file(skill / "scripts" / "load.py", "import yaml\nimport helper\n")
        write_file(skill / "scripts" / "helper.py", "VALUE = 1\n")
        self.assertNotIn("m13", self.ids(skill))


class ReferencesAndPaths(ValidatorCase):
    def test_long_reference_without_contents_is_m9(self):
        skill = make_skill(self.tmp)
        write_file(skill / "references" / "long.md", "# Long\n" + "line\n" * 120)
        self.assertEqual({"m9"}, self.ids(skill))

    def test_long_reference_with_contents_passes(self):
        skill = make_skill(self.tmp)
        write_file(skill / "references" / "long.md", "# Long\n\n## Contents\n\n- [A](#a)\n" + "line\n" * 120)
        self.assertClean(skill)

    def test_reference_chain_is_m10_check(self):
        skill = make_skill(self.tmp, body=body_with("Read references/first.md for the format."))
        write_file(skill / "references" / "first.md", "# First\n\nThe details are in [second](second.md).\n")
        write_file(skill / "references" / "second.md", "# Second\n")
        found = [f for f in self.findings(skill) if f.rule_id == "m10"]
        self.assertEqual(1, len(found))
        self.assertEqual((qv.CHECK, "references/first.md"), (found[0].confidence, found[0].file))

    def test_directly_linked_references_are_not_a_chain(self):
        body = body_with("Read references/first.md, then references/second.md.")
        skill = make_skill(self.tmp, body=body)
        write_file(skill / "references" / "first.md", "# First\n\nSee references/second.md.\n")
        write_file(skill / "references" / "second.md", "# Second\n")
        self.assertNotIn("m10", self.ids(skill))

    def test_drive_letter_path_is_m11(self):
        skill = make_skill(self.tmp, body=body_with("Install to C:\\tools\\csv."))
        self.assertEqual({"m11"}, self.ids(skill))

    def test_real_user_path_is_m11(self):
        skill = make_skill(self.tmp, body=body_with("Files live in /Users/jsmith/projects/."))
        self.assertEqual({"m11"}, self.ids(skill))

    def test_placeholder_user_path_passes(self):
        skill = make_skill(self.tmp, body=body_with("Files live in /Users/username/projects/ or ~/.claude/skills/."))
        self.assertClean(skill)

    def test_m11_applies_to_references_but_not_powershell_fences(self):
        skill = make_skill(self.tmp)
        write_file(skill / "references" / "win.md",
                   "# Windows\n\n```powershell\nGet-ChildItem C:\\Users\\jsmith\\skills\n```\n")
        self.assertClean(skill)
        write_file(skill / "references" / "win.md", "# Windows\n\nOpen /home/jsmith/skills/ first.\n")
        found = [f for f in self.findings(skill) if f.rule_id == "m11"]
        self.assertEqual(["references/win.md"], [f.file for f in found])


class LeftoversAndSubstitution(ValidatorCase):
    def test_todo_placeholder_is_m9(self):
        skill = make_skill(self.tmp, body=body_with("[TODO: describe the output]"))
        self.assertEqual({"M9"}, self.ids(skill))

    def test_init_placeholder_file_is_m9(self):
        skill = make_skill(self.tmp)
        write_file(skill / "scripts" / "example.py", "print('placeholder')\n")
        found = [f for f in self.findings(skill) if f.rule_id == "M9"]
        self.assertEqual(["scripts/example.py"], [f.file for f in found])

    def test_arguments_in_example_block_is_m12_check(self):
        body = CLEAN_BODY.replace('Request: "Summarise sales.csv"', 'Request: "/csv-report $ARGUMENTS"')
        found = [f for f in self.findings(make_skill(self.tmp, body=body)) if f.rule_id == "m12"]
        self.assertEqual([qv.CHECK], [f.confidence for f in found])

    def test_escaped_or_prose_arguments_pass(self):
        body = body_with("The skill reads $ARGUMENTS as the file path.\n\n```text\nCost: \\$1.00\n```")
        self.assertClean(make_skill(self.tmp, body=body))

    def test_injection_syntax_is_m9_check(self):
        body = body_with("Current branch: !" + "`git branch --show-current`")
        found = [f for f in self.findings(make_skill(self.tmp, body=body)) if f.rule_id == "M9"]
        self.assertEqual([qv.CHECK], [f.confidence for f in found])

    def test_exclamation_inside_a_word_is_not_injection(self):
        body = body_with("| `#DIV/0!` | Division by zero | Add a guard `=IF(B2=0,0,A2/B2)` |")
        self.assertClean(make_skill(self.tmp, body=body))


class WordingLeads(ValidatorCase):
    def test_weak_verbs_are_m7_check(self):
        body = body_with("Consider the size. Ensure it fits. Handle errors as needed.")
        found = [f for f in self.findings(make_skill(self.tmp, body=body)) if f.rule_id == "M7"]
        self.assertEqual([qv.CHECK], [f.confidence for f in found])

    def test_quoted_weak_verbs_do_not_count(self):
        body = body_with('Avoid "consider", "ensure", and "as needed" in your rules.')
        self.assertClean(make_skill(self.tmp, body=body))

    def test_emphasis_overuse_is_m15_check(self):
        body = body_with("You MUST read it. NEVER skip it. ALWAYS check it.")
        found = [f for f in self.findings(make_skill(self.tmp, body=body)) if f.rule_id == "m15"]
        self.assertEqual([qv.CHECK], [f.confidence for f in found])


class StyleRules(ValidatorCase):
    def test_no_evals_is_style_only_and_exit_zero(self):
        skill = make_skill(self.tmp, evals=False)
        self.assertEqual({"S5"}, self.ids(skill))
        self.assertTrue(all(f.severity == qv.STYLE for f in self.findings(skill)))
        result = run_script("quick_validate.py", str(skill))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_invalid_evals(self):
        skill = make_skill(self.tmp)
        write_file(skill / "evals" / "evals.json", '{"skill_name": "csv-report", "evals": [{"id": 1}]}')
        write_file(skill / "evals" / "trigger_queries.json", "not json")
        found = [f for f in self.findings(skill) if f.rule_id == "S5"]
        self.assertEqual(2, len(found))

    def test_missing_instructions_and_examples(self):
        skill = make_skill(self.tmp, body="# CSV Report\n\n1. Read the file.\n2. Summarise it.\n")
        self.assertEqual({"S1", "S2"}, self.ids(skill))

    def test_unexpected_root_entries(self):
        skill = make_skill(self.tmp)
        write_file(skill / "NOTES.md", "notes\n")
        write_file(skill / "LICENSE.txt", "MIT\n")
        write_file(skill / ".gitignore", "*.pyc\n")
        found = [f for f in self.findings(skill) if f.rule_id == "S4"]
        self.assertEqual(["NOTES.md"], [f.file for f in found])

    def test_mixed_separators(self):
        skill = make_skill(self.tmp)
        write_file(skill / "references" / "first-topic.md", "# A\n")
        write_file(skill / "references" / "second_topic.md", "# B\n")
        self.assertEqual({"S7"}, self.ids(skill))

    def test_long_skill_md(self):
        body = CLEAN_BODY + "\n".join(f"Line {n}." for n in range(450)) + "\n"
        self.assertEqual({"S3"}, self.ids(make_skill(self.tmp, body=body)))
        body = CLEAN_BODY + "\n".join(f"Line {n}." for n in range(520)) + "\n"
        self.assertEqual({"M1", "S3"}, self.ids(make_skill(self.tmp, folder="longer", body=body,
                                                          frontmatter=f"name: longer\ndescription: {CLEAN_DESCRIPTION}\n")))


class CommandLineContract(ValidatorCase):
    def test_output_format_order_and_exit_codes(self):
        clean = make_skill(self.tmp)
        result = run_script("quick_validate.py", str(clean))
        self.assertEqual(0, result.returncode)
        self.assertEqual(["RESULT major=0 minor=0 style=0 checks=0"], result.stdout.splitlines())

        fm = f"name: {CLEAN_NAME}\ndescription: {CLEAN_DESCRIPTION}\ncolour: blue\n"
        minor_only = make_skill(self.tmp, folder="minor-only", name="minor-only",
                                frontmatter=fm.replace(CLEAN_NAME, "minor-only"))
        result = run_script("quick_validate.py", str(minor_only))
        self.assertEqual(4, result.returncode, result.stdout)

        body = body_with("[TODO: fill]\n\nConsider it. Ensure it. Do it as needed.")
        fm = f"name: wrong-name\ndescription: {CLEAN_DESCRIPTION}\ncolour: blue\n"
        mixed = make_skill(self.tmp, folder="mixed", frontmatter=fm, body=body, evals=False)
        result = run_script("quick_validate.py", str(mixed))
        self.assertEqual(1, result.returncode)
        lines = result.stdout.splitlines()
        self.assertRegex(lines[-1], RESULT_LINE)
        parsed = [FINDING_LINE.match(line) for line in lines[:-1]]
        self.assertTrue(all(parsed), lines)
        order = [({"major": 0, "minor": 1, "style": 2}[m.group(2)], m.group(3) != "definitive") for m in parsed]
        self.assertEqual(sorted(order), order, "majors, minors, then style; definitive before check")
        definitive = [m for m in parsed if m.group(3) == "definitive"]
        expected = "RESULT major={} minor={} style={} checks={}".format(
            sum(m.group(2) == "major" for m in definitive),
            sum(m.group(2) == "minor" for m in definitive),
            sum(m.group(2) == "style" for m in definitive),
            sum(m.group(3) == "check" for m in parsed),
        )
        self.assertEqual(expected, lines[-1])

    def test_finding_format(self):
        finding = qv.Finding("M5", "major", "definitive", "SKILL.md", 12, "references scripts/x.py")
        self.assertEqual("[M5] major definitive SKILL.md:12 references scripts/x.py", finding.format())

    def test_usage_error_exits_2(self):
        result = run_script("quick_validate.py", str(self.tmp / "does-not-exist"))
        self.assertEqual(2, result.returncode)

    def test_missing_pyyaml_exits_3(self):
        skill = make_skill(self.tmp)
        code = (
            "import runpy, sys\n"
            "sys.modules['yaml'] = None\n"
            f"sys.argv = ['quick_validate.py', {str(skill)!r}]\n"
            f"runpy.run_path({str(_helpers.SCRIPTS / 'quick_validate.py')!r}, run_name='__main__')\n"
        )
        import subprocess
        import sys
        result = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True,
                                timeout=_helpers.SUBPROCESS_TIMEOUT_SECONDS)
        self.assertEqual(3, result.returncode, result.stderr)
        self.assertIn("python -m pip install pyyaml", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_non_utf8_skill_md_exits_3(self):
        skill = self.tmp / CLEAN_NAME
        skill.mkdir()
        (skill / "SKILL.md").write_bytes(b"---\nname: csv-report\ndescription: caf\xe9\n---\nbody\n")
        result = run_script("quick_validate.py", str(skill))
        self.assertEqual(3, result.returncode)
        self.assertIn("UTF-8", result.stderr)

    def test_validate_skill_shim(self):
        valid, message, warnings = qv.validate_skill(make_skill(self.tmp, evals=False))
        self.assertTrue(valid, message)
        self.assertEqual(2, len(warnings))
        fm = f"name: wrong-name\ndescription: {CLEAN_DESCRIPTION}\n"
        valid, message, _ = qv.validate_skill(make_skill(self.tmp, folder="broken", frontmatter=fm))
        self.assertFalse(valid)
        self.assertIn("[M9]", message)

    def test_checks_are_read_only(self):
        skill = make_skill(self.tmp)
        write_file(skill / "scripts" / "run.py", "print('ok')\n")
        before = sorted(p.relative_to(skill).as_posix() for p in skill.rglob("*"))
        qv.collect_findings(skill)
        qv.collect_findings(skill, portable=True)
        after = sorted(p.relative_to(skill).as_posix() for p in skill.rglob("*"))
        self.assertEqual(before, after)


# --- Regression tests for the verified review findings ----------------------
# Each class names the finding IDs it covers (validator-correctness QV-n,
# docs-vs-contract Fn, other-scripts F10, e2e:n).


class ForkNegation(ValidatorCase):
    """QV-1, QV-5: M2 negation follows rules.md clauses; more ask and wait phrasings count."""

    def m2(self, text: str, folder: str = CLEAN_NAME) -> list[qv.Finding]:
        fm = FORK.replace(CLEAN_NAME, folder)
        skill = make_skill(self.tmp, name=folder, frontmatter=fm, body=body_with(text))
        return [f for f in self.findings(skill) if f.rule_id == "M2" and f.confidence == qv.DEFINITIVE]

    def test_negated_mentions_are_not_m2(self):
        negated = (
            "If the path is missing, do not\nask the user for it; print usage and stop.",  # soft wrap
            "`AskUserQuestion` is not available in this subagent, so print usage and stop.",
            "Instead of asking the user, use the defaults below.",
            "Under no circumstances ask the user anything.",
            "Proceed without waiting for the user's approval.",
            "If you cannot ask the user, print usage and stop.",
        )
        for index, text in enumerate(negated):
            self.assertEqual([], self.m2(text, folder=f"neg-{index}"), text)

    def test_more_ask_and_wait_phrasings_are_m2(self):
        asks = (
            "Wait for the user to reply before continuing.",
            "Ask for confirmation before overwriting the output.",
            "Present the plan and stop until the user approves it.",
            "If the format is not given ask the user which one to use.",  # negation inside the condition
            "Do not proceed until the user approves.",  # the negation governs another verb
            "Ask which format to use.",
            "Wait for your response before writing the file.",
            "Wait for user input, then continue.",
        )
        for index, text in enumerate(asks):
            self.assertTrue(self.m2(text, folder=f"ask-{index}"), text)

    def test_descriptive_prose_is_not_an_ask(self):
        # Generic "ask for" / "ask which" / "get approval" count only as an instruction.
        prose = (
            "Users often ask for CSV summaries in Markdown.",
            "Reviewers usually ask which delimiter a file uses.",
            "If the request gets approval from the build, the job continues.",
        )
        for index, text in enumerate(prose):
            self.assertEqual([], self.m2(text, folder=f"prose-{index}"), text)
        for index, text in enumerate(("1. Ask for the file name.", "Then ask which sheet to use.",
                                      "- **Get approval** before deleting files.")):
            self.assertTrue(self.m2(text, folder=f"imperative-{index}"), text)

    def test_defaults_are_not_waits(self):
        for index, text in enumerate(("Use `medium` effort unless the user selects otherwise.",
                                      "Present the combined results. Let the user pick.")):
            self.assertEqual([], self.m2(text, folder=f"default-{index}"), text)

    def test_inline_triple_backticks_do_not_open_a_fence(self):
        # QV-12: "```csv```" is inline code, so later lines are still prose.
        text = "```csv``` is the only accepted input format.\n\nAsk the user which file to read."
        self.assertTrue(self.m2(text))
        skill = make_skill(self.tmp, folder="inline-ticks",
                           frontmatter=f"name: inline-ticks\ndescription: {CLEAN_DESCRIPTION}\n",
                           body=body_with("```csv``` is the only accepted input format."))
        self.assertEqual(set(), self.ids(skill))

    def test_non_string_agent_does_not_crash(self):
        # QV-3: agent as a YAML list or mapping must not raise TypeError.
        for index, agent in enumerate(("[Explore]", "{a: b}")):
            folder = f"agent-{index}"
            fm = f"name: {folder}\ndescription: {CLEAN_DESCRIPTION}\ncontext: fork\nagent: {agent}\n"
            skill = make_skill(self.tmp, name=folder, frontmatter=fm)
            self.assertNotIn("M2", self.ids(skill, confidence=qv.DEFINITIVE))
            self.assertEqual(0, run_script("quick_validate.py", str(skill)).returncode)


class ForkPausesMissedBefore(ValidatorCase):
    """M2 pauses that claude-md (now claudia-md, at 6f40f09) and pptx's intake reference slipped past."""

    INTAKE = (
        "# Intake Questionnaire\n\n"
        "> **Purpose**: If the user doesn't provide information after 2 prompts, use the safe default.\n\n"
        "## Usage\n\n"
        "1. **First pass**: Ask all 10 questions in a user-friendly format.\n"
        "2. **Apply defaults**: use the safe default for each missing item.\n"
    )

    def fork_skill(self, body: str, folder: str = CLEAN_NAME, fork: bool = True,
                   references: dict[str, str] | None = None) -> Path:
        fm = f"name: {folder}\ndescription: {CLEAN_DESCRIPTION}\n" + ("context: fork\n" if fork else "")
        skill = make_skill(self.tmp, name=folder, frontmatter=fm, body=body)
        for rel, text in (references or {}).items():
            write_file(skill / rel, text)
        return skill

    def m2(self, skill: Path, confidence: str = qv.DEFINITIVE) -> list[qv.Finding]:
        return [f for f in self.findings(skill) if f.rule_id == "M2" and f.confidence == confidence]

    def test_claude_md_phrasings_are_definitive_m2(self):
        pauses = (
            "After outputting the quality report, ask user for confirmation before updating.",
            "After user approval, apply changes using the Edit tool.",
            "| Phase | Action | Detail |\n|---|---|---|\n| U5 | User Approval | Present changes for approval. |",
            "Scan directories, then get user approval before creating any files.",
            "After the user's approval, write the files.",
            "Once user approves the plan, write the files.",
            "Do not proceed until you get user approval.",  # the negation governs "proceed"
            "Never create files without user approval.",  # two negations cancel
            "1. **First pass**: Ask all 10 questions in a friendly format.",
            "If the path is missing, ask for it.",
        )
        for index, text in enumerate(pauses):
            self.assertTrue(self.m2(self.fork_skill(body_with(text), folder=f"pause-{index}")), text)

    def test_choice_prompt_counts_inside_a_code_block(self):
        for index, prompt in enumerate(("Apply these changes? [All / Select / Cancel]", "Continue? (y/n)")):
            body = body_with(f"Print the preview:\n\n```markdown\n## Update Preview\n\n{prompt}\n```")
            found = self.m2(self.fork_skill(body, folder=f"choice-{index}"))
            self.assertEqual(1, len(found), prompt)
            self.assertIn(prompt, found[0].message)

    def test_negated_pauses_stay_ignored(self):
        negated = (
            "Do not wait for confirmation.",
            "Proceed without user approval.",
            "Proceed without first getting user approval.",
            "Never ask user for input; print usage and stop.",
            "User approval is not required, so write the files directly.",
            "Ordinary subagents lose `AskUserQuestion` and the Workflow tool.",
            "Never print a prompt such as 'Continue? (y/n)'; the fork cannot read the answer.",
        )
        for index, text in enumerate(negated):
            self.assertEqual([], self.m2(self.fork_skill(body_with(text), folder=f"neg-{index}")), text)

    def test_lookalikes_are_not_pauses(self):
        prose = (
            "Add a user confirmation dialog before destructive actions in the app.",
            "Rate each section: [Excellent/Good/Fair/Poor]",
            "Questions? [docs/faq](https://example.com/faq)",
            "Ask yourself these questions before writing.",
            "Mark the change as a fix if user-visible.",
            "Reviewers often ask clarifying questions.",
        )
        for index, text in enumerate(prose):
            self.assertEqual([], self.m2(self.fork_skill(body_with(text), folder=f"prose-{index}")), text)

    def test_reference_sent_to_as_a_step_is_definitive(self):
        rel = "references/content-workflow/INTAKE.md"
        body = body_with(f"1. **Intake**: Use questionnaire at `{rel}`")
        found = self.m2(self.fork_skill(body, references={rel: self.INTAKE}))
        self.assertEqual([(rel, 7)], [(f.file, f.line) for f in found])
        self.assertIn("sends Claude to as a step", found[0].message)
        self.assertIn("Ask all 10 questions", found[0].message)

    def test_reference_read_first_is_definitive(self):
        rel = "references/setup.md"
        body = body_with(f"Read `{rel}` before writing any code.")
        found = self.m2(self.fork_skill(body, references={rel: "# Setup\n\nAsk the user which database to use.\n"}))
        self.assertEqual([(rel, 3)], [(f.file, f.line) for f in found])

    def test_other_linked_reference_is_a_check(self):
        rel = "references/faq.md"
        faq = "# FAQ\n\nAsk the user which format to use.\n\nIf the user confirms, overwrite the file.\n"
        for index, line in enumerate((f"See `{rel}` for edge cases.", f"1. `{rel}`: edge cases")):
            skill = self.fork_skill(body_with(line), folder=f"linked-{index}", references={rel: faq})
            self.assertEqual([], self.m2(skill), line)
            checks = [f for f in self.m2(skill, qv.CHECK) if f.file == rel]
            self.assertEqual([3], [f.line for f in checks], line)
            self.assertIn("also lines 5", checks[0].message)

    def test_reference_pauses_need_fork_and_respect_negation(self):
        rel = "references/content-workflow/INTAKE.md"
        body = body_with(f"1. **Intake**: Use questionnaire at `{rel}`")
        inline = self.fork_skill(body, folder="inline", fork=False, references={rel: self.INTAKE})
        self.assertNotIn("M2", self.ids(inline))
        quiet = "# Intake\n\nDo not ask the user anything; use the safe defaults below.\n"
        skill = self.fork_skill(body, folder="quiet", references={rel: quiet})
        self.assertEqual([], [f for f in self.findings(skill) if f.rule_id == "M2" and f.file == rel])

    def test_reference_finding_prints_on_one_contract_line(self):
        rel = "references/content-workflow/INTAKE.md"
        skill = self.fork_skill(body_with(f"1. **Intake**: Use questionnaire at `{rel}`"),
                                references={rel: self.INTAKE})
        result = run_script("quick_validate.py", str(skill))
        self.assertEqual(1, result.returncode)
        lines = [line for line in result.stdout.splitlines() if line.startswith("[M2] major definitive")]
        self.assertEqual(1, len(lines))
        self.assertRegex(lines[0], FINDING_LINE)
        self.assertIn(f" {rel}:7 ", lines[0])


class OneLineMessages(ValidatorCase):
    """QV-9: a finding never spans two output lines."""

    def test_wrapped_matches_print_on_one_line(self):
        fm = (f"name: {CLEAN_NAME}\ndescription: |\n  Converts CSV files. With it you\n  can summarise them.\n"
              "  Use when the user asks.\ncontext: fork\n")
        skill = make_skill(self.tmp, frontmatter=fm, body=body_with("Then ask the\nuser which file to read."))
        found = self.findings(skill)
        self.assertTrue({"M2", "M8"} <= {f.rule_id for f in found})
        result = run_script("quick_validate.py", str(skill))
        lines = result.stdout.splitlines()
        self.assertRegex(lines[-1], RESULT_LINE)
        for line in lines[:-1]:
            self.assertRegex(line, FINDING_LINE)
        self.assertTrue(all("\n" not in f.format() for f in found))


class BundledPathTokens(ValidatorCase):
    """QV-2, QV-7, QV-8, QV-18, F15: M5 path tokens follow the rules.md M5 definition."""

    def m5(self, skill: Path) -> list[qv.Finding]:
        return [f for f in self.findings(skill) if f.rule_id == "M5"]

    def test_suffixes_and_curly_punctuation_are_not_part_of_the_path(self):
        body = body_with(
            "Run \u201cscripts/check.py\u201d first, or \u2018scripts/check.py\u2019.\n\n"
            "Then scripts/check.py\u2014it prints a table.\n\n"
            "See `scripts/check.py:10-20` and `scripts/cli.py:main`."
        )
        skill = make_skill(self.tmp, body=body)
        write_file(skill / "scripts" / "check.py", "print('ok')\n")
        write_file(skill / "scripts" / "cli.py", "def main():\n    return 0\n")
        self.assertEqual([], self.m5(skill))

    def test_dot_slash_link_and_bold_paths_are_checked(self):
        body = body_with(
            "Run `python ./scripts/missing.py` and read [the guide](./references/missing.md).\n\n"
            "Run **scripts/other.py** first, then _scripts/third.py_."
        )
        messages = " ".join(f.message for f in self.m5(make_skill(self.tmp, body=body)))
        for token in ("scripts/missing.py", "references/missing.md", "scripts/other.py", "scripts/third.py"):
            self.assertIn(f"{token},", messages)

    def test_word_inside_another_path_is_not_a_boundary(self):
        body = body_with("Helpers live in my_scripts/tool.py and docs/references/x.md of other repos.")
        self.assertEqual([], self.m5(make_skill(self.tmp, body=body)))

    def test_bare_directory_mention_needs_the_directory(self):
        skill = make_skill(self.tmp, body=body_with("Read the guides in `references/`."))
        found = self.m5(skill)
        self.assertEqual([qv.DEFINITIVE], [f.confidence for f in found])
        self.assertIn("directory references/", found[0].message)
        (skill / "references").mkdir()
        self.assertEqual([], self.m5(skill))

    def test_letter_case_mismatch_is_m5(self):
        body = body_with("Read `references/Guide.md`, then fill `assets/Templates/`.")
        skill = make_skill(self.tmp, body=body)
        write_file(skill / "references" / "guide.md", "# Guide\n")
        (skill / "assets" / "templates").mkdir(parents=True)
        found = self.m5(skill)
        self.assertEqual(2, len(found))
        self.assertTrue(all(f.confidence == qv.DEFINITIVE and "letter case" in f.message for f in found))
        self.assertIn("references/guide.md", found[0].message + found[1].message)

    def test_paths_inside_example_blocks_are_skipped(self):
        body = CLEAN_BODY.replace("Result: the error names", "Run scripts/convert.py.\nResult: the error names")
        self.assertEqual([], self.m5(make_skill(self.tmp, body=body)))


class LinkedFolders(ValidatorCase):
    """QV-4, QV-16: symlinks and junctions do not crash the validator or rename the skill."""

    def test_references_linked_outside_the_skill(self):
        shared = self.tmp / "shared-refs"
        write_file(shared / "a.md", "# A\n\nDetails in [b](b.md).\n")
        write_file(shared / "b.md", "# B\n")
        skill = make_skill(self.tmp, body=body_with("Read `references/a.md` first."))
        if not make_dir_link(skill / "references", shared):
            self.skipTest("cannot create a symlink or junction here")
        found = [f for f in self.findings(skill) if f.rule_id == "m10"]
        self.assertEqual(["references/a.md"], [f.file for f in found])
        self.assertIn("references/b.md", found[0].message)

    def test_installed_link_name_is_the_folder_name(self):
        real = make_skill(self.tmp, folder="real-name")  # name: csv-report, so the real folder mismatches
        link = self.tmp / "installed" / CLEAN_NAME
        if not make_dir_link(link, real):
            self.skipTest("cannot create a symlink or junction here")
        self.assertNotIn("M9", self.ids(link))
        self.assertIn("M9", self.ids(real))
        valid, message, _ = qv.validate_skill(link.resolve())  # package_skill validates the resolved path
        self.assertFalse(valid)
        self.assertIn("real-name", message)


class PythonInput(ValidatorCase):
    """QV-6, QV-13, F11, QV-14: interactive input and unparseable scripts."""

    def m6(self, source: str, filename: str = "run.py", folder: str = CLEAN_NAME) -> list[qv.Finding]:
        skill = make_skill(self.tmp, name=folder, frontmatter=f"name: {folder}\ndescription: {CLEAN_DESCRIPTION}\n")
        write_file(skill / "scripts" / filename, source)
        return [f for f in self.findings(skill) if f.rule_id == "M6"]

    def test_local_variable_named_input_does_not_hide_a_real_call(self):
        found = self.m6(
            "def load(path):\n    with open(path) as input:\n        return input.read()\n\n"
            "def main():\n    answer = input('Overwrite? [y/N] ')\n    return answer\n"
        )
        self.assertEqual([(qv.DEFINITIVE, 6)], [(f.confidence, f.line) for f in found])

    def test_bindings_in_scope_shadow_input(self):
        sources = (
            "from prompts import input\n\ndef main():\n    return input('x')\n",  # module level
            "def main(input):\n    return input('x')\n",  # parameter of the enclosing function
            "def outer():\n    input = print\n    def inner():\n        return input('x')\n    return inner\n",
        )
        for index, source in enumerate(sources):
            self.assertEqual([], self.m6(source, folder=f"shadow-{index}"), source)

    def test_global_rebinding_shadows_input(self):
        source = (
            "def setup():\n    global input\n    input = lambda prompt: 'y'\n\n"
            "def main():\n    return input('Overwrite? ')\n"
        )
        self.assertEqual([], self.m6(source, folder="global-input"))

    def test_getpass_is_definitive_m6(self):
        found = self.m6(
            "import getpass\nfrom getpass import getpass as ask\n"
            "token = getpass.getpass('API token: ')\nother = ask()\nuser = getpass.getuser()\n"
        )
        self.assertEqual([(qv.DEFINITIVE, 3), (qv.DEFINITIVE, 4)], sorted((f.confidence, f.line) for f in found))

    def test_stdin_reads_are_m6_checks(self):
        found = self.m6(
            "import json\nimport sys\nline = sys.stdin.readline()\nfor row in sys.stdin:\n    print(row)\n"
            "data = json.load(sys.stdin)\n"
        )
        self.assertEqual([qv.CHECK], [f.confidence for f in found])
        self.assertEqual(3, found[0].line)
        self.assertIn("also lines 4, 6", found[0].message)

    def test_isatty_guard_skips_the_stdin_lead(self):
        found = self.m6("import sys\nif not sys.stdin.isatty():\n    text = sys.stdin.read()\n")
        self.assertEqual([], found)

    def test_shell_read_is_m6_check(self):
        found = self.m6("#!/bin/sh\nread -p 'Name? ' name\necho \"$name\"\n", filename="ask.sh")
        self.assertEqual([(qv.CHECK, 2)], [(f.confidence, f.line) for f in found])

    def test_deeply_nested_script_is_a_check(self):
        found = self.m6("x = " + " + ".join(["'a'"] * 3000) + "\n")
        self.assertEqual([qv.CHECK], [f.confidence for f in found])
        self.assertIn("too deeply nested", found[0].message)


class DeepInputs(ValidatorCase):
    """QV-14: nesting that exhausts the parsers is reported, never a crash."""

    def test_deep_frontmatter_is_f(self):
        fm = f"name: {CLEAN_NAME}\ndescription: {CLEAN_DESCRIPTION}\nmetadata: " + "[" * 3000 + "]" * 3000 + "\n"
        found = self.findings(make_skill(self.tmp, frontmatter=fm))
        self.assertEqual(["F"], [f.rule_id for f in found])
        self.assertIn("nested too deeply", found[0].message)

    def test_deep_evals_json_is_s5(self):
        skill = make_skill(self.tmp)
        write_file(skill / "evals" / "evals.json", "[" * 100000 + "]" * 100000)
        found = [f for f in self.findings(skill) if f.rule_id == "S5"]
        self.assertEqual(1, len(found))
        self.assertIn("nested too deeply", found[0].message)


class LongLines(ValidatorCase):
    """QV-15: long runs without a match cost linear time, not quadratic."""

    def test_long_lines_stay_fast(self):
        body = body_with("Read references/long.md first.\n\n" + "](a" * 50000)
        skill = make_skill(self.tmp, body=body)
        write_file(skill / "references" / "long.md",
                   "# Long\n\n" + "a-" * 100000 + "\n\n" + "](a" * 50000 + "\n\n```!" + " " * 100000 + "\n")
        started = time.perf_counter()
        self.findings(skill)
        self.assertLess(time.perf_counter() - started, 10, "the old patterns took over a minute here")


class CountsAndNames(ValidatorCase):
    """QV-17 and F20 (S3 counts LF characters), F10 (names end at the string end), F19 (background)."""

    def test_crlf_does_not_change_the_character_count(self):
        filler = "\n".join("Row %03d: " % n + "x" * 60 for n in range(250)) + "\n"  # about 17,700 characters
        body = CLEAN_BODY + filler + "y" * (19900 - len(filler) - len(CLEAN_BODY) - 120) + "\n"
        for index, newline in enumerate(("\n", "\r\n")):
            folder = f"chars-{index}"
            fm = f"name: {folder}\ndescription: {CLEAN_DESCRIPTION}\n"
            skill = make_skill(self.tmp, name=folder, frontmatter=fm, body=body, newline=newline)
            data = skill.joinpath("SKILL.md").read_bytes()
            self.assertLess(len(data.replace(b"\r\n", b"\n")), 20000)
            if newline == "\r\n":
                self.assertGreater(len(data), 20000, "the CRLF copy must exceed the limit to test anything")
            self.assertNotIn("S3", self.ids(skill), newline.encode())

    def test_name_with_trailing_newline_is_rejected(self):
        self.assertEqual([], qv.name_errors("demo"))
        self.assertTrue(qv.name_errors("demo\n"))
        self.assertTrue(qv.name_errors("demo\r\n"))

    def test_background_without_fork_is_m12(self):
        fm = f"name: {CLEAN_NAME}\ndescription: {CLEAN_DESCRIPTION}\nbackground: false\n"
        found = [f for f in self.findings(make_skill(self.tmp, frontmatter=fm)) if f.rule_id == "m12"]
        self.assertEqual(1, len(found))
        self.assertIn("background is set without context: fork", found[0].message)
        fm = FORK + "background: false\n"
        self.assertNotIn("m12", self.ids(make_skill(self.tmp, folder="forked", name="forked",
                                                    frontmatter=fm.replace(CLEAN_NAME, "forked"))))


class DescriptionLists(ValidatorCase):
    """QV-10, F4: the M8 trigger and person lists are exactly the ones in rules.md."""

    def m8(self, description: str, folder: str) -> list[qv.Finding]:
        fm = f"name: {folder}\ndescription: {description}\n"
        skill = make_skill(self.tmp, name=folder, frontmatter=fm)
        return [f for f in self.findings(skill) if f.rule_id == "M8"]

    def test_listed_trigger_forms(self):
        forms = (
            "Converts CSV files. Use whenever a CSV file needs a summary.",
            "Converts CSV files. Use it when a CSV file needs a summary.",
            "Converts CSV files. Use for CSV summaries.",
            "Converts CSV files. Use if a CSV file needs a summary.",
            "Converts CSV files. Triggers on CSV uploads.",
            "Converts CSV files. Invoke when a CSV file arrives.",
            "Converts CSV files. Activates when a CSV file is opened.",
            "Converts CSV files when users upload one.",
            "Converts CSV files when the users upload one.",
        )
        for index, description in enumerate(forms):
            self.assertEqual([], self.m8(description, f"trigger-{index}"), description)

    def test_unlisted_trigger_forms_are_m8(self):
        for index, description in enumerate(("Converts CSV files. Triggered by CSV uploads.",
                                             "Converts CSV files. Use it for CSV summaries.")):
            self.assertTrue(self.m8(description, f"unlisted-{index}"), description)

    def test_first_and_second_person_words(self):
        for index, words in enumerate(("Use when you want a summary.", "Use when you have a CSV file.",
                                       "Use when you're stuck.", "Use when your CSV breaks.",
                                       "We summarise them. Use when the user asks.",
                                       "Our tool summarises them. Use when the user asks.",
                                       "I'm a summariser. Use when the user asks.",
                                       "Let me summarise them. Use when the user asks.")):
            description = "Converts CSV files. " + words
            self.assertTrue(self.m8(description, f"person-{index}"), description)

    def test_person_exemptions(self):
        for index, description in enumerate((
            "Converts I/O logs into reports. Use when the user asks.",
            "Converts Type I error tables into reports. Use when the user asks.",
            "Converts CSV files. Use when the user says 'summarise this for you'.",
            'Converts CSV files. Use when the user says "can you summarise my file".',
        )):
            self.assertEqual([], self.m8(description, f"exempt-{index}"), description)


class WordingAndLayout(ValidatorCase):
    """F12 (handle ... appropriately), F15 (S1 needs a real block), QV-11 (indented fences)."""

    def test_handle_with_words_between_counts_as_weak(self):
        body = body_with("Handle errors appropriately.\nEnsure the file exists.\nRetry as needed.")
        found = [f for f in self.findings(make_skill(self.tmp, body=body)) if f.rule_id == "M7"]
        self.assertEqual(1, len(found))
        self.assertTrue(found[0].message.startswith("3 weak-verb uses"))

    def test_instructions_tag_in_inline_code_is_not_a_block(self):
        body = CLEAN_BODY.replace("<instructions>\n", "").replace("</instructions>\n", "")
        body = body.replace("# CSV Report\n", "# CSV Report\n\nWrap workflows in `<instructions>` tags.\n")
        self.assertEqual({"S1"}, self.ids(make_skill(self.tmp, body=body)))

    def test_indented_powershell_fence_keeps_its_exemption(self):
        skill = make_skill(self.tmp)
        write_file(skill / "references" / "windows.md",
                   "# Windows\n\n- Install\n  - Run this in PowerShell:\n\n"
                   "    ```powershell\n    Set-Location C:\\Tools\\csv\n    ```\n")
        self.assertClean(skill)


class EnvironmentAndErrors(ValidatorCase):
    """e2e:2 (Python before 3.10), e2e:5 (read errors name the cause), internal errors exit 3."""

    def test_import_check_needs_python_310(self):
        skill = make_skill(self.tmp)
        write_file(skill / "scripts" / "chart.py", "import matplotlib\n")
        with mock.patch.object(sys, "stdlib_module_names", None, create=True):
            found = [f for f in self.findings(skill) if f.rule_id == "m13"]
        self.assertEqual([qv.CHECK], [f.confidence for f in found])
        self.assertIn("Python 3.10", found[0].message)

    def test_unreadable_evals_file_names_the_os_error(self):
        skill = make_skill(self.tmp)
        (skill / "evals" / "evals.json").unlink()
        (skill / "evals" / "evals.json").mkdir()  # reading a directory fails with an OS error
        found = [f for f in self.findings(skill) if f.file == "evals/evals.json"]
        self.assertEqual(1, len(found))
        self.assertIn("could not be read", found[0].message)
        self.assertNotIn("JSON", found[0].message)

    def test_invalid_json_names_line_and_column(self):
        skill = make_skill(self.tmp)
        write_file(skill / "evals" / "trigger_queries.json", '[\n  {"query": "x",}\n]')
        found = [f for f in self.findings(skill) if f.file == "evals/trigger_queries.json"]
        self.assertRegex(found[0].message, r"not valid JSON \(line 2 column \d+")

    def test_internal_error_exits_3_with_one_line(self):
        skill = make_skill(self.tmp)
        stderr = io.StringIO()
        with mock.patch.object(qv, "collect_findings", side_effect=RuntimeError("boom\nsecond line")), \
                contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
            code = qv.main([str(skill)])
        self.assertEqual(3, code)
        self.assertEqual("[env] internal error: RuntimeError: boom second line\n", stderr.getvalue())
        with mock.patch.object(qv, "collect_findings", side_effect=RuntimeError("boom")):
            valid, message, _ = qv.validate_skill(skill)
        self.assertFalse(valid)
        self.assertIn("internal error", message)


if __name__ == "__main__":
    unittest.main()
