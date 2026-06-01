from __future__ import annotations

import logging
from typing import Any

from titanic.app.dtos.james_dto import JamesRowPayload, JamesUploadResult
from titanic.app.ports.output.james_repository import JamesRepository
from titanic.app.ports.input.james_use_case import JamesUseCase

logger = logging.getLogger(__name__)


class JamesInteractor(JamesUseCase):
    """james_router → 입력 포트 → 출력 포트(repository)로 업로드 데이터 이동."""

    def __init__(self, repository: JamesRepository | None = None) -> None:
        self._repository = repository

    async def receive_upload_records(
        self,
        records: list[dict[str, Any]],
    ) -> JamesUploadResult:
        logger.info(
            "🤖 [JamesInteractor] receive_upload_records 진입 — rows=%s",
            len(records),
        )
        rows = [JamesRowPayload.model_validate(record) for record in records]
        result = await self._repository.save_rows(rows)
        logger.info(
            "🤖 [JamesInteractor] receive_upload_records 완료 — saved=%s",
            result.row_count,
        )
        return result