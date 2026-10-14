"""Tests for xai_x response parsing and how research.py records a bad reply."""

import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lib import http, render, schema, xai_x


def _reply(text):
    """An xAI Responses API reply whose message text is `text`."""
    return {"output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}]}


class TestParseXResponse(unittest.TestCase):
    def test_reads_items(self):
        items = xai_x.parse_x_response(_reply(
            '{"items": [{"text": "hi", "url": "https://x.com/a/status/1", "author_handle": "@a"}]}'
        ))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["author_handle"], "a")

    def test_empty_items_list_is_not_an_error(self):
        self.assertEqual(xai_x.parse_x_response(_reply('{"items": []}')), [])

    def test_unreadable_json_raises(self):
        with self.assertRaises(http.BadResponseError):
            xai_x.parse_x_response(_reply('{"items": [ {"text": }'))

    def test_no_output_text_raises(self):
        with self.assertRaises(http.BadResponseError):
            xai_x.parse_x_response({"output": []})


class TestBadReplyIsNotCovered(unittest.TestCase):
    """A reply the script cannot read sets the source's error, so the
    'Script covered' line leaves that site out for the subagents."""

    def setUp(self):
        import research  # imported here: it is a script with import-time setup
        self.research = research

    def test_bad_x_reply_sets_x_error(self):
        with mock.patch.object(self.research.xai_x, "search_x", return_value=_reply("no json here")):
            items, _, error = self.research._search_x(
                "topic", {"XAI_API_KEY": "k"}, {"xai": "m"}, "2026-01-01", "2026-03-01", "quick", False
            )
        self.assertEqual(items, [])
        self.assertTrue(error.startswith("Bad response:"))

        report = schema.Report(
            topic="t", range_from="2026-01-01", range_to="2026-03-01",
            generated_at="2026-03-01T12:00:00Z", mode="both",
        )
        report.x_error = error
        self.assertEqual(render.covered_sites(report), ["reddit.com"])

    def test_bad_reddit_reply_sets_reddit_error(self):
        with mock.patch.object(self.research.openai_reddit, "search_reddit", return_value=_reply('{"items": [')):
            items, _, error = self.research._search_reddit(
                "topic", {"OPENAI_API_KEY": "k"}, {"openai": "m"}, "2026-01-01", "2026-03-01", "quick", False
            )
        self.assertEqual(items, [])
        self.assertTrue(error.startswith("Bad response:"))


if __name__ == "__main__":
    unittest.main()
