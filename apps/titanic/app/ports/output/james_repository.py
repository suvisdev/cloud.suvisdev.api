from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from titanic.app.use_cases.james_command import JamesRowPayload, JamesUploadResult


class JamesRepositoryPort(Protocol):
    """james 업로드 데이터를 외부로 내보내는 아웃바운드 포트."""

    async def save_rows(self, rows: list["JamesRowPayload"]) -> "JamesUploadResult": ...


class JamesRepository(JamesRepositoryPort):
    """아웃바운드 PG 어댑터에 저장을 위임하는 포트 구현."""

    def __init__(self) -> None:
        from titanic.adapter.outbound.pg.james_pg_repository import JamesPgRepository

        self._pg_repository = JamesPgRepository()

    async def save_rows(self, rows: list["JamesRowPayload"]) -> "JamesUploadResult":
        return await self._pg_repository.save_rows(rows)
