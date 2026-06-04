from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from mova.adapter.inbound.api.schemas.characters_schema import (
    CharacterLinkCreateSchema,
    CharacterLinkSchema,
    CharacterWithActorSchema,
    CharacterWithMovieSchema,
)
from mova.adapter.outbound.pg.characters_pg_repository import CharactersRepositoryError
from mova.app.ports.input.characters_use_case import CharactersUseCase
from mova.app.use_cases.characters_interactor import CharactersInteractor

characters_router = APIRouter(tags=["mova-characters"])

logger = logging.getLogger(__name__)


@characters_router.post("/characters", response_model=CharacterLinkSchema, status_code=201)
async def link_character(req: CharacterLinkCreateSchema) -> CharacterLinkSchema:
    logger.info(
        "[CharactersRouter] link — movie_id=%s actor_id=%s",
        req.movie_id,
        req.actor_id,
    )
    use_case: CharactersUseCase = CharactersInteractor()
    try:
        return await use_case.link(req)
    except CharactersRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@characters_router.delete("/characters/{link_id}", status_code=204)
async def unlink_character(link_id: int) -> None:
    use_case: CharactersUseCase = CharactersInteractor()
    try:
        await use_case.unlink(link_id)
    except CharactersRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@characters_router.get("/characters", response_model=list[CharacterLinkSchema])
async def list_character_links(
    movie_id: int | None = None,
    actor_id: int | None = None,
    limit: int = 100,
) -> list[CharacterLinkSchema]:
    use_case: CharactersUseCase = CharactersInteractor()
    try:
        return await use_case.list_links(
            movie_id=movie_id,
            actor_id=actor_id,
            limit=limit,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@characters_router.get(
    "/movies/{movie_id}/characters",
    response_model=list[CharacterWithActorSchema],
)
async def list_characters_by_movie(
    movie_id: int,
    limit: int = 100,
) -> list[CharacterWithActorSchema]:
    use_case: CharactersUseCase = CharactersInteractor()
    try:
        return await use_case.list_actors_by_movie(movie_id, limit=limit)
    except CharactersRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@characters_router.get(
    "/actors/{actor_id}/movies",
    response_model=list[CharacterWithMovieSchema],
)
async def list_movies_by_actor(
    actor_id: int,
    limit: int = 100,
) -> list[CharacterWithMovieSchema]:
    use_case: CharactersUseCase = CharactersInteractor()
    try:
        return await use_case.list_movies_by_actor(actor_id, limit=limit)
    except CharactersRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
