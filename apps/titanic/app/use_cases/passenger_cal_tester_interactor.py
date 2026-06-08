from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterQuery, CalTesterResponse
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.output.passenger_cal_tester_repository import CalTesterRepository

logger = logging.getLogger(__name__)


class CalTesterInteractor(CalTesterUseCase):
    def __init__(self, repository: CalTesterRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: CalTesterSchema) -> CalTesterResponse:
     
        return await self._repository.introduce_myself(CalTesterQuery(
            id=schemas.id,
            name=schemas.name,
        ))
