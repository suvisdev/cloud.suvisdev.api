from __future__ import annotations

from fastapi import APIRouter

__all__ = ["dispatch_router"]


def __getattr__(name: str) -> APIRouter:
    if name == "dispatch_router":
        from dispatch.adapter.inbound.api.v1.email_router import email_router

        router = APIRouter(prefix="/dispatch", tags=["dispatch"])
        router.include_router(email_router)
        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
