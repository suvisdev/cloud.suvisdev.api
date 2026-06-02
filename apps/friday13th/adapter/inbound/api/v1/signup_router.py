from __future__ import annotations

import logging

from fastapi import APIRouter

from friday13th.adapter.inbound.api.schemas.signup_schema import SignupSchema
from friday13th.app.ports.input.signup_use_case import SignupUseCase

signup_router = APIRouter(prefix="/friday13th/signup", tags=["signup"])
logger = logging.getLogger(__name__)
signup_use_case: SignupUseCase | None = None

@signup_router.post("/signup", response_model=int)
async def signup(request: SignupSchema) -> int:
    # 🎁로그 코드 시작
    logger.info("🤖 [SignupRouter] signup 진입 — %s", request.log_summary())
    # 🎁로그 코드 끝
    if signup_use_case is None:
        raise RuntimeError("SignupUseCase가 연결되지 않았습니다.")
    user_id = await signup_use_case.signup(request)
    # 🎁로그 코드 시작
    logger.info("🤖 [SignupRouter] signup 완료 — user_id=%s", user_id)
    # 🎁로그 코드 끝
    return user_id



