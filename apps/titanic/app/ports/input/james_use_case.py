from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.use_cases.james_command import (
    JamesCommand,
    JamesRowPayload,
    JamesUploadResult,
)


class JamesUseCase(ABC):
    """James CSV 업로드(POST) 입력 포트 (ABC). 조회(GET)는 WalterUseCase."""

    @abstractmethod
    async def receive_upload_records(records: list[dict[str, Any]]) -> JamesUploadResult:
        pass
