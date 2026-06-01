from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from titanic.app.dtos.james_dto import JamesUploadResult


class JamesUseCase(ABC):
    """James CSV 업로드(POST) 입력 포트 (ABC). 조회(GET)는 WalterUseCase."""

    @abstractmethod
    async def receive_upload_records(
        self,
        records: list[dict[str, Any]],
    ) -> JamesUploadResult:
        pass
