from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from mova.adapter.inbound.api.schemas.actors_schema import ActorCreateSchema, ActorSchema
from mova.adapter.outbound.pg.actors_pg_repository import ActorsRepositoryError
from mova.app.ports.input.actors_use_case import ActorsUseCase
from mova.dependencies.actors import get_actors_use_case

actors_router = APIRouter(tags=["mova-actors"])


@actors_router.post("/actors", response_model=ActorSchema, status_code=201)
async def save_actor(
    req: ActorCreateSchema,
    actors: ActorsUseCase = Depends(get_actors_use_case),
) -> ActorSchema:
    try:
        return await actors.save_actor(req)
    except ActorsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@actors_router.get("/actors", response_model=list[ActorSchema])
async def list_actors(
    limit: int = 100,
    actors: ActorsUseCase = Depends(get_actors_use_case),
) -> list[ActorSchema]:
    try:
        return await actors.list_actors(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@actors_router.post("/actors/names", response_model=ActorSchema, status_code=201)
async def save_actor_name(
    req: ActorCreateSchema,
    actors: ActorsUseCase = Depends(get_actors_use_case),
) -> ActorSchema:
    try:
        return await actors.save_name(req)
    except ActorsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@actors_router.get("/actors/names", response_model=list[ActorSchema])
async def list_actor_names(
    limit: int = 100,
    actors: ActorsUseCase = Depends(get_actors_use_case),
) -> list[ActorSchema]:
    try:
        return await actors.list_names(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@actors_router.get("/actors/{actor_id}", response_model=ActorSchema)
async def get_actor(
    actor_id: int,
    actors: ActorsUseCase = Depends(get_actors_use_case),
) -> ActorSchema:
    try:
        return await actors.get_actor(actor_id)
    except ActorsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
