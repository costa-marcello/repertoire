"""Tests for research.py output: the web coverage block, the lookback window,
and a real web-only run (no API keys, so no network calls)."""

import os
import subprocess
import sys
import tempfile
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
        self.assertIn("SearXNG", block)
        self.assertIn("WebSearch and WebFetch", block)
        self.assertNotIn("Use your WebSearch tool", block)

    def test_include_web_block_lists_covered_sites(self):
        block = render.web_search_block(_report("all"), "t", "2026-01-01", "2026-03-01")
        self.assertIn("Script covered: reddit.com, x.com, twitter.com", block)


class TestLookbackWindow(unittest.TestCase):
    def test_default_range_uses_lookback_days(self):
        from_date, to_date = dates.get_date_range()
        span = datetime.strptime(to_date, "%Y-%m-%d") - datetime.strptime(from_date, "%Y-%m-%d")
        self.assertEqual(span.days, dates.LOOKBACK_DAYS)


class TestWebOnlyRun(unittest.TestCase):
    def test_runs_from_any_folder_with_utf8_output(self):
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as cwd:
            child_env = dict(os.environ)
            for key in ("OPENAI_API_KEY", "XAI_API_KEY", "PYTHONIOENCODING", "PYTHONUTF8"):
                child_env.pop(key, None)
            child_env["HOME"] = home
            child_env["USERPROFILE"] = home
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPTS / "research.py"), "café ✓ topic", "--emit=compact"],
                cwd=cwd,
                env=child_env,
                capture_output=True,
                timeout=60,
            )
        stdout = result.stdout.decode("utf-8")
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        self.assertIn("**Mode:** web-only", stdout)
        self.assertIn("**Script covered:** none", stdout)
        self.assertIn(render.WEB_SEARCH_MARKER, stdout)
        self.assertIn("café ✓ topic", stdout)


if __name__ == "__main__":
    unittest.main()
