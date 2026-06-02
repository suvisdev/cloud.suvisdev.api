from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.james_dto import BookingCommand, PersonCommand
from titanic.app.ports.output.james_repository import JamesRepository

logger = logging.getLogger(__name__)


class JamesPgRepository(JamesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def receive_uploaded_records(
        self,
        person_commands: list[PersonCommand],
        booking_commands: list[BookingCommand],
    ) -> int:
        # 🎁로그 코드 시작
        logger.info(
            "🤖 [JamesPgRepository] receive_uploaded_records 진입 — persons=%s bookings=%s",
            len(person_commands),
            len(booking_commands),
        )
        # 🎁로그 코드 끝
        for index, person in enumerate(person_commands[:5], start=1):
            # 🎁로그 코드 시작
            logger.info(
                "🤖 [JamesPgRepository] person_commands[%s/%s] — %s",
                index,
                min(5, len(person_commands)),
                person,
            )
            # 🎁로그 코드 끝
        for index, booking in enumerate(booking_commands[:5], start=1):
            # 🎁로그 코드 시작
            logger.info(
                "🤖 [JamesPgRepository] booking_commands[%s/%s] — %s",
                index,
                min(5, len(booking_commands)),
                booking,
            )
            # 🎁로그 코드 끝

        pass
