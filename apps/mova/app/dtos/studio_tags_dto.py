from dataclasses import dataclass


@dataclass(frozen=True)
class StudioTagsQuery:
    id: int
    name: str


@dataclass(frozen=True)
class StudioTagsResponse:
    id: int
    name: str
