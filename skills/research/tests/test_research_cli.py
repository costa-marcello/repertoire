"""Tests for research.py output: the web coverage block, the --days lookback
window, and a real web-only run (no API keys, so no network calls)."""

import os
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lib import dates, render, schema


def _report(mode, reddit_error=None, x_error=None):
    report = schema.Report(
        topic="test topic",
        range_from="2026-01-01",
        range_to="2026-03-01",
        generated_at="2026-03-01T12:00:00Z",
        mode=mode,
    )
    report.reddit_error = reddit_error
    report.x_error = x_error
    return report


class TestCoveredSites(unittest.TestCase):
    def test_web_only_covers_nothing(self):
        self.assertEqual(render.covered_sites(_report("web-only")), [])

    def test_both_covers_reddit_and_x(self):
        self.assertEqual(render.covered_sites(_report("both")), ["reddit.com", "x.com", "twitter.com"])

    def test_errored_source_is_not_covered(self):
        sites = render.covered_sites(_report("both", reddit_error="API error: HTTP 401"))
        self.assertEqual(sites, ["x.com", "twitter.com"])

    def test_compact_output_names_covered_sites(self):
        self.assertIn("**Script covered:** reddit.com", render.render_compact(_report("reddit-only")))
        self.assertIn("**Script covered:** none", render.render_compact(_report("web-only")))


class TestWebSearchBlock(unittest.TestCase):
    def test_web_only_block_hands_web_coverage_to_subagents(self):
        block = render.web_search_block(_report("web-only"), "test topic", "2026-01-01", "2026-03-01")
        self.assertIn(render.WEB_SEARCH_MARKER, block)
        self.assertIn("Script covered: none", block)
        self.assertIn("subagents", block)
        self.assertIn("Parallel Search", block)
        self.assertIn("Keenable", block)
        self.assertIn("WebSearch and WebFetch", block)
        self.assertNotIn("Use your WebSearch tool", block)

    def test_include_web_block_lists_covered_sites(self):
        block = render.web_search_block(_report("all"), "t", "2026-01-01", "2026-03-01")
        self.assertIn("Script covered: reddit.com, x.com, twitter.com", block)


def _run_script(*argv):
    """Run research.py as a child process with no API keys and a temp home folder.

    Returns the finished process; stdout and stderr are bytes.
    """
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as cwd:
        child_env = dict(os.environ)
        for key in ("OPENAI_API_KEY", "XAI_API_KEY", "PYTHONIOENCODING", "PYTHONUTF8"):
            child_env.pop(key, None)
        child_env["HOME"] = home
        child_env["USERPROFILE"] = home
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "research.py"), *argv],
            cwd=cwd,
            env=child_env,
            capture_output=True,
            timeout=60,
        )


class TestLookbackWindow(unittest.TestCase):
    """The search period comes only from --days; there is no default."""

    def test_date_range_spans_exactly_the_days_given(self):
        from_date, to_date = dates.get_date_range(30)
        span = datetime.strptime(to_date, "%Y-%m-%d") - datetime.strptime(from_date, "%Y-%m-%d")
        self.assertEqual(span.days, 30)

    def test_date_range_rejects_less_than_one_day(self):
        with self.assertRaises(ValueError):
            dates.get_date_range(0)

    def test_run_without_days_exits_2_and_names_the_option(self):
        result = _run_script("test topic", "--emit=compact")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--days", result.stderr.decode("utf-8", "replace"))

    def test_run_with_days_0_exits_2(self):
        result = _run_script("test topic", "--days", "0", "--emit=compact")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--days must be 1 or more", result.stderr.decode("utf-8", "replace"))

    def test_compact_output_shows_the_range_for_the_days_given(self):
        before = dates.get_date_range(90)
        result = _run_script("test topic", "--days", "90", "--emit=compact")
        after = dates.get_date_range(90)
        stdout = result.stdout.decode("utf-8")
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        # Either side of midnight UTC is a valid answer if the run straddled it.
        self.assertTrue(
            any(f"**Date Range:** {frm} to {to}" in stdout for frm, to in (before, after)),
            stdout,
        )


class TestWebOnlyRun(unittest.TestCase):
    def test_runs_from_any_folder_with_utf8_output(self):
        result = _run_script("café ✓ topic", "--days", "60", "--emit=compact")
        stdout = result.stdout.decode("utf-8")
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        self.assertIn("**Mode:** web-only", stdout)
        self.assertIn("**Script covered:** none", stdout)
        self.assertIn(render.WEB_SEARCH_MARKER, stdout)
        self.assertIn("café ✓ topic", stdout)


class TestEnrichDeadline(unittest.TestCase):
    """Reddit enrichment stops at the deadline, so the run fits the skill's
    Bash timeout; the threads not yet enriched are still returned."""

    def setUp(self):
        import research  # imported here: it is a script with import-time setup
        self.research = research

    def _run(self, deadline):
        return self.research.run_research(
            "test topic", "reddit", {}, {"openai": "m", "xai": "m"},
            "2026-01-01", "2026-03-01", mock=True, deadline=deadline,
        )

    def test_no_deadline_enriches_every_thread(self):
        reddit_items, _, _, _, _, enriched, _, _ = self._run(None)
        self.assertTrue(reddit_items)
        self.assertEqual(len(enriched), len(reddit_items))

    def test_passed_deadline_skips_enrichment_but_keeps_threads(self):
        reddit_items, _, _, _, _, enriched, reddit_error, _ = self._run(time.monotonic() - 1)
        self.assertTrue(reddit_items)
        self.assertEqual(enriched, [])
        self.assertIsNone(reddit_error)


if __name__ == "__main__":
    unittest.main()
