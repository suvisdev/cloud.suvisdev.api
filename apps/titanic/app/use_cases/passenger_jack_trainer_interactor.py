from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery, JackTrainerResponse
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.output.passenger_jack_trainer_repository import JackTrainerRepository

logger = logging.getLogger(__name__)


class JackTrainerInteractor(JackTrainerUseCase):
    def __init__(self, repository: JackTrainerRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: JackTrainerSchema) -> JackTrainerResponse:
    
        return await self._repository.introduce_myself(JackTrainerQuery(
            id=schemas.id,
            name=schemas.name,
        ))
