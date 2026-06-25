"""인바운드 예외 핸들러 — 도메인 예외를 HTTP 응답으로 변환하는 유일한 지점.

LLM 아웃바운드 어댑터는 ``mova.app.exceptions.LLMError`` 만 던지고, HTTP 상태코드
결정은 여기 한 곳에서만 이뤄진다. ``gemini_reply`` 호출 경로(mova chat·main /chat·
titanic)가 모두 동일 FastAPI 앱이므로 앱 전역 핸들러 하나로 일관되게 처리된다.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from mova.app.exceptions import LLMError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(LLMError)
    async def _llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
