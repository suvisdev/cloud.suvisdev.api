"""Neon PostgreSQL — Mova·Secom·Titanic ORM 연결 (SQLAlchemy 2.0 async)."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

_BACKEND_ENV = Path(__file__).resolve().parent.parent / ".env"

_mova_session_factory: async_sessionmaker[AsyncSession] | None = None
_secom_session_factory: async_sessionmaker[AsyncSession] | None = None
_mova_engine = None
_secom_engine = None
_mova_init_error: str | None = None
_secom_init_error: str | None = None
_active_mova_url: str | None = None
_active_secom_url: str | None = None


def reload_env() -> None:
    """`backend/.env` 변경을 반영한다."""
    load_dotenv(_BACKEND_ENV, override=True)


class MovaBase(DeclarativeBase):
    """Mova ORM (movies, rankings, …)."""

    pass


class SecomBase(DeclarativeBase):
    """Secom ORM (users, members, groups — 회원·로그인)."""

    pass


class TitanicBase(DeclarativeBase):
    """Titanic James CSV 업로드 ORM."""

    pass


# Mova 모델 호환
Base = MovaBase


def _normalize_database_url(url: str) -> str:
    normalized = url.strip()
    if normalized.startswith("postgresql://") and "+psycopg" not in normalized:
        normalized = normalized.replace("postgresql://", "postgresql+psycopg://", 1)
    normalized = normalized.replace("&channel_binding=require", "").replace(
        "?channel_binding=require&",
        "?",
    ).replace("?channel_binding=require", "")
    return normalized


def _resolve_mova_url() -> str:
    return _normalize_database_url(
        (os.getenv("MOVA_DATABASE_URL") or os.getenv("DATABASE_URL") or "").strip(),
    )


def _resolve_secom_url() -> str:
    explicit = (os.getenv("SECOM_DATABASE_URL") or "").strip()
    if explicit:
        return _normalize_database_url(explicit)
    return _resolve_mova_url()


def _init_engine(
    *,
    url: str,
    label: str,
    active_url: str | None,
    engine,
    factory: async_sessionmaker[AsyncSession] | None,
) -> tuple[object | None, async_sessionmaker[AsyncSession] | None, str | None, str | None]:
    if not url:
        return None, None, (
            f"{label} URL이 없습니다. backend/.env 에 "
            f"{'SECOM_DATABASE_URL' if label == 'Secom' else 'MOVA_DATABASE_URL 또는 DATABASE_URL'} "
            "을 설정하세요."
        ), None

    if factory is not None and active_url == url:
        return engine, factory, None, url

    if engine is not None and active_url != url:
        logger.warning("%s DB URL 변경 — 엔진 재초기화", label)

    try:
        parsed = urlparse(url.replace("postgresql+psycopg://", "postgresql://"))
        new_engine = create_async_engine(url, echo=False)
        new_factory = async_sessionmaker(
            bind=new_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info(
            "%s DB 엔진 — user=%s host=%s db=%s",
            label,
            parsed.username,
            parsed.hostname,
            (parsed.path or "").lstrip("/"),
        )
        return new_engine, new_factory, None, url
    except Exception as e:
        logger.exception("%s DB 엔진 생성 실패", label)
        return None, None, str(e), None


def ensure_mova_database() -> tuple[bool, str | None]:
    global _mova_session_factory, _mova_engine, _mova_init_error, _active_mova_url
    reload_env()
    engine, factory, err, active = _init_engine(
        url=_resolve_mova_url(),
        label="Mova",
        active_url=_active_mova_url,
        engine=_mova_engine,
        factory=_mova_session_factory,
    )
    _mova_engine, _mova_session_factory, _mova_init_error, _active_mova_url = (
        engine,
        factory,
        err,
        active,
    )
    return factory is not None, err


def ensure_secom_database() -> tuple[bool, str | None]:
    global _secom_session_factory, _secom_engine, _secom_init_error, _active_secom_url
    reload_env()
    engine, factory, err, active = _init_engine(
        url=_resolve_secom_url(),
        label="Secom",
        active_url=_active_secom_url,
        engine=_secom_engine,
        factory=_secom_session_factory,
    )
    _secom_engine, _secom_session_factory, _secom_init_error, _active_secom_url = (
        engine,
        factory,
        err,
        active,
    )
    return factory is not None, err


def ensure_database() -> tuple[bool, str | None]:
    """Mova DB 연결 (기존 호환)."""
    return ensure_mova_database()


def get_mova_engine():
    ok, err = ensure_mova_database()
    if not ok or _mova_engine is None:
        raise RuntimeError(err or "Mova DB를 초기화할 수 없습니다.")
    return _mova_engine


def get_secom_engine():
    ok, err = ensure_secom_database()
    if not ok or _secom_engine is None:
        raise RuntimeError(err or "Secom DB를 초기화할 수 없습니다.")
    return _secom_engine


def get_mova_session_factory() -> async_sessionmaker[AsyncSession]:
    ok, err = ensure_mova_database()
    if not ok or _mova_session_factory is None:
        raise RuntimeError(err or "Mova DB를 초기화할 수 없습니다.")
    return _mova_session_factory


def get_secom_session_factory() -> async_sessionmaker[AsyncSession]:
    ok, err = ensure_secom_database()
    if not ok or _secom_session_factory is None:
        raise RuntimeError(err or "Secom DB를 초기화할 수 없습니다.")
    return _secom_session_factory


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Mova 리포지토리용 (기존 호환)."""
    return get_mova_session_factory()


def get_engine():
    return get_mova_engine()


async def get_mova_db():
    ok, err = ensure_mova_database()
    if not ok:
        raise HTTPException(status_code=503, detail=err or "Mova DB를 사용할 수 없습니다.")
    async with _mova_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            logger.exception("Mova DB 세션 오류")
            raise


async def get_secom_db():
    ok, err = ensure_secom_database()
    if not ok:
        raise HTTPException(status_code=503, detail=err or "Secom DB를 사용할 수 없습니다.")
    async with _secom_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            logger.exception("Secom DB 세션 오류")
            raise


async def get_db():
    """FastAPI Depends — Mova 세션."""
    async for session in get_mova_db():
        yield session


async def verify_connection() -> tuple[bool, str | None]:
    from sqlalchemy import text as sql_text

    ok_mova, err_mova = ensure_mova_database()
    if not ok_mova:
        return False, err_mova
    try:
        async with _mova_session_factory() as session:
            await session.execute(sql_text("SELECT 1"))
    except Exception as e:
        msg = str(e)
        if "password authentication failed" in msg:
            msg = "Mova DB 비밀번호 인증 실패 — MOVA_DATABASE_URL / DATABASE_URL 확인"
        logger.exception("Mova DB 연결 확인 실패")
        await dispose_engine()
        return False, msg

    ok_secom, err_secom = ensure_secom_database()
    if not ok_secom:
        return False, err_secom
    try:
        async with _secom_session_factory() as session:
            await session.execute(sql_text("SELECT 1"))
        return True, None
    except Exception as e:
        logger.exception("Secom DB 연결 확인 실패")
        await dispose_engine()
        return False, str(e)


async def _drop_legacy_mova_users_table(conn) -> None:
    """Mova 취향용 users( preferred_genres )가 남아 있으면 Secom users 생성을 막으므로 제거."""
    result = await conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = 'users'"
        ),
    )
    columns = {row[0] for row in result.fetchall()}
    if not columns:
        return
    if "user_group_id" in columns:
        return
    if "preferred_genres" in columns or "nickname" in columns:
        logger.warning("레거시 Mova users 테이블 제거 — Secom users 로 교체")
        await conn.execute(text('DROP TABLE IF EXISTS "users" CASCADE'))


async def create_tables() -> None:
    """Mova·Friday13th·Titanic ORM 테이블을 Neon에 생성."""
    import mova.app.models  # noqa: F401
    import titanic.adapter.outbound.orm.james_orm_model  # noqa: F401

    mova_engine = get_mova_engine()
    async with mova_engine.begin() as conn:
        await conn.run_sync(MovaBase.metadata.create_all)
        await conn.run_sync(TitanicBase.metadata.create_all)
    logger.info("Mova/Titanic DB 테이블 생성 완료")

    try:
        import friday13th.app.models  # noqa: F401
    except ModuleNotFoundError:
        logger.warning("friday13th 패키지 없음 — Secom 테이블 생성 생략")
        return

    secom_engine = get_secom_engine()
    async with secom_engine.begin() as conn:
        await _drop_legacy_mova_users_table(conn)
        await conn.run_sync(SecomBase.metadata.create_all)
    logger.info("Secom DB 테이블 생성 완료")


async def dispose_engine() -> None:
    global _mova_session_factory
    global _mova_engine
    global _mova_init_error
    global _active_mova_url
    global _secom_session_factory
    global _secom_engine
    global _secom_init_error
    global _active_secom_url
    if _mova_engine is not None:
        await _mova_engine.dispose()
    if _secom_engine is not None and _secom_engine is not _mova_engine:
        await _secom_engine.dispose()
    _mova_session_factory = None
    _mova_engine = None
    _mova_init_error = None
    _active_mova_url = None
    _secom_session_factory = None
    _secom_engine = None
    _secom_init_error = None
    _active_secom_url = None
