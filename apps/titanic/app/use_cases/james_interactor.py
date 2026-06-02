from __future__ import annotations

import logging
from typing import Any

from titanic.adapter.outbound.pg.james_pg_repository import JamesPgRepository
from titanic.adapter.inbound.api.schemas.james_schema import TitanicRowSchema
from titanic.app.dtos.james_dto import BookingCommand, PersonCommand
from titanic.app.ports.input.james_use_case import JamesUseCase
from titanic.app.ports.output.james_repository import JamesRepository

logger = logging.getLogger(__name__)


class JamesInteractor(JamesUseCase):
    """james_router → 입력 포트 → 출력 포트(repository) — 스키마까지 전달."""

    def __init__(self) -> None:
        pass

    async def receive_uploaded_records(self, schemas: list[TitanicRowSchema]):
        # 🎁로그 코드 시작
        logger.info(
            "[🤖JamesUseCase] receive_uploaded_records 진입 — rows=%s",
            len(schemas),
        )
        # 🎁로그 코드 끝

        preview_count = min(5, len(schemas))
        for index, schema in enumerate(schemas[:preview_count], start=1):
            # 🎁로그 코드 시작
            logger.info(
                "[🤖JamesUseCase] TitanicRowSchema[%s/%s] — %s",
                index,
                preview_count,
                schema.model_dump(),
            )
            # 🎁로그 코드 끝

        # schema를 PersonCommand, BookingCommand로 나눠 옮겨담기
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
        repository: JamesRepository = JamesPgRepository(None)

        await repository.receive_uploaded_records(person_commands, booking_commands)

        pass


