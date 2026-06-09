"""Neon PostgreSQL — Mova·Secom·Titanic ORM 연결 (SQLAlchemy 2.0 최신 비동기)."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from urllib.parse import urlparse
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_ENV = _BACKEND_ROOT / ".env"

# 타입 명시 강화
_mova_engine: AsyncEngine | None = None
_secom_engine: AsyncEngine | None = None
_mova_session_factory: async_sessionmaker[AsyncSession] | None = None
_secom_session_factory: async_sessionmaker[AsyncSession] | None = None

_mova_init_error: str | None = None
_secom_init_error: str | None = None
_active_mova_url: str | None = None
_active_secom_url: str | None = None


def reload_env() -> None:
    load_dotenv(_BACKEND_ENV, override=True)


class MovaBase(DeclarativeBase):
    """Mova ORM (movies, rankings, …)."""
    pass


class SecomBase(DeclarativeBase):
    """Secom ORM (groups, admins, users)."""
    pass


class TitanicBase(DeclarativeBase):
    """Titanic James CSV 업로드 ORM."""
    pass


# Mova 모델 호환용
Base = MovaBase


def _normalize_database_url(url: str) -> str:
    normalized = url.strip()
    if normalized.startswith("postgresql://") and "+psycopg" not in normalized:
        normalized = normalized.replace("postgresql://", "postgresql+psycopg://", 1)
    
    # Neon/PostgreSQL 특유의 쿼리 파라미터 정리
    for param in ["channel_binding=require", "channel_binding=require&", "?channel_binding=require"]:
        normalized = normalized.replace(param, "")
    return normalized.rstrip("?")


def _init_engine(
    url: str,
    label: str,
    active_url: str | None,
) -> tuple[AsyncEngine | None, async_sessionmaker[AsyncSession] | None, str | None, str | None]:
    if not url:
        return None, None, f"{label} URL이 설정되지 않았습니다.", None

    # URL이 같으면 기존 엔진 유지
    # (이미 전역변수에 할당된 상태에서 호출되므로 엔진을 여기서 생성할지 결정)
    
    try:
        parsed = urlparse(url.replace("postgresql+psycopg://", "postgresql://"))
        
        # SQLAlchemy 2.0 비동기 엔진
        new_engine = create_async_engine(
            url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
        )

        new_factory = async_sessionmaker(
            bind=new_engine,
            expire_on_commit=False,
            autoflush=False,
        )
        
        logger.info("%s DB 엔진 초기화 성공: host=%s", label, parsed.hostname)
        return new_engine, new_factory, None, url
        
    except Exception as e:
        logger.exception("%s DB 엔진 생성 실패", label)
        return None, None, str(e), None


def ensure_mova_database() -> tuple[bool, str | None]:
    global _mova_session_factory, _mova_engine, _mova_init_error, _active_mova_url
    url = _normalize_database_url(os.getenv("MOVA_DATABASE_URL") or os.getenv("DATABASE_URL") or "")
    
    if _mova_session_factory is not None and _active_mova_url == url:
        return True, None

    reload_env()
    engine, factory, err, active = _init_engine(url, "Mova", _active_mova_url)
    _mova_engine, _mova_session_factory, _mova_init_error, _active_mova_url = engine, factory, err, active
    return factory is not None, err


def ensure_secom_database() -> tuple[bool, str | None]:
    global _secom_session_factory, _secom_engine, _secom_init_error, _active_secom_url
    reload_env()
    explicit_url = (os.getenv("SECOM_DATABASE_URL") or "").strip()
    if explicit_url:
        url = _normalize_database_url(explicit_url)
    else:
        url = _normalize_database_url(
            os.getenv("MOVA_DATABASE_URL") or os.getenv("DATABASE_URL") or "",
        )

    if _secom_session_factory is not None and _active_secom_url == url:
        return True, None

    engine, factory, err, active = _init_engine(url, "Secom", _active_secom_url)
    _secom_engine, _secom_session_factory, _secom_init_error, _active_secom_url = engine, factory, err, active
    return factory is not None, err


# --- Dependency Injections (FastAPI) ---

async def get_mova_db() -> AsyncGenerator[AsyncSession, None]:
    ok, err = ensure_mova_database()
    if not ok or _mova_session_factory is None:
        raise HTTPException(status_code=503, detail=err)
    
    async with _mova_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_secom_db() -> AsyncGenerator[AsyncSession, None]:
    ok, err = ensure_secom_database()
    if not ok or _secom_session_factory is None:
        raise HTTPException(status_code=503, detail=err)
    
    async with _secom_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# --- Legacy Compatibility ---

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_mova_db():
        yield session


def get_mova_engine() -> AsyncEngine | None:
    ensure_mova_database()
    return _mova_engine


def get_secom_engine() -> AsyncEngine | None:
    ensure_secom_database()
    return _secom_engine


def get_engine() -> AsyncEngine | None:
    return get_mova_engine()


def get_mova_session_factory() -> async_sessionmaker[AsyncSession]:
    ok, err = ensure_mova_database()
    if not ok or _mova_session_factory is None:
        raise RuntimeError(err or "Mova database not initialized")
    return _mova_session_factory


def get_secom_session_factory() -> async_sessionmaker[AsyncSession]:
    ok, err = ensure_secom_database()
    if not ok or _secom_session_factory is None:
        raise RuntimeError(err or "Secom database not initialized")
    return _secom_session_factory


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return get_mova_session_factory()


async def verify_connection() -> tuple[bool, str | None]:
    ok, err = ensure_mova_database()
    if not ok or _mova_session_factory is None:
        return False, err or "Mova database not initialized"
    try:
        async with _mova_session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        return False, str(e)

    ok_secom, err_secom = ensure_secom_database()
    if not ok_secom or _secom_session_factory is None:
        return False, err_secom or "Secom database not initialized"
    try:
        async with _secom_session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        return False, str(e)

    return True, None


# --- Schema Management (2.0 Style) ---

async def _drop_legacy_mova_users_table(conn) -> None:
    # 2.0 스타일의 결과 집합 처리
    query = text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'users'"
    )
    result = await conn.execute(query)
    columns = {row.column_name for row in result.mappings()} # mappings() 사용 권장
    
    if not columns or "user_group_id" in columns:
        return
    if "group_id" in columns or "role" in columns:
        return
    if "preferred_genres" in columns or "nickname" in columns:
        logger.warning("Legacy Mova users table detected. Dropping for Secom integration.")
        await conn.execute(text('DROP TABLE IF EXISTS "users" CASCADE'))


async def create_tables() -> None:
    """SQLAlchemy 2.0 방식의 테이블 일괄 생성."""
    await ensure_titanic_tables()
    import mova.adapter.outbound.orm  # noqa: F401

    try:
        import viewer.adapter.outbound.orm.admin_orm  # noqa: F401
        import viewer.adapter.outbound.orm.group_orm  # noqa: F401
        import viewer.adapter.outbound.orm.user_orm  # noqa: F401
        secom_engine = get_secom_engine()
        if secom_engine:
            async with secom_engine.begin() as conn:
                await _drop_legacy_mova_users_table(conn)
                await conn.run_sync(SecomBase.metadata.create_all)
    except ModuleNotFoundError:
        logger.warning("Viewer models not found.")

    mova_engine = get_mova_engine()
    if mova_engine:
        async with mova_engine.begin() as conn:
            await conn.run_sync(MovaBase.metadata.create_all)


async def ensure_titanic_tables() -> None:
    """passengers·bookings 없으면 생성 (삭제 후 업로드 복구용)."""
    from core.matrix.grid_neo_theone_base import Base

    import titanic.adapter.outbound.orm.passenger_rose_model_orm  # noqa: F401
    import titanic.adapter.outbound.orm.passenger_jack_trainer_orm  # noqa: F401

    ok, err = ensure_mova_database()
    if not ok:
        raise RuntimeError(err or "Mova database not initialized")

    engine = get_mova_engine()
    if engine is None:
        raise RuntimeError("Mova engine not initialized")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def dispose_engine() -> None:
    global _mova_engine, _secom_engine, _mova_session_factory, _secom_session_factory
    if _mova_engine is not None:
        await _mova_engine.dispose()
    if _secom_engine is not None:
        await _secom_engine.dispose()
    _mova_engine = None
    _secom_engine = None
    _mova_session_factory = None
    _secom_session_factory = None