import logging
import os

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

load_dotenv()

_session_factory = None
_init_error: str | None = None

Base = declarative_base()


def ensure_database() -> tuple[bool, str | None]:
    """엔진을 한 번만 만들고, (성공 여부, 실패 시 메시지)를 돌려준다. import 시에는 호출되지 않는다."""
    global _session_factory, _init_error
    if _session_factory is not None:
        return True, None
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        _init_error = (
            "DATABASE_URL 환경 변수가 없거나 비어 있습니다. "
            ".env에 Neon 연결 문자열을 설정하세요."
        )
        return False, _init_error
    try:
        engine = create_async_engine(url, echo=True)
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        _init_error = None
        return True, None
    except Exception as e:
        _init_error = str(e)
        logger.exception("DB 엔진 생성 실패")
        return False, _init_error


def get_session_factory():
    ok, err = ensure_database()
    if not ok or _session_factory is None:
        raise RuntimeError(err or "데이터베이스를 초기화할 수 없습니다.")
    return _session_factory


async def get_db():
    ok, err = ensure_database()
    if not ok:
        raise HTTPException(status_code=503, detail=err or "데이터베이스를 사용할 수 없습니다.")
    async with _session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            logger.exception("DB 세션 처리 중 오류가 발생했습니다.")
            raise
