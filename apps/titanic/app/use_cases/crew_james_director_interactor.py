from __future__ import annotations

from typing import TYPE_CHECKING

from titanic.app.dtos.crew_james_director_dto import BookingCommand, JamesResponse, PassengerCommand
from titanic.app.ports.input.crew_james_director_use_case import JamesUseCase
from titanic.app.ports.output.crew_james_director_repository import JamesRepository
from titanic.adapter.inbound.api.schemas.crew_james_director_schema import JamesSchema


class JamesInteractor(JamesUseCase):
    """crew_james_director_router → 입력 포트 → 출력 포트(repository)."""

    def __init__(self, repository: JamesRepository) -> None:
        self._repository = repository

    async def receive_uploaded_records(
        self,
        schemas: list[JamesSchema],
    ) -> JamesResponse:
        person_commands = [
            PassengerCommand(
                passenger_id=schema.passenger_id,
                name=schema.name,
                gender=schema.gender,
                age=schema.age,
                sib_sp=schema.sib_sp,
                parch=schema.parch,
                survived=schema.survived,
            )
            for schema in schemas
        ]
        booking_commands = [
            BookingCommand(
                pclass=schema.pclass,
                ticket=schema.ticket,
                fare=schema.fare,
                cabin=schema.cabin,
                embarked=schema.embarked,
            )
            for schema in schemas
        ]
        saved = await self._repository.receive_uploaded_records(
            person_commands,
            booking_commands,
        )
        return JamesResponse(answer=str(saved))
