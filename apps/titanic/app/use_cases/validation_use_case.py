from typing import Literal

from pydantic import BaseModel, Field


class TitanicPredictInput(BaseModel):
    """타이타닉 생존 예측 입력 스키마 (6개 독립변수)."""

    pclass: int = Field(..., description="티켓 클래스 (1 = 1등석, 2 = 2등석, 3 = 3등석)", ge=1, le=3)
    sex: Literal["male", "female"] = Field(..., description="성별 (male 또는 female)")
    age: float = Field(29.699, description="나이", ge=0.0)
    sibsp: int = Field(0, description="함께 탑승한 자녀 / 배우자 수", ge=0)
    parch: int = Field(0, description="함께 탑승한 부모 / 자녀 수", ge=0)
    fare: float = Field(32.204, description="탑승 요금", ge=0.0)


class TitanicPredictOutput(BaseModel):
    """타이타닉 생존 예측 결과 출력 스키마."""

    survived: int = Field(..., description="생존 여부 (0 = 사망, 1 = 생존)")
    survival_probability: float = Field(..., description="생존 확률 (0.0 ~ 1.0)")
    pclass: int
    sex: str
    age: float
    fare: float
    description: str = Field(..., description="데이터 기반 생존/사망 분석 상세 설명")


class CaledonValidation:
    """기존 클래스 네이밍 호환을 위한 래퍼 검증 클래스."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def validate_predict_input(data: dict) -> TitanicPredictInput:
        """딕셔너리 데이터를 받아 TitanicPredictInput 객체로 검증 및 파싱합니다."""
        return TitanicPredictInput(**data)
