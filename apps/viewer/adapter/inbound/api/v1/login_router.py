from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from viewer.adapter.inbound.api.http_errors import invoke
from viewer.adapter.inbound.api.schemas.login_schema import LoginSchema
from viewer.app.ports.input.login_use_case import LoginUseCase
from viewer.dependencies.login import LoginRepositoryError, get_login_use_case

login_router = APIRouter(prefix="/viewer/login", tags=["login"])
logger = logging.getLogger(__name__)
_REPO_ERRORS = (LoginRepositoryError,)


@login_router.post("/login", response_model=int)
async def login(
    request: LoginSchema,
    login: LoginUseCase = Depends(get_login_use_case),
) -> int:
    logger.info("🤖 [LoginRouter] login 진입 — %s", request.log_summary())
    result = await invoke(login.login(request), domain_errors=_REPO_ERRORS)
    logger.info("🤖 [LoginRouter] login 완료 — user_id=%s", result.user_id)
    return result.user_id
