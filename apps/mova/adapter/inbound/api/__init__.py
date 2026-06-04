from fastapi import APIRouter

from mova.adapter.inbound.api.v1.actors_router import actors_router
from mova.adapter.inbound.api.v1.characters_router import characters_router
from mova.adapter.inbound.api.v1.movies_router import movies_router
from mova.adapter.inbound.api.v1.reviews_router import reviews_router
from mova.adapter.inbound.api.v1.search_router import search_router
from mova.adapter.inbound.api.v1.tags_router import tags_router
from mova.adapter.inbound.api.v1.rankings_router import rankings_router
from mova.adapter.inbound.api.v1.movie_import_router import movie_import_router
from mova.adapter.inbound.api.v1.chat_router import chat_router

mova_router = APIRouter(prefix="/mova", tags=["mova"])
mova_router.include_router(movies_router)
mova_router.include_router(actors_router)
mova_router.include_router(characters_router)
mova_router.include_router(tags_router)
mova_router.include_router(reviews_router)
mova_router.include_router(search_router)
mova_router.include_router(rankings_router)
mova_router.include_router(movie_import_router)
mova_router.include_router(chat_router)

__all__ = ["mova_router"]
