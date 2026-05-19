import logging
import os

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

load_dotenv()

_session_factory: async_sessionmaker[AsyncSession] | None = None
_engine = None
_init_error: str | None = None


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 DeclarativeBase — 모든 ORM 모델이 상속한다."""

    pass


def _normalize_database_url(url: str) -> str:
    """Neon 등에서 받은 URL을 비동기 psycopg 드라이버 형식으로 맞춘다."""
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def ensure_database() -> tuple[bool, str | None]:
    """엔진·세션 팩토리를 한 번만 생성한다."""
    global _session_factory, _engine, _init_error
    if _session_factory is not None:
        return True, None

    raw_url = os.getenv("DATABASE_URL", "").strip()
    if not raw_url:
        _init_error = (
            "DATABASE_URL 환경 변수가 없거나 비어 있습니다. "
            "backend/.env 에 Neon(PostgreSQL) 연결 문자열을 설정하세요. "
            "예: postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require"
        )
        return False, _init_error

    url = _normalize_database_url(raw_url)
    try:
        _engine = create_async_engine(url, echo=True)
        _session_factory = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        _init_error = None
        logger.info("Neon(PostgreSQL) 비동기 엔진 초기화 완료")
        return True, None
    except Exception as e:
        _init_error = str(e)
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


async def create_tables() -> None:
    """등록된 ORM 모델 기준으로 Neon(PostgreSQL)에 테이블을 생성한다."""
    engine = get_engine()
    import mova.app.models  # noqa: F401
    import secom.app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("DB 테이블 생성 완료 (Neon/PostgreSQL)")


async def dispose_engine() -> None:
    """앱 종료 시 비동기 엔진·세션 팩토리를 정리한다."""
    global _session_factory, _engine, _init_error
    if _engine is not None:
        await _engine.dispose()
    _session_factory = None
    _engine = None
    _init_error = None
