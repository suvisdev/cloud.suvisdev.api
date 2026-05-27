from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class TitanicRowRequest(BaseModel):
    """
    Inbound(Adapter)용 타이타닉 입력 DTO.

    - 타입: 모든 컬럼은 `str`로 받습니다. (파싱/변환은 use-case에서 처리)
    - 컬럼명: 이미지 기준 `Sex`를 도메인/코드 관점에서 `gender`로 변형합니다.
    """

    model_config = ConfigDict(populate_by_name=True)

    passenger_id: str = Field(..., alias="PassengerId")
    survived: str = Field(..., alias="Survived")
    pclass: str = Field(..., alias="Pclass")
    name: str = Field(..., alias="Name")
    gender: str = Field(..., alias="Sex")
    age: str = Field(..., alias="Age")
    sibsp: str = Field(..., alias="SibSp")
    parch: str = Field(..., alias="Parch")
    ticket: str = Field(..., alias="Ticket")
    fare: str = Field(..., alias="Fare")
    cabin: str = Field(..., alias="Cabin")
    embarked: str = Field(..., alias="Embarked")


class TitanicDatasetRequest(BaseModel):
    """
    배치로 받을 경우를 위한 요청 스키마.
    """

    model_config = ConfigDict(populate_by_name=True)

    rows: List[TitanicRowRequest] = Field(..., description="타이타닉 데이터 row 목록")

