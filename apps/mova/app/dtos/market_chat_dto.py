from dataclasses import dataclass


@dataclass(frozen=True)
class MarketChatQuery:
    id: int
    name: str


@dataclass(frozen=True)
class MarketChatResponse:
    id: int
    name: str
