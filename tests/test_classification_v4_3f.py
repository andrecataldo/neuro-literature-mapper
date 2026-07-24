from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from neuro_mapper.config import load_config
from neuro_mapper.tagging import suggest_priority


class ClassificationV43FTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(
            "config/queries_neuro.yaml"
        )

        cases_path = Path(
            "tests/classification_cases_neuro_v4_3f.yaml"
        )

        payload = yaml.safe_load(
            cases_path.read_text(
                encoding="utf-8"
            )
        )

        cls.cases = payload["cases"]

    def test_audited_p10_cases(self) -> None:
        self.assertEqual(
            28,
            len(self.cases),
        )

        for case in self.cases:
            with self.subTest(
                case=case["id"]
            ):
                actual = suggest_priority(
                    config=self.config,
                    title=case.get("title", ""),
                    abstract=case.get(
                        "abstract",
                        "",
                    ),
                )

                self.assertEqual(
                    case["expected_priority"],
                    actual,
                    msg=(
                        "Prioridade incorreta para "
                        f"{case['title']!r}"
                    ),
                )


if __name__ == "__main__":
    unittest.main()
