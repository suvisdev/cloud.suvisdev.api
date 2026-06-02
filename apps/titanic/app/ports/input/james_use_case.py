from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class JamesUseCase(ABC):
    """James CSV 업로드(POST) 입력 포트 (ABC). 조회(GET)는 WalterUseCase."""

    @abstractmethod
    async def receive_uploaded_records(self, 
    person_commands: list[PersonCommand],
    booking_commands: list[BookingCommand]) -> int:
        pass
