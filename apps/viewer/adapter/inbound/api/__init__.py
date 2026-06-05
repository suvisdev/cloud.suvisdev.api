from __future__ import annotations

from viewer.adapter.inbound.api.v1 import login_router as login_router_module
from viewer.adapter.inbound.api.v1 import signup_router as signup_router_module

login_router = login_router_module.login_router
signup_router = signup_router_module.signup_router

__all__ = ["login_router", "signup_router"]
