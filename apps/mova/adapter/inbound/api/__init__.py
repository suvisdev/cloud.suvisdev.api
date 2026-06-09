from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import APIRouter

__all__ = ["mova_router"]


def __getattr__(name: str) -> APIRouter:
    if name == "mova_router":
        from fastapi import APIRouter

        from mova.adapter.inbound.api.v1.actors_router import actors_router
        from mova.adapter.inbound.api.v1.characters_router import characters_router
        from mova.adapter.inbound.api.v1.chat_router import chat_router
        from mova.adapter.inbound.api.v1.movie_import_router import movie_import_router
        from mova.adapter.inbound.api.v1.movies_router import movies_router
        from mova.adapter.inbound.api.v1.rankings_router import rankings_router
        from mova.adapter.inbound.api.v1.reviews_router import reviews_router
        from mova.adapter.inbound.api.v1.search_router import search_router
        from mova.adapter.inbound.api.v1.tags_router import tags_router

        router = APIRouter(prefix="/mova", tags=["mova"])
        router.include_router(movies_router)
        router.include_router(actors_router)
        router.include_router(characters_router)
        router.include_router(tags_router)
        router.include_router(reviews_router)
        router.include_router(search_router)
        router.include_router(rankings_router)
        router.include_router(movie_import_router)
        router.include_router(chat_router)
        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
