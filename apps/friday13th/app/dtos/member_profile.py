"""회원 프로필 코드값 — `members` 테이블."""

from enum import StrEnum


class MemberGender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNDISCLOSED = "undisclosed"


class MemberAgeGroup(StrEnum):
    TEENS = "10s"
    TWENTIES = "20s"
    THIRTIES = "30s"
    FORTIES = "40s"
    FIFTIES = "50s"
    SIXTIES_PLUS = "60s_plus"
    UNDISCLOSED = "undisclosed"


MEMBER_GENDERS = frozenset({g.value for g in MemberGender})
MEMBER_AGE_GROUPS = frozenset({a.value for a in MemberAgeGroup})
