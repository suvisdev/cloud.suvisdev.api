from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from mova.adapter.inbound.api.schemas.actors_schema import ActorCreateSchema, ActorSchema
from mova.adapter.outbound.pg.actors_pg_repository import ActorsRepositoryError
from mova.app.ports.input.actors_use_case import ActorsUseCase
from mova.app.use_cases.actors_interactor import ActorsInteractor

actors_router = APIRouter(tags=["mova-actors"])

logger = logging.getLogger(__name__)


@actors_router.post("/actors", response_model=ActorSchema, status_code=201)
async def save_actor(req: ActorCreateSchema) -> ActorSchema:
    logger.info("[ActorsRouter] save_actor — %r", req.name)
    use_case: ActorsUseCase = ActorsInteractor()
    try:
        return await use_case.save_actor(req)
    except ActorsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@actors_router.get("/actors", response_model=list[ActorSchema])
async def list_actors(limit: int = 100) -> list[ActorSchema]:
    use_case: ActorsUseCase = ActorsInteractor()
    try:
        return await use_case.list_actors(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@actors_router.post("/actors/names", response_model=ActorSchema, status_code=201)
async def save_actor_name(req: ActorCreateSchema) -> ActorSchema:
    logger.info("[ActorsRouter] save_actor_name — %r", req.name)
    use_case: ActorsUseCase = ActorsInteractor()
    try:
        return await use_case.save_name(req)
    except ActorsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@actors_router.get("/actors/names", response_model=list[ActorSchema])
async def list_actor_names(limit: int = 100) -> list[ActorSchema]:
    use_case: ActorsUseCase = ActorsInteractor()
    try:
        return await use_case.list_names(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@actors_router.get("/actors/{actor_id}", response_model=ActorSchema)
async def get_actor(actor_id: int) -> ActorSchema:
    use_case: ActorsUseCase = ActorsInteractor()
    try:
        return await use_case.get_actor(actor_id)
    except ActorsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
