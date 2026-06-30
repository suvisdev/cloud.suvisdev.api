"""Spoke → Hub 이벤트 타입 정의."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DispatchEmailEvent:
    to: str
    prompt: str
    subject: str | None
