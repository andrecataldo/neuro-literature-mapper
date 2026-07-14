from dataclasses import dataclass, asdict
from typing import Optional


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
    decision: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
