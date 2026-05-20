"""Neon/PostgreSQL 연결 확인용 어댑터."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import ensure_database, get_session_factory

# Mova 도메인 테이블 (접두어 mova_ 제거)
DOMAIN_TABLE_CHECKS: tuple[tuple[str, str], ...] = (
    ("mova", "movies"),
    ("mova", "actors"),
    ("mova", "movie_characters"),
    ("mova", "tags"),
    ("mova", "movie_tags"),
    ("mova", "rankings"),
    ("mova", "chat_intents"),
    ("mova", "users"),
    ("mova", "interactions"),
    ("mova", "reviews"),
)


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
    async def check_all_domains(db: AsyncSession) -> dict:
        """Neon DB 내 Mova 테이블 접근 확인."""
        ping = await DbHealthAdapter._run_now(db)
        if ping.get("status") != "success":
            return ping

        domains: dict[str, dict] = {}
        for domain, table in DOMAIN_TABLE_CHECKS:
            try:
                result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar_one()
                domains.setdefault(domain, {})[table] = {"status": "ok", "count": count}
            except Exception as e:
                domains.setdefault(domain, {})[table] = {
                    "status": "error",
                    "message": str(e),
                }

        failed = [
            f"{domain}.{table}"
            for domain, tables in domains.items()
            for table, info in tables.items()
            if info.get("status") != "ok"
        ]
        return {
            "status": "success" if not failed else "partial",
            "neon_time": ping.get("neon_time"),
            "domains": domains,
            "failed": failed,
        }

    @staticmethod
    async def check_all_domains_standalone() -> dict:
        ok, err = ensure_database()
        if not ok:
            return {"status": "error", "message": err or "데이터베이스를 사용할 수 없습니다."}

        factory = get_session_factory()
        async with factory() as session:
            return await DbHealthAdapter.check_all_domains(session)

    @staticmethod
    async def _run_now(session: AsyncSession) -> dict:
        try:
            result = await session.execute(text("SELECT NOW();"))
            now = result.scalar_one()
            return {"status": "success", "neon_time": str(now)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
