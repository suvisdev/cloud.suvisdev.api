from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformAssistantsQuery:
    id: int
    name: str


@dataclass(frozen=True)
class PlatformAssistantsResponse:
    id: int
    name: str
