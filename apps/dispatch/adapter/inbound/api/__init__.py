from __future__ import annotations

from fastapi import APIRouter

__all__ = ["dispatch_router"]


def __getattr__(name: str) -> APIRouter:
    if name == "dispatch_router":
        from dispatch.adapter.inbound.api.v1.adress_router import adress_router
        from dispatch.adapter.inbound.api.v1.discord_router import discord_router
        from dispatch.adapter.inbound.api.v1.email_router import email_router
        from dispatch.adapter.inbound.api.v1.save_router import inbox_router
        from dispatch.adapter.inbound.api.v1.telegram_router import telegram_router

        router = APIRouter(prefix="/dispatch", tags=["dispatch"])
        router.include_router(email_router)
        router.include_router(adress_router)
        router.include_router(discord_router)
        router.include_router(telegram_router)
        router.include_router(inbox_router)
        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
