from __future__ import annotations

import logging

from core.database import ensure_titanic_tables, get_mova_session_factory
from titanic.adapter.outbound.orm.james_orm_model import TitanicPassengerRow
from titanic.app.dtos.james_dto import JamesRowPayload, JamesUploadResult
from titanic.app.ports.output.james_repository import JamesRepository

logger = logging.getLogger(__name__)


class JamesPgRepository(JamesRepository):
    def __init__(self, repository: JamesRepository | None = None) -> None:
        self._repository = repository
    
    """Titanic James 업로드 — Neon(PostgreSQL) 아웃바운드 어댑터 (포트 구현)."""

    async def save_rows(self, rows: list[JamesRowPayload]) -> JamesUploadResult:
        logger.info("🤖 [JamesPgRepository] save_rows 진입 — rows=%s", len(rows))

        if not rows:
            logger.info("🤖 [JamesPgRepository] save_rows 완료 — saved=0")
            return JamesUploadResult(row_count=0, rows=[])

        await ensure_titanic_tables()
        factory = get_mova_session_factory()
        async with factory() as session:
            session.add_all(
                [
                    TitanicPassengerRow(
                        passenger_id=row.passenger_id,
                        survived=row.survived,
                        pclass=row.pclass,
                        name=row.name,
                        gender=row.gender,
                        age=row.age,
                        sibsp=row.sibsp,
                        parch=row.parch,
                        ticket=row.ticket,
                        fare=row.fare,
                        cabin=row.cabin,
                        embarked=row.embarked,
                    )
                    for row in rows
                ],
            )
            await session.commit()

        logger.info("🤖 [JamesPgRepository] save_rows 완료 — saved=%s", len(rows))
        return JamesUploadResult(row_count=len(rows), rows=rows)
