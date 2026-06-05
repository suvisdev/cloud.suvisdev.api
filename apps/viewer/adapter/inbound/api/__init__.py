from __future__ import annotations

from viewer.adapter.inbound.api.v1 import login_router as login_router_module
from viewer.adapter.inbound.api.v1 import signup_router as signup_router_module
from viewer.adapter.outbound.pg.login_pg_repository import LoginPgRepository
from viewer.adapter.outbound.pg.signup_pg_repository import SignupPgRepository
from viewer.app.use_cases.login_interactor import LoginInteractor
from viewer.app.use_cases.signup_interactor import SignupInteractor

login_router_module.login_use_case = LoginInteractor(LoginPgRepository())
signup_router_module.signup_use_case = SignupInteractor(SignupPgRepository())

login_router = login_router_module.login_router
signup_router = signup_router_module.signup_router

__all__ = ["login_router", "signup_router"]
