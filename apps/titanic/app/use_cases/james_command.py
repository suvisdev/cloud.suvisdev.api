from __future__ import annotations

from pydantic import BaseModel
from titanic.app.ports.output.james_repository import JamesRepository, JamesRepositoryPort


class JamesRowPayload(BaseModel):
    passenger_id: str
    survived: str
    pclass: str
    name: str
    gender: str
    age: str
    sibsp: str
    parch: str
    ticket: str
    fare: str
    cabin: str
    embarked: str


class JamesUploadResult(BaseModel):
    row_count: int
    rows: list[JamesRowPayload]


class JamesCommand:
    """james 입력 데이터를 애플리케이션 유스케이스로 이동/처리."""

    def __init__(self, repository: JamesRepositoryPort | None = None) -> None:
        self._repository = repository or JamesRepository()

    async def upload_rows(self, rows: list[JamesRowPayload]) -> JamesUploadResult:
        # use case -> output port(repository)로 전달
        return await self._repository.save_rows(rows)

