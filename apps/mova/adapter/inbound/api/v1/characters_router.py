from __future__ import annotations

from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.schemas.characters_schema import (
    CharacterLinkCreateSchema,
    CharacterLinkSchema,
    CharacterWithActorSchema,
    CharacterWithMovieSchema,
)
from mova.app.ports.input.characters_use_case import CharactersUseCase
from mova.dependencies.characters_provider import get_characters_use_case

characters_router = APIRouter(tags=["mova-characters"])


@characters_router.post("/characters", response_model=CharacterLinkSchema, status_code=201)
async def link_character(
    req: CharacterLinkCreateSchema,
    characters: CharactersUseCase = Depends(get_characters_use_case),
) -> CharacterLinkSchema:
    return (await characters.link(req)).to_schema()


@characters_router.delete("/characters/{link_id}", status_code=204)
async def unlink_character(
    link_id: int,
    characters: CharactersUseCase = Depends(get_characters_use_case),
) -> None:
    await characters.unlink(link_id)


@characters_router.get("/characters", response_model=list[CharacterLinkSchema])
async def list_character_links(
    movie_id: int | None = None,
    actor_id: int | None = None,
    limit: int = 100,
    characters: CharactersUseCase = Depends(get_characters_use_case),
) -> list[CharacterLinkSchema]:
    rows = await characters.list_links(movie_id=movie_id, actor_id=actor_id, limit=limit)
    return [row.to_schema() for row in rows]


@characters_router.get(
    "/movies/{movie_id}/characters",
    response_model=list[CharacterWithActorSchema],
)
async def list_characters_by_movie(
    movie_id: int,
    limit: int = 100,
    characters: CharactersUseCase = Depends(get_characters_use_case),
) -> list[CharacterWithActorSchema]:
    rows = await characters.list_actors_by_movie(movie_id, limit=limit)
    return [row.to_schema() for row in rows]


@characters_router.get(
    "/actors/{actor_id}/movies",
    response_model=list[CharacterWithMovieSchema],
)
async def list_movies_by_actor(
    actor_id: int,
    limit: int = 100,
    characters: CharactersUseCase = Depends(get_characters_use_case),
) -> list[CharacterWithMovieSchema]:
    rows = await characters.list_movies_by_actor(actor_id, limit=limit)
    return [row.to_schema() for row in rows]
