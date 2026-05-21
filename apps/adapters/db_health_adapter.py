"""Neon/PostgreSQL 연결 확인용 어댑터."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import (
    ensure_mova_database,
    ensure_secom_database,
    get_mova_session_factory,
    get_secom_session_factory,
)

MOVA_TABLE_CHECKS: tuple[str, ...] = (
    "movies",
    "actors",
    "characters",
    "tags",
    "rankings",
    "chat",
    "reviews",
)

SECOM_TABLE_CHECKS: tuple[str, ...] = (
    "user_groups",
    "users",
)


class DbHealthAdapter:
    @staticmethod
    async def neon_time_check(db: AsyncSession) -> dict:
        return await DbHealthAdapter._run_now(db)

    @staticmethod
    async def check_neon() -> dict:
        ok, err = ensure_mova_database()
        if not ok:
            return {"status": "error", "message": err or "데이터베이스를 사용할 수 없습니다."}

        factory = get_mova_session_factory()
        async with factory() as session:
            return await DbHealthAdapter._run_now(session)

    @staticmethod
    async def _count_table(session: AsyncSession, table: str) -> dict:
        try:
            result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            return {"status": "ok", "count": result.scalar_one()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    async def check_all_domains(db: AsyncSession) -> dict:
        """Mova·Secom DB 테이블 접근 확인."""
        ping = await DbHealthAdapter._run_now(db)
        if ping.get("status") != "success":
            return ping

        domains: dict[str, dict] = {"mova": {}, "secom": {}}

        for table in MOVA_TABLE_CHECKS:
            domains["mova"][table] = await DbHealthAdapter._count_table(db, table)

        ok_secom, err_secom = ensure_secom_database()
        if ok_secom:
            async with get_secom_session_factory() as secom_session:
                for table in SECOM_TABLE_CHECKS:
                    domains["secom"][table] = await DbHealthAdapter._count_table(
                        secom_session,
                        table,
                    )
        else:
            domains["secom"]["_connection"] = {"status": "error", "message": err_secom}

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
        ok, err = ensure_mova_database()
        if not ok:
            return {"status": "error", "message": err or "데이터베이스를 사용할 수 없습니다."}

        async with get_mova_session_factory() as session:
            return await DbHealthAdapter.check_all_domains(session)

    @staticmethod
    async def _run_now(session: AsyncSession) -> dict:
        try:
            result = await session.execute(text("SELECT NOW();"))
            now = result.scalar_one()
            return {"status": "success", "neon_time": str(now)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
