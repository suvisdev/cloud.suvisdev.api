from __future__ import annotations

from dataclasses import dataclass, field

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import MessageSchema


@dataclass(frozen=True)
class SmithCaptainQuery:
    id: int
    name: str


@dataclass(frozen=True)
class SmithCaptainResponse:
    id: int
    name: str


@dataclass(frozen=True)
class SmithChatResponse:
    reply: str


@dataclass(frozen=True)
class SmithCaptainChatCommand:
    messages: list[MessageSchema]
    system_instruction: str | None = None
    model: str | None = "flash"
 