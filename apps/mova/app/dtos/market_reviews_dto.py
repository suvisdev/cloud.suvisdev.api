from dataclasses import dataclass


@dataclass(frozen=True)
class MarketReviewsQuery:
    id: int
    name: str


@dataclass(frozen=True)
class MarketReviewsResponse:
    id: int
    name: str
