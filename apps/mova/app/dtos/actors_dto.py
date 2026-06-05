from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from mova.adapter.inbound.api.schemas.actors_schema import ActorCreateSchema, ActorSchema
    from mova.adapter.outbound.orm.actors_orm import MovaActor


@dataclass
class ActorUpsertCommand:
    name: str
    role_type: Literal["director", "actor"] = "actor"
    profile_photo: str = ""

    @classmethod
    def from_schema(cls, payload: ActorCreateSchema) -> ActorUpsertCommand:
        return cls(
            name=payload.name,
            role_type=payload.role_type,
            profile_photo=payload.profile_photo,
        )


@dataclass
class ActorDto:
    id: int
    name: str
    role_type: str
    profile_photo: str

    @classmethod
    def from_orm(cls, row: MovaActor) -> ActorDto:
        return cls(
            id=row.id,
            name=row.name,
            role_type=row.role_type,
            profile_photo=row.profile_photo_url or "",
        )

    def to_schema(self) -> ActorSchema:
        from mova.adapter.inbound.api.schemas.actors_schema import ActorSchema

        return ActorSchema(
            id=self.id,
            name=self.name,
            role_type=self.role_type,
            profile_photo=self.profile_photo,
        )
