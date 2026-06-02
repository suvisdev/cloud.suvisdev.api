from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

class JamesRepository(ABC):
    """James 업로드 데이터를 외부로 보내는 아웃바운드 포트 (ABC)."""
    @abstractmethod
    async def receive_uploaded_records(
        self,
        person_commands: list[PersonCommand], 
        booking_commands: list[BookingCommand]) -> int:
        pass
