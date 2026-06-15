from dataclasses import dataclass


@dataclass(frozen=True)
class StudioImportQuery:
    id: int
    name: str


@dataclass(frozen=True)
class StudioImportResponse:
    id: int
    name: str
