from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.james_dto import JamesRowPayload, JamesUploadResult


class JamesRepository(ABC):
    """James 업로드 데이터를 외부로 보내는 아웃바운드 포트 (ABC)."""

    @abstractmethod
    async def save_rows(
        self,
        rows: list[JamesRowPayload],
    ) -> JamesUploadResult:
        pass
