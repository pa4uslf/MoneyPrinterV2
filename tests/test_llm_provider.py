import os
import sys
import unittest
from unittest.mock import Mock
from unittest.mock import patch


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import llm_provider


class LlmProviderTests(unittest.TestCase):
    @patch("llm_provider.get_lms_base_url", return_value="http://127.0.0.1:1234/v1")
    @patch("llm_provider.requests.get")
    def test_list_models_reads_lm_studio_models(self, get_mock, _base_url_mock) -> None:
        response = Mock()
        response.json.return_value = {
            "data": [{"id": "model-b"}, {"id": "model-a"}, {"object": "model"}]
        }
        get_mock.return_value = response

        self.assertEqual(llm_provider.list_models(), ["model-a", "model-b"])
        get_mock.assert_called_once_with("http://127.0.0.1:1234/v1/models", timeout=5)
        response.raise_for_status.assert_called_once()

    @patch("llm_provider.get_lms_base_url", return_value="http://127.0.0.1:1234/v1/")
    @patch("llm_provider.requests.post")
    def test_generate_text_posts_chat_completion(self, post_mock, _base_url_mock) -> None:
        response = Mock()
        response.json.return_value = {
            "choices": [{"message": {"content": " hello "}}],
        }
        post_mock.return_value = response

        self.assertEqual(llm_provider.generate_text("Say hi", model_name="local-model"), "hello")
        post_mock.assert_called_once_with(
            "http://127.0.0.1:1234/v1/chat/completions",
            json={
                "model": "local-model",
                "messages": [{"role": "user", "content": "Say hi"}],
            },
            timeout=120,
        )
        response.raise_for_status.assert_called_once()


if __name__ == "__main__":
    unittest.main()
