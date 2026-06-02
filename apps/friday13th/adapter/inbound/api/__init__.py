from friday13th.adapter.inbound.api.v1 import login_router as login_router_module
from friday13th.adapter.inbound.api.v1 import signup_router as signup_router_module
from friday13th.adapter.inbound.api.v1.login_router import login_router
from friday13th.adapter.inbound.api.v1.signup_router import signup_router
from friday13th.adapter.outbound.pg.login_pg_repository import LoginPgRepository
from friday13th.adapter.outbound.pg.signup_pg_repository import SignupPgRepository
from friday13th.app.use_case.login_interactor import LoginInteractor
from friday13th.app.use_case.signup_interactor import SignupInteractor

login_router_module.login_use_case = LoginInteractor(LoginPgRepository())
signup_router_module.signup_use_case = SignupInteractor(SignupPgRepository())

__all__ = ["login_router", "signup_router"]
