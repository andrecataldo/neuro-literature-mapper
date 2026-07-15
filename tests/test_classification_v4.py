from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from neuro_mapper.config import load_config
from neuro_mapper.tagging import suggest_priority


class ClassificationV4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config("config/queries_neuro.yaml")
        cls.cases = yaml.safe_load(
            Path("tests/classification_cases_neuro_v4.yaml")
            .read_text(encoding="utf-8")
        )["cases"]

    def test_regression_cases(self) -> None:
        for case in self.cases:
            with self.subTest(title=case["title"]):
                actual = suggest_priority(
                    config=self.config,
                    title=case["title"],
                    abstract=case.get("abstract", ""),
                )
                self.assertEqual(
                    case["expected_priority"],
                    actual,
                )


if __name__ == "__main__":
    unittest.main()
