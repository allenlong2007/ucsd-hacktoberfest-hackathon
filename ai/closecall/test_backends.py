import json
import os
import unittest
from unittest.mock import patch

from ai.closecall.test_verdict import load_pr
from run import call_model, gemini_models


ANSWER = {"claims": [], "summary": "Human review needed.", "reasons_not_to_close": []}


class BackendTests(unittest.TestCase):
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
