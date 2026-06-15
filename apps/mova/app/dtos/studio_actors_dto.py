from dataclasses import dataclass


@dataclass(frozen=True)
class StudioActorsQuery:
    id: int
    name: str


@dataclass(frozen=True)
class StudioActorsResponse:
    id: int
    name: str
