from __future__ import annotations

from dataclasses import dataclass

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import ChatSchema


@dataclass(frozen=True)
class SmithCaptainQuery:
    id: int
    name: str


@dataclass(frozen=True)
class SmithCaptainResponse:
    id: int
    name: str


@dataclass(frozen=True)
class SmithCaptainChatCommand:
    message: str

    @classmethod
    def from_schema(cls, schema: ChatSchema) -> SmithCaptainChatCommand:
        return cls(message=schema.message)
 