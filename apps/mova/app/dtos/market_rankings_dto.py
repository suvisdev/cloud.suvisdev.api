from dataclasses import dataclass


@dataclass(frozen=True)
class MarketRankingsQuery:
    id: int
    name: str


@dataclass(frozen=True)
class MarketRankingsResponse:
    id: int
    name: str
