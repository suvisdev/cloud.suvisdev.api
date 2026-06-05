from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from viewer.adapter.inbound.api.http_errors import invoke
from viewer.adapter.inbound.api.schemas.signup_schema import SignupSchema
from viewer.app.ports.input.signup_use_case import SignupUseCase
from viewer.dependencies.signup import SignupRepositoryError, get_signup_use_case

signup_router = APIRouter(prefix="/viewer/signup", tags=["signup"])
logger = logging.getLogger(__name__)
_REPO_ERRORS = (SignupRepositoryError,)


@signup_router.post("/signup", response_model=int)
async def signup(
    request: SignupSchema,
    signup: SignupUseCase = Depends(get_signup_use_case),
) -> int:
    logger.info("🤖 [SignupRouter] signup 진입 — %s", request.log_summary())
    result = await invoke(signup.signup(request), domain_errors=_REPO_ERRORS)
    logger.info("🤖 [SignupRouter] signup 완료 — user_id=%s", result.user_id)
    return result.user_id
