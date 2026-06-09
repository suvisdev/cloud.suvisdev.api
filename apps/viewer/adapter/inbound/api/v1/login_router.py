from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from viewer.adapter.inbound.api.schemas.login_schema import LoginSchema
from viewer.adapter.outbound.pg.login_pg_repository import LoginRepositoryError
from viewer.app.ports.input.login_use_case import LoginUseCase
from viewer.dependencies.login_provider import get_login_use_case

login_router = APIRouter(prefix="/login", tags=["login"])
logger = logging.getLogger(__name__)


@login_router.post("/login", response_model=int)
async def login(
    request: LoginSchema,
    login: LoginUseCase = Depends(get_login_use_case),
) -> int:
    logger.info("🤖 [LoginRouter] login 진입 — %s", request.log_summary())
    try:
        result = await login.login(request)
    except LoginRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    logger.info("🤖 [LoginRouter] login 완료 — user_id=%s", result.user_id)
    return result.user_id
