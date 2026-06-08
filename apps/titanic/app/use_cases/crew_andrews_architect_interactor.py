from __future__ import annotations

from titanic.adapter.inbound.api.schemas.crew_andrews_architect_schema import AndrewsArchitectSchema
from titanic.app.dtos.crew_andrews_architect_dto import AndrewsArchitectQuery, AndrewsArchitectResponse
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.ports.output.crew_andrews_architect_repository import AndrewsArchitectRepository


class AndrewsArchitectInteractor(AndrewsArchitectUseCase):
    def __init__(self, repository: AndrewsArchitectRepository):
        self._repository = repository

    async def introduce_myself(
        self,
        schemas: AndrewsArchitectSchema,
    ) -> AndrewsArchitectResponse:
        
        return await self._repository.introduce_myself(AndrewsArchitectQuery(
            id=schemas.id,
            name=schemas.name,
        ))
