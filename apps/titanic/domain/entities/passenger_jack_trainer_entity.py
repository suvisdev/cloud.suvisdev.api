from __future__ import annotations

from dataclasses import dataclass

from titanic.domain.value_objects.passenger_jack_trainer_vo import (
    FamilyRelation,
    PassengerId,
    PersonalInfo,
    SurvivalStatus,
)


@dataclass
class PassengerJackTrainer:
    """
    Passenger Domain Entity — DDD 엄격 적용.

    동등성 기준 : passenger_id (비즈니스 키)
    ORM 매핑   : 인프라 계층(JackTrainerPgRepository)에서 담당 — 엔티티는 ORM을 모른다.
    PK         : passenger_id (ORM·DB와 동일 비즈니스 키).
    """

    passenger_id: PassengerId
    personal_info: PersonalInfo
    family_relation: FamilyRelation
    survival_status: SurvivalStatus

    # ── 동등성: passenger_id 기준 ─────────────────────────────────
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PassengerJackTrainer):
            return NotImplemented
        return self.passenger_id == other.passenger_id

    def __hash__(self) -> int:
        return hash(self.passenger_id)

    # ── 도메인 행위 ────────────────────────────────────────────────
    def update_survival(self, new_status: SurvivalStatus) -> None:
        """생존 상태 갱신."""
        self.survival_status = new_status

    def is_traveling_alone(self) -> bool:
        return self.family_relation.is_alone()

    def summary(self) -> str:
        survived_label = {True: "생존", False: "사망", None: "미확인"}[
            self.survival_status.is_survived
        ]
        return (
            f"[{self.passenger_id}] {self.personal_info.name} "
            f"({self.personal_info.gender}, {self.personal_info.age}세) — {survived_label}"
        )

    # ── 팩토리: VO 집합에서 Entity 생성 ───────────────────────────
    @classmethod
    def create(
        cls,
        passenger_id: PassengerId,
        personal_info: PersonalInfo,
        family_relation: FamilyRelation,
        survival_status: SurvivalStatus | None = None,
    ) -> PassengerJackTrainer:
        """신규 승객 생성 팩토리 — ORM·DB와 무관."""
        return cls(
            passenger_id=passenger_id,
            personal_info=personal_info,
            family_relation=family_relation,
            survival_status=survival_status or SurvivalStatus.unknown(),
        )
