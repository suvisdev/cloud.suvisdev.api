from __future__ import annotations

import logging

from sqlalchemy import func, select

from core.database import get_mova_session_factory
from titanic.adapter.outbound.orm.james_orm_model import TitanicPassengerRow
from titanic.app.dtos.walter_dto import WalterPassengerItem

logger = logging.getLogger(__name__)


class WalterPgReader:
    """Titanic 승객 목록 조회용 PostgreSQL 아웃바운드 어댑터."""

    async def get_passengers(self, *, offset: int, limit: int) -> list[WalterPassengerItem]:
        logger.info(
            "[WalterPgReader] get_passengers 진입 (Neon) — offset=%s limit=%s",
            offset,
            limit,
        )
        factory = get_mova_session_factory()
        async with factory() as session:
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
                "[WalterPgReader] get_passengers 완료 (Neon) — items=%s",
                len(items),
            )
            return items

    async def get_total_count(self) -> int:
        logger.info("[WalterPgReader] get_total_count 진입 (Neon)")
        factory = get_mova_session_factory()
        async with factory() as session:
            result = await session.execute(select(func.count()).select_from(TitanicPassengerRow))
            total = int(result.scalar_one())
            logger.info("[WalterPgReader] get_total_count 완료 (Neon) — total=%s", total)
            return total
