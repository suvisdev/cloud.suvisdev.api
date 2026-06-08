from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_james_director_schema import JamesSchema

class JamesUseCase(ABC):
    """James CSV 업로드(POST) 입력 포트 (ABC). 조회(GET)는 WalterUseCase."""

    @abstractmethod
    async def receive_uploaded_records(
        self,
        schemas: list["JamesSchema"],
    ):
        pass
