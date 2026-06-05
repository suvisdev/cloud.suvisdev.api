from __future__ import annotations

from collections.abc import Awaitable
from typing import TypeVar

from fastapi import HTTPException

T = TypeVar("T")


def _status_code(exc: Exception, default: int = 400) -> int:
    code = getattr(exc, "status_code", default)
    return int(code) if code else default


def _detail(exc: Exception) -> str:
    message = getattr(exc, "message", None)
    return message if message else str(exc)


async def invoke(
    coro: Awaitable[T],
    *,
    domain_errors: tuple[type[Exception], ...] = (),
    chat: bool = False,
) -> T:
    """Use case 호출 — Repository/Adapter·RuntimeError를 HTTPException으로 변환."""
    try:
        return await coro
    except HTTPException:
        raise
    except domain_errors as e:
        raise HTTPException(status_code=_status_code(e), detail=_detail(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        if chat:
            raise HTTPException(
                status_code=502,
                detail="추천 응답을 만들지 못했습니다. 잠시 후 다시 시도하세요.",
            ) from e
        raise
