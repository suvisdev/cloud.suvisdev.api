from __future__ import annotations

from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerOrm
from titanic.domain.entities.passenger_jack_trainer_entity import PassengerJackTrainer
from titanic.domain.value_objects.passenger_jack_trainer_vo import (
    FamilyRelation,
    PassengerId,
    PersonalInfo,
    SurvivalStatus,
)


class PassengerJackTrainerMapper:
    """JackTrainerOrm ↔ PassengerJackTrainer 변환 — 인프라 계층 전용."""

    @staticmethod
    def to_entity(orm: JackTrainerOrm) -> PassengerJackTrainer:
        """ORM row → Domain Entity."""
        return PassengerJackTrainer(
            passenger_id=PassengerId(orm.passenger_id),
            personal_info=PersonalInfo(
                name=orm.name,
                gender=orm.gender,
                age=orm.age,
            ),
            family_relation=FamilyRelation(
                sib_sp=orm.sib_sp,
                parch=orm.parch,
            ),
            survival_status=SurvivalStatus(orm.survived),
        )

    @staticmethod
    def to_orm_fields(entity: PassengerJackTrainer) -> dict[str, str]:
        """Domain Entity → ORM 컬럼 dict (INSERT/UPDATE 시 사용)."""
        return {
            "passenger_id": str(entity.passenger_id),
            "name": entity.personal_info.name,
            "gender": entity.personal_info.gender,
            "age": entity.personal_info.age,
            "sib_sp": entity.family_relation.sib_sp,
            "parch": entity.family_relation.parch,
            "survived": entity.survival_status.value,
        }
