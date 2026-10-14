"""Tests for env module: API keys come from environment variables first."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Add lib to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from lib import env


class TestGetConfig(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.env_file = Path(self._tmp.name) / ".env"
        patcher = mock.patch.object(env, "CONFIG_FILE", self.env_file)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._tmp.cleanup)

    def test_environment_variables_without_a_file(self):
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "env-openai", "XAI_API_KEY": "env-xai"}):
            config = env.get_config()
        self.assertEqual(config["OPENAI_API_KEY"], "env-openai")
        self.assertEqual(config["XAI_API_KEY"], "env-xai")

    def test_environment_variable_beats_file(self):
        self.env_file.write_text("OPENAI_API_KEY=file-openai\nXAI_API_KEY='file-xai'\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "env-openai"}):
            os.environ.pop("XAI_API_KEY", None)
            config = env.get_config()
        self.assertEqual(config["OPENAI_API_KEY"], "env-openai")
        self.assertEqual(config["XAI_API_KEY"], "file-xai")

    def test_no_keys_means_web_only(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            config = env.get_config()
        self.assertEqual(env.get_available_sources(config), "web")
        self.assertEqual(env.get_missing_keys(config), "both")


class TestValidateSources(unittest.TestCase):
    def test_auto_without_keys_is_web_only_without_note(self):
        self.assertEqual(env.validate_sources("auto", "web"), ("web", None))

    def test_requested_source_without_keys_is_a_note(self):
        sources, note = env.validate_sources("reddit", "web")
        self.assertEqual(sources, "web")
        self.assertTrue(note.startswith(env.WEB_ONLY_NOTE))
        self.assertIn("environment variables", note)
        self.assertIn("Cowork", note)

    def test_include_web_with_both_keys(self):
        self.assertEqual(env.validate_sources("auto", "both", include_web=True), ("all", None))


if __name__ == "__main__":
    unittest.main()
