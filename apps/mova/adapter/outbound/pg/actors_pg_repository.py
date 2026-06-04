from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.matrix.oracle_database import get_session_factory
from mova.adapter.outbound.orm.actors_orm import MovaActor
from mova.app.ports.output.actors_repository import ActorsRepository

logger = logging.getLogger(__name__)


class ActorsRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ActorsPgRepository(ActorsRepository):
    async def get_by_id(self, actor_id: int) -> MovaActor | None:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(select(MovaActor).where(MovaActor.id == actor_id))
            return result.scalar_one_or_none()

    async def upsert(self, data: dict) -> MovaActor:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ActorsRepositoryError("인물 이름이 비어 있습니다.", status_code=400)
        role_type = str(data.get("role_type", "actor")).strip() or "actor"
        if role_type not in ("director", "actor"):
            raise ActorsRepositoryError(
                "role_type은 director 또는 actor 여야 합니다.",
                status_code=400,
            )

        logger.info("[ActorsPgRepository] upsert — %r (%s)", name, role_type)
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaActor).where(
                    MovaActor.name == name[:128],
                    MovaActor.role_type == role_type,
                ),
            )
            row = result.scalar_one_or_none()
            if row is None:
                row = MovaActor(
                    name=name[:128],
                    role_type=role_type,
                    profile_photo_url=str(data.get("profile_photo", "")).strip(),
                )
                session.add(row)
            else:
                row.profile_photo_url = str(
                    data.get("profile_photo", row.profile_photo_url),
                ).strip()

            try:
                await session.commit()
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise ActorsRepositoryError(
                    "인물 저장에 실패했습니다.",
                    status_code=409,
                ) from e
            return row

    async def upsert_name(self, name: str) -> int:
        row = await self.upsert({"name": name, "role_type": "actor"})
        return row.id

    async def upsert_names(self, names: list[str]) -> list[int]:
        ids: list[int] = []
        seen: set[str] = set()
        for raw in names:
            key = raw.strip()
            if not key or key in seen:
                continue
            seen.add(key)
            ids.append(await self.upsert_name(key))
        return ids

    async def list_actors(self, limit: int = 100) -> list[MovaActor]:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaActor).order_by(MovaActor.id.desc()).limit(limit),
            )
            return list(result.scalars().all())

    async def list_names(self, limit: int = 100) -> list[MovaActor]:
        return await self.list_actors(limit=limit)
