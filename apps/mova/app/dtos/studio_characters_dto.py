from dataclasses import dataclass


@dataclass(frozen=True)
class StudioCharactersQuery:
    id: int
    name: str


@dataclass(frozen=True)
class StudioCharactersResponse:
    id: int
    name: str
