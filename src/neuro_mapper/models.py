from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import ClassVar, Optional


@dataclass
class WorkRecord:
    source_api: str
    query_layer: str
    query: str
    title: str
    year: Optional[int]
    authors: str
    venue: str
    doi: str
    url: str
    abstract: str
    cited_by_count: Optional[int]
    suggested_priority: str
    suggested_tags: str

    professor_source: str = ""
    corrente: str = ""
    publication_status: str = ""
    metadata_completeness: str = ""
    decision: str = ""
    notes: str = ""
    seed_source: str = ""
    duplicate_count: int = 1

    # Campo legado, aceito temporariamente, mas não exportado.
    classification_confidence: str = ""

    CSV_FIELDS: ClassVar[list[str]] = [
        "source_api",
        "query_layer",
        "query",
        "title",
        "year",
        "authors",
        "venue",
        "doi",
        "url",
        "abstract",
        "cited_by_count",
        "suggested_priority",
        "suggested_tags",
        "corrente",
        "publication_status",
        "metadata_completeness",
        "seed_source",
        "duplicate_count",
        "decision",
        "notes",
    ]

    def to_dict(self) -> dict:
        data = asdict(self)
        legacy_source = data.pop("professor_source", "")
        data.pop("classification_confidence", None)

        if not data.get("seed_source"):
            data["seed_source"] = legacy_source

        return {
            field: data.get(field, "")
            for field in self.CSV_FIELDS
        }
