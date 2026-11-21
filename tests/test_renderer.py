import json
import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "scripts" / "render_report.py"
SAMPLE = ROOT / "tests" / "sample-experiment.json"


class RendererContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def render(self, data):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            input_path = directory_path / "experiment.json"
            output_path = directory_path / "report.html"
            input_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                ["python3", str(RENDERER), str(input_path), "--output", str(output_path)],
                text=True,
                capture_output=True,
                check=False,
            )

    def test_complete_four_language_report_renders(self):
        result = self.render(self.sample)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_required_language_is_rejected(self):
        data = deepcopy(self.sample)
        del data["i18n"]["locales"]["ja"]
        result = self.render(data)
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing: ja", result.stderr)

    def test_partial_translation_is_rejected(self):
        data = deepcopy(self.sample)
        del data["i18n"]["locales"]["en"]["content"]["rounds"]
        result = self.render(data)
        self.assertEqual(result.returncode, 2)
        self.assertIn("must translate all three rounds", result.stderr)

    def test_skipped_external_research_is_rejected(self):
        data = deepcopy(self.sample)
        data["analysis"]["research"]["attempted"] = False
        result = self.render(data)
        self.assertEqual(result.returncode, 2)
        self.assertIn("research.attempted must be true", result.stderr)


if __name__ == "__main__":
    unittest.main()
