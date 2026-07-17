from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from neuro_mapper.config import load_config
from neuro_mapper.tagging import (
    infer_corrente,
    suggest_priority,
    suggest_tags,
)


class ClassificationV43Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(
            "config/queries_neuro.yaml"
        )

        cases_path = Path(
            "tests/classification_cases_neuro_v4_3.yaml"
        )

        payload = yaml.safe_load(
            cases_path.read_text(encoding="utf-8")
        )

        cls.cases = payload["cases"]

    def test_regression_cases(self) -> None:
        for case in self.cases:
            case_id = case["id"]
            title = case.get("title", "")
            abstract = case.get("abstract", "")

            with self.subTest(case=case_id):
                actual_priority = suggest_priority(
                    config=self.config,
                    title=title,
                    abstract=abstract,
                )

                self.assertEqual(
                    case["expected_priority"],
                    actual_priority,
                    msg=(
                        f"Prioridade incorreta no caso "
                        f"{case_id!r}"
                    ),
                )

                actual_tags = set(
                    suggest_tags(
                        self.config,
                        title,
                        abstract,
                    )
                )

                for expected_tag in case.get(
                    "expected_tags_contains",
                    [],
                ):
                    self.assertIn(
                        expected_tag,
                        actual_tags,
                        msg=(
                            f"Tag esperada ausente no caso "
                            f"{case_id!r}: {expected_tag}"
                        ),
                    )

                for excluded_tag in case.get(
                    "expected_tags_excludes",
                    [],
                ):
                    self.assertNotIn(
                        excluded_tag,
                        actual_tags,
                        msg=(
                            f"Tag indevida no caso "
                            f"{case_id!r}: {excluded_tag}"
                        ),
                    )

                expected_corrente = case.get(
                    "expected_corrente"
                )

                if expected_corrente:
                    actual_corrente = infer_corrente(
                        title,
                        abstract,
                        self.config,
                    )

                    self.assertEqual(
                        expected_corrente,
                        actual_corrente,
                        msg=(
                            f"Corrente incorreta no caso "
                            f"{case_id!r}"
                        ),
                    )


if __name__ == "__main__":
    unittest.main()