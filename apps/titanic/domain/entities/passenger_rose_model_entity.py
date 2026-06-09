from __future__ import annotations

from dataclasses import dataclass, field

from titanic.domain.value_objects.passenger_rose_model_vo import (
    Cabin,
    Embarkation,
    PassengerClass,
    PersonId,
    TicketInfo,
)


@dataclass
class Booking:
    """
    Booking Domain Entity — DDD 엄격 적용.

    동등성 기준 : (person_id, ticket_info.ticket) — 비즈니스 자연 키
    ORM 매핑   : 인프라 계층(PassengerRoseModelMapper)에서 담당 — 엔티티는 ORM을 모른다.
    _db_id     : 인프라 전용 PK; 도메인 로직에서 직접 참조 금지.
    """

    person_id: PersonId
    passenger_class: PassengerClass
    ticket_info: TicketInfo
    cabin: Cabin
    embarkation: Embarkation

    _db_id: int | None = field(default=None, repr=False, compare=False)

    # ── 동등성: (person_id, ticket) 기준 ─────────────────────────
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Booking):
            return NotImplemented
        return (
            self.person_id == other.person_id
            and self.ticket_info.ticket == other.ticket_info.ticket
        )

    def __hash__(self) -> int:
        return hash((self.person_id, self.ticket_info.ticket))

    # ── 도메인 행위 ────────────────────────────────────────────────
    def is_first_class(self) -> bool:
        return self.passenger_class.is_first_class()

    def deck(self) -> str | None:
        return self.cabin.deck

    def embarkation_port(self) -> str:
        return self.embarkation.port_name

    def summary(self) -> str:
        deck_text = self.cabin.deck or "미확인"
        return (
            f"[person:{self.person_id}] {self.ticket_info.ticket} "
            f"(등급:{self.passenger_class.value}, 데크:{deck_text}, "
            f"요금:{self.ticket_info.fare}, 승선:{self.embarkation.port_name})"
        )

    # ── 팩토리: VO 집합에서 Entity 생성 ───────────────────────────
    @classmethod
    def create(
        cls,
        person_id: PersonId,
        passenger_class: PassengerClass,
        ticket_info: TicketInfo,
        cabin: Cabin,
        embarkation: Embarkation,
    ) -> Booking:
        """신규 예약 생성 팩토리 — ORM·DB와 무관."""
        return cls(
            person_id=person_id,
            passenger_class=passenger_class,
            ticket_info=ticket_info,
            cabin=cabin,
            embarkation=embarkation,
        )
