from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InboxSaveCommand:
    sender: str
    subject: str
    body: str


@dataclass(frozen=True)
class InboxItem:
    id: int
    sender: str
    subject: str
    body: str
    received_at: datetime
