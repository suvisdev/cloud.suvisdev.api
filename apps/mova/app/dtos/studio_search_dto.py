from dataclasses import dataclass


@dataclass(frozen=True)
class StudioSearchQuery:
    id: int
    name: str


@dataclass(frozen=True)
class StudioSearchResponse:
    id: int
    name: str
