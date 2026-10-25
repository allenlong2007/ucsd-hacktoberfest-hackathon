import json
import os
import unittest
from urllib.error import HTTPError
from unittest.mock import patch

from ai.closecall.test_verdict import load_pr
from run import call_model, gemini_models, resolve_verifier, request_json


ANSWER = {"claims": [], "summary": "Human review needed.", "reasons_not_to_close": []}


class BackendTests(unittest.TestCase):
    def test_nonfixture_cannot_fall_back_to_stub(self):
        with patch("run.importlib.import_module", side_effect=ModuleNotFoundError(name="verify")):
            with self.assertRaisesRegex(RuntimeError, "Real verifier required"):
                resolve_verifier({"repo": "jestjs/jest"})
            self.assertEqual(resolve_verifier({"_fixture": True})[1], "stub")

    def test_verifier_internal_errors_do_not_enable_stub(self):
        with patch("run.importlib.import_module", side_effect=ModuleNotFoundError(name="dependency")):
            with self.assertRaises(ModuleNotFoundError):
                resolve_verifier({"_fixture": True})

    def test_gemini_429_backs_off_and_retries(self):
        response = unittest.mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'{}'
        error = HTTPError("https://generativelanguage.googleapis.com/", 429, "rate limited", {}, None)
        with patch("run.urlopen", side_effect=[error, response]) as request, patch("run.time.sleep") as sleep:
            self.assertEqual(request_json("https://generativelanguage.googleapis.com/v1beta/models"), {})
            self.assertEqual(request.call_count, 2)
            sleep.assert_called_once_with(2)

    def test_gemini_ignores_thought_parts(self):
        body = {"candidates": [{"content": {"parts": [
            {"text": "private reasoning", "thought": True}, {"text": json.dumps(ANSWER)}]}}]}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-only"}), patch("run.request_json", return_value=body):
            self.assertEqual(call_model("prompt", "models/discovered", "gemini")[0], ANSWER)

    def test_ollama_retries_invalid_json(self):
        with patch("run.request_json", side_effect=[{"response": "invalid"},
                   {"response": json.dumps(ANSWER)}]) as request:
            result, _ = call_model("prompt", "local", "ollama")
            self.assertEqual(result, ANSWER)
            self.assertEqual(request.call_count, 2)

    def test_gemini_request_and_retry(self):
        def reply(text):
            return {"candidates": [{"content": {"parts": [{"text": text}]}}]}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-only"}), patch(
            "run.request_json", side_effect=[reply("bad"), reply(json.dumps(ANSWER))]
        ) as request:
            self.assertEqual(call_model("prompt", "models/discovered", "gemini")[0], ANSWER)
            self.assertEqual(request.call_count, 2)
            self.assertEqual(request.call_args.args[2]["x-goog-api-key"], "test-only")

    def test_discovery_filters_and_paginates(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-only"}), patch(
            "run.request_json", side_effect=[{"models": [{"name": "models/gemini-example"}],
            "nextPageToken": "page2"}, {"models": [{"name": "models/gemma-4-example",
            "supportedGenerationMethods": ["generateContent"]}]}]
        ):
            self.assertEqual(gemini_models(), ["models/gemma-4-example"])


if __name__ == "__main__":
    unittest.main()
