from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from star_craft.domain.events.base_event import BaseEvent


@dataclass(frozen=True)
class EventDto:
    event_id: str
    event_type: str
    source_spoke: str
    occurred_at: datetime

    @classmethod
    def from_event(cls, event: BaseEvent) -> EventDto:
        return cls(
            event_id=event.event_id,
            event_type=type(event).__name__,
            source_spoke=event.source_spoke,
            occurred_at=event.occurred_at,
        )
