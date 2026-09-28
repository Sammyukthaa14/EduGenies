"""Run with: python -m unittest discover -s tests -v"""
import os
import sys
import unittest
import asyncio
from pathlib import Path
from unittest.mock import patch, AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from main import app
from quiz_module import validate_quiz
from ai_client import ProviderError, complete


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"GEMINI_API_KEY": "", "OPENROUTER_API_KEY": "", "EXPLANATION_PROVIDER": "auto"})
        self.env.start()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        self.env.stop()

    def test_home_and_health(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertIn("EduGenie", self.client.get("/").text)
        self.assertEqual(self.client.get("/health").json(), {
            "status": "ok", "gemini_configured": False, "openrouter_configured": False,
        })

    def test_all_features_call_gemini(self):
        for endpoint, module in (("/explain", "explanation_module"), ("/qa", "qna"), ("/summarize", "summary_module"), ("/learn/recommendations", "learning_path")):
            with self.subTest(endpoint=endpoint), patch(f"{module}.complete", new_callable=AsyncMock, return_value=("Generated answer", "gemini")):
                payload = {"topic": "SQL", "level": "beginner"} if endpoint == "/learn/recommendations" else {"text": "Explain photosynthesis"}
                res = self.client.post(endpoint, json=payload)
                self.assertEqual(res.status_code, 200, res.text)
                self.assertEqual(res.json(), {"result": "Generated answer", "provider": "gemini"})
        import json
        items = [{"question": f"Question {n}", "options": ["A", "B", "C", "D"], "answer": "A"} for n in range(3)]
        with patch("quiz_module.complete", new_callable=AsyncMock, return_value=(json.dumps(items), "gemini")):
            res = self.client.post("/quiz", json={"text": "Earth orbits the Sun."})
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.json()["questions"]), 3)
            self.assertEqual(res.json()["provider"], "gemini")

    def test_gemini_failure_uses_openrouter_fallback(self):
        with patch("ai_client.gemini", new_callable=AsyncMock, side_effect=ProviderError("Gemini unavailable")), \
                patch("ai_client.openrouter", new_callable=AsyncMock, return_value="Fallback answer") as fallback:
            result = asyncio.run(complete("Explain photosynthesis"))
        self.assertEqual(result, ("Fallback answer", "openrouter"))
        fallback.assert_awaited_once_with("Explain photosynthesis", False)

    def test_validation_and_bad_quiz(self):
        self.assertEqual(self.client.post("/explain", json={"text": "a"}).status_code, 422)
        self.assertEqual(self.client.post("/learn/recommendations", json={"topic": "SQL", "level": "expert"}).status_code, 422)
        with self.assertRaises(ProviderError):
            validate_quiz([{"question": "bad", "options": ["a"], "answer": "a"}])


if __name__ == "__main__":
    unittest.main()
