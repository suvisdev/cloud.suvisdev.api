"""Neon/PostgreSQL 연결 확인용 어댑터."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import ensure_database, get_session_factory


class DbHealthAdapter:
    @staticmethod
    async def neon_time_check(db: AsyncSession) -> dict:
        """FastAPI `Depends(get_db)` 로 주입된 세션으로 시각을 조회한다."""
        return await DbHealthAdapter._run_now(db)

    @staticmethod
    async def check_neon() -> dict:
        ok, err = ensure_database()
        if not ok:
            return {"status": "error", "message": err or "데이터베이스를 사용할 수 없습니다."}

        factory = get_session_factory()
        async with factory() as session:
            return await DbHealthAdapter._run_now(session)

    @staticmethod
    async def _run_now(session: AsyncSession) -> dict:
        try:
            result = await session.execute(text("SELECT NOW();"))
            now = result.scalar_one()
            return {"status": "success", "neon_time": str(now)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
