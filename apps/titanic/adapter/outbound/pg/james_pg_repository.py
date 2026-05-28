from __future__ import annotations

from typing import TYPE_CHECKING

from core.database import get_mova_session_factory
from titanic.adapter.outbound.orm.james_orm_model import TitanicPassengerRow

if TYPE_CHECKING:
    from titanic.app.use_cases.james_command import JamesRowPayload, JamesUploadResult


class JamesPgRepository:
    """Titanic James 업로드 데이터 — Neon(PostgreSQL) 아웃바운드 어댑터."""

    async def save_rows(self, rows: list["JamesRowPayload"]) -> "JamesUploadResult":
        from titanic.app.use_cases.james_command import JamesUploadResult

        if not rows:
            return JamesUploadResult(row_count=0, rows=[])

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

        return JamesUploadResult(row_count=len(rows), rows=rows)
