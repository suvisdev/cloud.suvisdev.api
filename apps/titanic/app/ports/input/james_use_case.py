from __future__ import annotations

from typing import Protocol

from titanic.app.use_cases.james_command import (
    JamesCommand,
    JamesRowPayload,
    JamesUploadResult,
)


class JamesUseCasePort(Protocol):
    """CSV 업로드로 받은 데이터를 처리하는 입력 포트."""

    async def upload_rows(self, rows: list[JamesRowPayload]) -> JamesUploadResult: ...


class JamesUseCase(JamesUseCasePort):
    """입력 포트에서 use case 구현으로 위임."""

    def __init__(self, command: JamesCommand | None = None) -> None:
        self._command = command or JamesCommand()

    async def upload_rows(self, rows: list[JamesRowPayload]) -> JamesUploadResult:
        return await self._command.upload_rows(rows)

