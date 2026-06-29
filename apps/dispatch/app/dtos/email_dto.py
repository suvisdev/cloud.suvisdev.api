from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmailDto:
    to: str
    subject: str
    body: str
