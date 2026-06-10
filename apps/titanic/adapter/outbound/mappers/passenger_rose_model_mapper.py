from __future__ import annotations

from titanic.adapter.outbound.orm.passenger_rose_model_orm import RoseModelOrm
from titanic.domain.entities.passenger_rose_model_entity import Booking
from titanic.domain.value_objects.passenger_rose_model_vo import (
    Cabin,
    Embarkation,
    PassengerClass,
    PersonId,
    TicketInfo,
)


class PassengerRoseModelMapper:
    """RoseModelOrm ↔ Booking 변환 — 인프라 계층 전용."""

    @staticmethod
    def to_entity(orm: RoseModelOrm) -> Booking:
        """ORM row → Domain Entity."""
        return Booking(
            person_id=PersonId(orm.passenger_id),
            passenger_class=PassengerClass(orm.pclass),
            ticket_info=TicketInfo(ticket=orm.ticket, fare=orm.fare),
            cabin=Cabin(orm.cabin),
            embarkation=Embarkation(orm.embarked),
            _db_id=orm.id,
        )

    @staticmethod
    def to_orm_fields(entity: Booking) -> dict[str, str]:
        """Domain Entity → ORM 컬럼 dict (INSERT/UPDATE 시 사용)."""
        return {
            "passenger_id": entity.person_id.value,
            "pclass": entity.passenger_class.value,
            "ticket": entity.ticket_info.ticket,
            "fare": entity.ticket_info.fare,
            "cabin": entity.cabin.value,
            "embarked": entity.embarkation.value,
        }
