from __future__ import annotations

import logging

from sqlalchemy import func, select

from core.database import ensure_titanic_tables, get_mova_session_factory
from titanic.adapter.outbound.orm.james_orm_model import TitanicPassengerRow
from titanic.app.dtos.walter_dto import WalterPassengerItem
from titanic.app.ports.output.walter_reader import WalterReader

logger = logging.getLogger(__name__)


class WalterPgReader(WalterReader):
    """Titanic 승객 목록 조회 — PostgreSQL 아웃바운드 어댑터 (포트 구현)."""

    async def read_passengers_page(
        self,
        offset: int,
        limit: int,
    ) -> tuple[list[WalterPassengerItem], int]:
        await ensure_titanic_tables()
        logger.info(
            "🤖 [WalterPgReader] read_passengers_page 진입 (Neon) — offset=%s limit=%s",
            offset,
            limit,
        )
        factory = get_mova_session_factory()
        async with factory() as session:
            count_result = await session.execute(
                select(func.count()).select_from(TitanicPassengerRow),
            )
            total = int(count_result.scalar_one())

            result = await session.execute(
                select(TitanicPassengerRow)
                .order_by(TitanicPassengerRow.id.asc())
                .offset(offset)
                .limit(limit),
            )
            rows = list(result.scalars().all())
            items = [
                WalterPassengerItem(
                    id=row.id,
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
            ]

        logger.info(
            "🤖 [WalterPgReader] read_passengers_page 완료 (Neon) — items=%s total=%s",
            len(items),
            total,
        )
        return items, total
