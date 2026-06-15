from dataclasses import dataclass


@dataclass(frozen=True)
class MarketPicksQuery:
    id: int
    name: str


@dataclass(frozen=True)
class MarketPicksResponse:
    id: int
    name: str
