from __future__ import annotations

from titanic.adapter.inbound.api.schemas.james_schema import TitanicRowSchema
from titanic.app.dtos.james_dto import BookingCommand, JamesResponse, PersonCommand
from titanic.app.ports.input.james_use_case import JamesUseCase
from titanic.app.ports.output.james_repository import JamesRepository


class JamesInteractor(JamesUseCase):
    """james_router → 입력 포트 → 출력 포트(repository) — 스키마까지 전달."""

    def __init__(self, repository: JamesRepository) -> None:
        self._repository = repository

    async def receive_uploaded_records(
        self, schemas: list[TitanicRowSchema]
    ) -> JamesResponse:
        person_commands = [
            PersonCommand(
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
