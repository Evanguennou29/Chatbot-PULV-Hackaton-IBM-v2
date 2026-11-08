import csv
import os
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source"))
import main
import Generate


class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.temp.name) / "knowledge.csv"
        self.csv_path.write_text("id,Title,Content,Post Type,Langues,Thématiques,Utilisateurs,Écoles,Status\n9,Question,Réponse,question,Français,,,ESILV,publish\n", encoding="utf-8")
        self.path_patch = patch.object(main, "DATASET_PATH", self.csv_path)
        self.path_patch.start()
        self.client = main.app.test_client()

    def tearDown(self):
        self.path_patch.stop()
        self.temp.cleanup()
        Generate.get_model.cache_clear()

    def test_home_and_health_without_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(self.client.get("/").status_code, 200)
            self.assertEqual(self.client.get("/health").json, {"status": "ok"})
            self.assertEqual(self.client.post("/answer", json={"question": "Bonjour"}).status_code, 503)

    def test_missing_dataset_is_unhealthy(self):
        with patch.object(main, "DATASET_PATH", self.csv_path.parent / "missing.csv"):
            self.assertEqual(self.client.get("/health").status_code, 503)

    def test_invalid_payloads(self):
        for endpoint in ("/answer", "/satisfied"):
            for data in (None, [], {"question": 12}, {"question": "  "}):
                self.assertEqual(self.client.post(endpoint, json=data).status_code, 400)
            self.assertEqual(self.client.post(endpoint, data="broken", content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post("/answer", json={"question": "a" * 2001}).status_code, 400)

    def test_model_response_and_failure(self):
        with patch.object(main, "generate_answer", return_value="Réponse test"):
            result = self.client.post("/answer", json={"question": " Bonjour "})
            self.assertEqual(result.json, {"question": "Bonjour", "answer": "Réponse test"})
        with patch.object(main, "generate_answer", side_effect=RuntimeError("provider details")):
            result = self.client.post("/answer", json={"question": "Bonjour"})
            self.assertEqual(result.status_code, 502)
            self.assertNotIn("provider details", result.get_data(as_text=True))

    def test_feedback_preserves_all_columns_and_existing_rows(self):
        result = self.client.post("/satisfied", json={"question": "Avec, virgule", "answer": "Deux\nlignes"})
        self.assertEqual(result.json, {"success": True, "id": 10})
        with self.csv_path.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["Écoles"], "ESILV")
        self.assertEqual(rows[1]["Content"], "Deux\nlignes")
        self.assertEqual(len(rows[1]), 9)
        self.assertTrue(all(value is not None for value in rows[1].values()))

    def test_concurrent_feedback_has_unique_ids(self):
        def submit(index):
            with main.app.test_client() as client:
                return client.post("/satisfied", json={"question": str(index), "answer": "Réponse"}).json["id"]
        with ThreadPoolExecutor(max_workers=4) as executor:
            ids = list(executor.map(submit, range(12)))
        self.assertEqual(sorted(ids), list(range(10, 22)))

    def test_project_or_space_must_be_exclusive(self):
        for env in ({"IBM_CLOUD_API_KEY": "test"}, {"IBM_CLOUD_API_KEY": "test", "WATSONX_PROJECT_ID": "p", "SPACE_ID": "s"}):
            with patch.dict(os.environ, env, clear=True):
                with self.assertRaises(Generate.ConfigurationError):
                    Generate.get_model()

    def test_model_prompt_and_cleaning(self):
        with patch.object(Generate, "DATASET_PATH", self.csv_path), patch.object(Generate, "get_model") as get_model:
            get_model.return_value.generate_text.return_value = "Une réponse.\nEntrée : suite"
            self.assertEqual(Generate.query("Ma question"), "Une réponse.")
            prompt = get_model.return_value.generate_text.call_args.kwargs["prompt"]
            self.assertIn("Entrée : Question\nSortie : Réponse", prompt)
            self.assertTrue(prompt.endswith("Entrée : Ma question\nSortie : \n"))


if __name__ == "__main__":
    unittest.main()
