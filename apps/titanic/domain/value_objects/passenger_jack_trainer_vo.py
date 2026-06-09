from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PassengerId:
    """ORM passenger_id(str) 를 감싸는 도메인 식별자 VO."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PassengerId는 빈 문자열일 수 없습니다.")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PersonalInfo:
    """이름·성별·나이 — 함께 의미를 가지는 묶음 VO."""

    name: str
    gender: str
    age: str  # 원본 CSV가 str이므로 유지; 도메인 불변식만 검증

    _ALLOWED_GENDERS: frozenset[str] = frozenset({"male", "female", ""})

    def __post_init__(self) -> None:
        if self.gender.lower() not in self._ALLOWED_GENDERS:
            raise ValueError(f"허용되지 않는 성별 값: {self.gender!r}")

    @property
    def age_as_int(self) -> int | None:
        try:
            return int(float(self.age))
        except (ValueError, TypeError):
            return None

    def is_adult(self) -> bool:
        age = self.age_as_int
        return age is not None and age >= 18


@dataclass(frozen=True)
class FamilyRelation:
    """형제/배우자(sib_sp)·부모/자녀(parch) 관계 수치 VO."""

    sib_sp: str
    parch: str

    def __post_init__(self) -> None:
        for field_name, val in (("sib_sp", self.sib_sp), ("parch", self.parch)):
            if val and not val.strip().lstrip("-").isdigit():
                raise ValueError(f"{field_name} 값이 숫자 형식이 아닙니다: {val!r}")

    @property
    def total_family_members(self) -> int:
        return int(self.sib_sp or 0) + int(self.parch or 0)

    def is_alone(self) -> bool:
        return self.total_family_members == 0


@dataclass(frozen=True)
class SurvivalStatus:
    """생존 여부 VO — '0'(사망) / '1'(생존) / ''(미확인) 세 가지 상태."""

    value: str

    _SURVIVED: str = "1"
    _NOT_SURVIVED: str = "0"
    _UNKNOWN: str = ""

    def __post_init__(self) -> None:
        allowed = {self._SURVIVED, self._NOT_SURVIVED, self._UNKNOWN}
        if self.value not in allowed:
            raise ValueError(
                f"SurvivalStatus 허용값: '0', '1', '' — 받은 값: {self.value!r}"
            )

    @property
    def is_survived(self) -> bool | None:
        if self.value == self._SURVIVED:
            return True
        if self.value == self._NOT_SURVIVED:
            return False
        return None

    @classmethod
    def unknown(cls) -> SurvivalStatus:
        return cls(cls._UNKNOWN)
