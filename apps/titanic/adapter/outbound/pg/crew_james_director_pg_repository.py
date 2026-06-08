from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import ensure_titanic_tables, get_mova_session_factory
from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import Booking
from titanic.adapter.outbound.orm.passenger_rose_model_orm import Person
from titanic.app.dtos.crew_james_director_dto import BookingCommand, PassengerCommand
from titanic.app.ports.output.crew_james_director_repository import JamesRepository

logger = logging.getLogger(__name__)


class JamesPgRepository(JamesRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def receive_uploaded_records(
        self,
        person_commands: list[PassengerCommand],
        booking_commands: list[BookingCommand],
    ) -> int:
        await ensure_titanic_tables()

        if self._session is not None:
            return await self._persist(self._session, person_commands, booking_commands)

        factory = get_mova_session_factory()
        async with factory() as session:
            count = await self._persist(session, person_commands, booking_commands)
            await session.commit()
            return count

    async def _persist(
        self,
        session: AsyncSession,
        person_commands: list[PassengerCommand],
        booking_commands: list[BookingCommand],
    ) -> int:
        if len(person_commands) != len(booking_commands):
            raise ValueError("person_commands와 booking_commands 길이가 일치해야 합니다.")

        passenger_ids = [cmd.passenger_id for cmd in person_commands]
        result = await session.execute(
            select(Person).where(Person.passenger_id.in_(passenger_ids)),
        )
        existing_by_passenger_id = {
            person.passenger_id: person for person in result.scalars().all()
        }

        for person_cmd in person_commands:
            person_row = existing_by_passenger_id.get(person_cmd.passenger_id)
            if person_row is None:
                person_row = Person.from_command(person_cmd)
                session.add(person_row)
                existing_by_passenger_id[person_cmd.passenger_id] = person_row
                continue

            person_row.name = person_cmd.name
            person_row.gender = person_cmd.gender
            person_row.age = person_cmd.age
            person_row.sib_sp = person_cmd.sib_sp
            person_row.parch = person_cmd.parch
            person_row.survived = person_cmd.survived

        await session.flush()

        saved = 0
        for person_cmd, booking_cmd in zip(person_commands, booking_commands, strict=True):
            person_row = existing_by_passenger_id[person_cmd.passenger_id]
            session.add(Booking.from_command(booking_cmd, person_id=person_row.id))
            saved += 1

        if self._session is not None:
            await session.commit()

        return saved
