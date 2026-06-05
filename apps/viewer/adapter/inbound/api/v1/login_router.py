from __future__ import annotations

import logging

from fastapi import APIRouter

from viewer.adapter.inbound.api.schemas.login_schema import LoginSchema
from viewer.app.ports.input.login_use_case import LoginUseCase

login_router = APIRouter(prefix="/viewer/login", tags=["login"])
logger = logging.getLogger(__name__)
login_use_case: LoginUseCase | None = None


@login_router.post("/login", response_model=int)
async def login(request: LoginSchema) -> int:
    # 🎁로그 코드 시작
    logger.info("🤖 [LoginRouter] login 진입 — %s", request.log_summary())
    # 🎁로그 코드 끝
    if login_use_case is None:
        raise RuntimeError("LoginUseCase가 연결되지 않았습니다.")
    user_id = await login_use_case.login(request)
    # 🎁로그 코드 시작
    logger.info("🤖 [LoginRouter] login 완료 — user_id=%s", user_id)
    # 🎁로그 코드 끝
    return user_id

