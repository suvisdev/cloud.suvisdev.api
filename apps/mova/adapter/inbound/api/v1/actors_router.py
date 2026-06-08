from __future__ import annotations

from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.http_errors import invoke
from mova.adapter.inbound.api.schemas.actors_schema import ActorCreateSchema, ActorSchema
from mova.adapter.outbound.pg.actors_pg_repository import ActorsRepositoryError
from mova.app.ports.input.actors_use_case import ActorsUseCase
from mova.dependencies.actors_provider import get_actors_use_case

actors_router = APIRouter(tags=["mova-actors"])
_REPO_ERRORS = (ActorsRepositoryError,)


@actors_router.post("/actors", response_model=ActorSchema, status_code=201)
async def save_actor(
    req: ActorCreateSchema,
    actors: ActorsUseCase = Depends(get_actors_use_case),
) -> ActorSchema:
    return (await invoke(actors.save_actor(req), domain_errors=_REPO_ERRORS)).to_schema()


@actors_router.get("/actors", response_model=list[ActorSchema])
async def list_actors(
    limit: int = 100,
    actors: ActorsUseCase = Depends(get_actors_use_case),
) -> list[ActorSchema]:
    rows = await invoke(actors.list_actors(limit=limit))
    return [row.to_schema() for row in rows]


@actors_router.post("/actors/names", response_model=ActorSchema, status_code=201)
async def save_actor_name(
    req: ActorCreateSchema,
    actors: ActorsUseCase = Depends(get_actors_use_case),
) -> ActorSchema:
    return (await invoke(actors.save_name(req), domain_errors=_REPO_ERRORS)).to_schema()


@actors_router.get("/actors/names", response_model=list[ActorSchema])
async def list_actor_names(
    limit: int = 100,
    actors: ActorsUseCase = Depends(get_actors_use_case),
) -> list[ActorSchema]:
    rows = await invoke(actors.list_names(limit=limit))
    return [row.to_schema() for row in rows]


@actors_router.get("/actors/{actor_id}", response_model=ActorSchema)
async def get_actor(
    actor_id: int,
    actors: ActorsUseCase = Depends(get_actors_use_case),
) -> ActorSchema:
    return (await invoke(actors.get_actor(actor_id), domain_errors=_REPO_ERRORS)).to_schema()
