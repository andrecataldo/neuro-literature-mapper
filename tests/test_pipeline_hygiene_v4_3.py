from __future__ import annotations

import unittest

from neuro_mapper.config import load_config
from neuro_mapper.export import records_to_dataframe
from neuro_mapper.models import WorkRecord
from neuro_mapper.pipeline import (
    classify_records,
    deduplicate_records,
    is_supplementary_material,
    normalize_doi,
    normalize_title,
)


def make_record(
    *,
    source_api: str = "Crossref",
    title: str = "Example article",
    doi: str = "",
    url: str = "",
    abstract: str = "Example abstract.",
    year: int | None = 2025,
    cited_by_count: int | None = 1,
    duplicate_count: int = 1,
) -> WorkRecord:
    return WorkRecord(
        source_api=source_api,
        query_layer="test-layer",
        query="test-query",
        title=title,
        year=year,
        authors="Test Author",
        venue="Test Venue",
        doi=doi,
        url=url,
        abstract=abstract,
        cited_by_count=cited_by_count,
        suggested_priority="",
        suggested_tags="",
        duplicate_count=duplicate_count,
    )


class PipelineHygieneV43Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(
            "config/queries_neuro.yaml"
        )

    def test_title_prefixes_are_normalized(self) -> None:
        base_title = (
            "High-performance brain-to-text "
            "communication via handwriting"
        )

        variants = [
            base_title,
            f"Title: {base_title}",
            f"Title : {base_title}",
            f"Paper title: {base_title}",
            f"Article title: {base_title}",
            f"Manuscript title: {base_title}",
        ]

        normalized = {
            normalize_title(title)
            for title in variants
        }

        self.assertEqual(
            1,
            len(normalized),
        )

    def test_title_deduplication_and_source_order(self) -> None:
        records = [
            make_record(
                source_api="Semantic Scholar",
                title="Title : Example Brain-to-Text Study",
            ),
            make_record(
                source_api="OpenAlex",
                title="Example Brain-to-Text Study",
            ),
            make_record(
                source_api="Crossref",
                title="Paper title: Example Brain-to-Text Study",
            ),
        ]

        result = deduplicate_records(records)

        self.assertEqual(1, len(result))
        self.assertEqual(
            3,
            result[0].duplicate_count,
        )
        self.assertEqual(
            "Crossref | OpenAlex | Semantic Scholar",
            result[0].source_api,
        )

    def test_doi_normalization(self) -> None:
        variants = [
            "10.1234/example",
            "https://doi.org/10.1234/example",
            "http://dx.doi.org/10.1234/example",
            "doi:10.1234/example",
            "10.1234/example.",
        ]

        normalized = {
            normalize_doi(doi)
            for doi in variants
        }

        self.assertEqual(
            {"10.1234/example"},
            normalized,
        )

    def test_supplementary_material_detection(self) -> None:
        title_record = make_record(
            title=(
                "CLEP-based EEG to text "
                "reconstruction_supp4-3665623.png"
            )
        )

        url_record = make_record(
            title="Supporting dataset",
            url=(
                "https://example.org/files/"
                "experiment-supp2.xlsx"
            ),
        )

        valid_record = make_record(
            title=(
                "The Role of the Supplementary "
                "Motor Area in Speech"
            )
        )

        self.assertTrue(
            is_supplementary_material(title_record)
        )
        self.assertTrue(
            is_supplementary_material(url_record)
        )
        self.assertFalse(
            is_supplementary_material(valid_record)
        )

    def test_invalid_records_are_discarded(self) -> None:
        supplementary = make_record(
            title=(
                "CLEP-based EEG to text "
                "reconstruction_supp4-3665623.png"
            ),
            abstract=(
                "EEG brain-to-text decoding using "
                "neural signals."
            ),
        )

        missing_title = make_record(
            title="",
            abstract=(
                "EEG brain-to-text decoding using "
                "neural signals."
            ),
        )

        classified = classify_records(
            [
                supplementary,
                missing_title,
            ],
            self.config,
        )

        supplementary_result = classified[0]
        missing_title_result = classified[1]

        self.assertEqual(
            "supplementary-material",
            supplementary_result.publication_status,
        )
        self.assertEqual(
            "D-descartar",
            supplementary_result.suggested_priority,
        )

        self.assertEqual(
            "D-descartar",
            missing_title_result.suggested_priority,
        )
        self.assertEqual(
            "low",
            missing_title_result.metadata_completeness,
        )

    def test_integer_columns_do_not_use_decimal_suffix(self) -> None:
        records = [
            make_record(
                year=2025,
                cited_by_count=42,
                duplicate_count=3,
            ),
            make_record(
                title="Article without numeric metadata",
                year=None,
                cited_by_count=None,
                duplicate_count=1,
            ),
        ]

        dataframe = records_to_dataframe(records)

        self.assertEqual(
            "Int64",
            str(dataframe["year"].dtype),
        )
        self.assertEqual(
            "Int64",
            str(dataframe["cited_by_count"].dtype),
        )
        self.assertEqual(
            "Int64",
            str(dataframe["duplicate_count"].dtype),
        )

        csv_text = dataframe.to_csv(
            index=False,
            na_rep="",
        )

        self.assertNotIn("2025.0", csv_text)
        self.assertNotIn("42.0", csv_text)
        self.assertNotIn("3.0", csv_text)


if __name__ == "__main__":
    unittest.main()