from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class PersonId:
    """passengers.passenger_id FK를 감싸는 도메인 참조 VO (Cross-aggregate 참조는 ID로만)."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError(f"PersonId는 빈 문자열일 수 없습니다: {self.value!r}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PassengerClass:
    """객실 등급 VO — '1'(1등석) / '2'(2등석) / '3'(3등석) / ''(미확인)."""

    value: str

    _ALLOWED: ClassVar[frozenset[str]] = frozenset({"1", "2", "3", ""})

    def __post_init__(self) -> None:
        if self.value not in self._ALLOWED:
            raise ValueError(f"PassengerClass 허용값: 1·2·3·'' — 받은 값: {self.value!r}")

    @property
    def rank(self) -> int | None:
        try:
            return int(self.value)
        except ValueError:
            return None

    def is_first_class(self) -> bool:
        return self.value == "1"

    def is_unknown(self) -> bool:
        return self.value == ""


@dataclass(frozen=True)
class TicketInfo:
    """티켓 번호 + 요금 묶음 VO — 함께 의미를 가지는 발권 정보."""

    ticket: str
    fare: str  # 원본 CSV가 str이므로 유지; 도메인 불변식만 검증

    def __post_init__(self) -> None:
        if self.fare and not self._is_numeric(self.fare):
            raise ValueError(f"fare 값이 숫자 형식이 아닙니다: {self.fare!r}")

    @staticmethod
    def _is_numeric(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    @property
    def fare_as_float(self) -> float | None:
        try:
            return float(self.fare)
        except (ValueError, TypeError):
            return None

    def is_free(self) -> bool:
        fare = self.fare_as_float
        return fare is not None and fare == 0.0


@dataclass(frozen=True)
class Cabin:
    """객실 번호 VO — 데크(알파벳 첫 글자) 추출 가능."""

    value: str

    @property
    def deck(self) -> str | None:
        """예: 'C85' → 'C', '' → None."""
        if self.value and self.value[0].isalpha():
            return self.value[0].upper()
        return None

    def is_unknown(self) -> bool:
        return not self.value.strip()


@dataclass(frozen=True)
class Embarkation:
    """승선 항구 VO — 'C'(셰르부르) / 'Q'(퀸스타운) / 'S'(사우샘프턴) / ''(미확인)."""

    value: str

    _ALLOWED: ClassVar[frozenset[str]] = frozenset({"C", "Q", "S", ""})
    _NAMES: ClassVar[dict[str, str]] = {
        "C": "Cherbourg",
        "Q": "Queenstown",
        "S": "Southampton",
        "": "Unknown",
    }

    def __post_init__(self) -> None:
        if self.value not in self._ALLOWED:
            raise ValueError(
                f"Embarkation 허용값: C·Q·S·'' — 받은 값: {self.value!r}"
            )

    @property
    def port_name(self) -> str:
        return self._NAMES.get(self.value, "Unknown")

    def is_unknown(self) -> bool:
        return self.value == ""
