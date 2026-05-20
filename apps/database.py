import logging
import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

_BACKEND_ENV = Path(__file__).resolve().parent.parent / ".env"

_session_factory: async_sessionmaker[AsyncSession] | None = None
_engine = None
_init_error: str | None = None
_active_db_url: str | None = None


def reload_env() -> None:
    """`backend/.env` 변경을 반영한다. (기존 프로세스에 남은 옛 DATABASE_URL 덮어쓰기)"""
    load_dotenv(_BACKEND_ENV, override=True)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 DeclarativeBase — 모든 ORM 모델이 상속한다."""

    pass


def _normalize_database_url(url: str) -> str:
    """Neon 등에서 받은 URL을 비동기 psycopg 드라이버 형식으로 맞춘다."""
    normalized = url.strip()
    if normalized.startswith("postgresql://") and "+psycopg" not in normalized:
        normalized = normalized.replace("postgresql://", "postgresql+psycopg://", 1)
    # psycopg 비동기에서 channel_binding=require 가 연결 실패를 유발하는 경우가 있음
    normalized = normalized.replace("&channel_binding=require", "").replace(
        "?channel_binding=require&", "?",
    ).replace("?channel_binding=require", "")
    return normalized


def ensure_database() -> tuple[bool, str | None]:
    """엔진·세션 팩토리를 한 번만 생성한다. `.env`의 DATABASE_URL 변경 시 재생성."""
    global _session_factory, _engine, _init_error, _active_db_url

    reload_env()
    raw_url = os.getenv("DATABASE_URL", "").strip()
    if not raw_url:
        _init_error = (
            "DATABASE_URL 환경 변수가 없거나 비어 있습니다. "
            "backend/.env 에 Neon(PostgreSQL) 연결 문자열을 설정하세요. "
            "예: postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require"
        )
        return False, _init_error

    url = _normalize_database_url(raw_url)
    if _session_factory is not None and _active_db_url == url:
        return True, None

    if _engine is not None and _active_db_url != url:
        logger.warning(
            "DATABASE_URL 변경 감지 (%s → %s) — DB 엔진 재초기화",
            urlparse(_active_db_url.replace("postgresql+psycopg://", "postgresql://")).username
            if _active_db_url
            else "?",
            urlparse(url.replace("postgresql+psycopg://", "postgresql://")).username,
        )
        _session_factory = None
        _engine = None

    try:
        parsed = urlparse(url.replace("postgresql+psycopg://", "postgresql://"))
        _engine = create_async_engine(url, echo=True)
        _session_factory = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        _active_db_url = url
        _init_error = None
        logger.info(
            "Neon(PostgreSQL) 비동기 엔진 초기화 — user=%s host=%s db=%s",
            parsed.username,
            parsed.hostname,
            (parsed.path or "").lstrip("/"),
        )
        return True, None
    except Exception as e:
        _init_error = str(e)
        _session_factory = None
        _engine = None
        _active_db_url = None
        logger.exception("DB 엔진 생성 실패")
        return False, _init_error


def get_engine():
    ok, err = ensure_database()
    if not ok or _engine is None:
        raise RuntimeError(err or "데이터베이스를 초기화할 수 없습니다.")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    ok, err = ensure_database()
    if not ok or _session_factory is None:
        raise RuntimeError(err or "데이터베이스를 초기화할 수 없습니다.")
    return _session_factory


async def get_db():
    """FastAPI Depends — 비동기 세션 yield."""
    ok, err = ensure_database()
    if not ok:
        raise HTTPException(
            status_code=503,
            detail=err or "데이터베이스를 사용할 수 없습니다.",
        )
    async with _session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            logger.exception("DB 세션 처리 중 오류가 발생했습니다.")
            raise


async def verify_connection() -> tuple[bool, str | None]:
    """실제 DB 연결 가능 여부 확인. 실패 시 엔진 상태를 초기화한다."""
    from sqlalchemy import text

    ok, err = ensure_database()
    if not ok:
        return False, err

    try:
        factory = get_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        msg = str(e)
        if "password authentication failed" in msg:
            msg = (
                "Neon DB 비밀번호 인증 실패입니다. "
                "Neon 콘솔에서 connection string을 복사해 backend/.env 의 "
                "DATABASE_URL 을 전체 교체하세요."
            )
        logger.exception("DB 연결 확인 실패")
        await dispose_engine()
        return False, msg


async def create_tables() -> None:
    """등록된 ORM 모델 기준으로 Neon(PostgreSQL)에 테이블을 생성한다."""
    engine = get_engine()
    import mova.app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("DB 테이블 생성 완료 (Neon/PostgreSQL)")


async def dispose_engine() -> None:
    """앱 종료 시 비동기 엔진·세션 팩토리를 정리한다."""
    global _session_factory, _engine, _init_error, _active_db_url
    if _engine is not None:
        await _engine.dispose()
    _session_factory = None
    _engine = None
    _init_error = None
    _active_db_url = None
