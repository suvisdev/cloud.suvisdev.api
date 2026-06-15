from dataclasses import dataclass


@dataclass(frozen=True)
class StudioMoviesQuery:
    id: int
    name: str


@dataclass(frozen=True)
class StudioMoviesResponse:
    id: int
    name: str
