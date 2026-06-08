from io import StringIO
import csv
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from titanic.adapter.inbound.api.schemas.crew_james_director_schema import JamesIntroduceSchema, JamesSchema
from titanic.app.dtos.crew_james_director_dto import JamesIntroduceResponse, JamesResponse
from titanic.app.ports.input.crew_james_director_use_case import JamesUseCase
from titanic.dependencies.crew_james_director_provider import get_james_director_use_case

james_director_router = APIRouter(prefix="/james", tags=["james"])
logger = logging.getLogger(__name__)


@james_director_router.get("/myself")
async def introduce_myself(
    james: JamesUseCase = Depends(get_james_director_use_case),
) -> JamesIntroduceResponse:
    return await james.introduce_myself(
        JamesIntroduceSchema(
            id=12,
            name="제임스 카메론 (James Cameron)",
        )
    )


@james_director_router.post("/upload")
async def receive_uploaded_records(
    file: UploadFile = File(...),
    james: JamesUseCase = Depends(get_james_director_use_case),
) -> JamesResponse:
    return await james.receive_uploaded_records(
        _parse_csv((await file.read()).decode("utf-8-sig", errors="replace"))
    )


def _parse_csv(text: str) -> list[JamesSchema]:
    if not text.strip():
        raise HTTPException(status_code=400, detail="빈 CSV 파일입니다.")
    reader = csv.DictReader(StringIO(text))
    if reader.fieldnames is None:
        raise HTTPException(status_code=400, detail="CSV 헤더를 읽을 수 없습니다.")
    return [
        JamesSchema(**_normalize_james_row(row))
        for row in reader
    ]


def _normalize_james_row(row: dict) -> dict:
    normalized: dict[str, str] = {}
    for raw_key, value in row.items():
        if raw_key is None:
            continue
        key = raw_key.strip()
        lower_key = key.lower()
        if lower_key == "sex":
            normalized["gender"] = value
        elif lower_key == "passengerid":
            normalized["passenger_id"] = value
        elif lower_key == "sibsp":
            normalized["sib_sp"] = value
        elif lower_key in {
            "survived",
            "pclass",
            "name",
            "age",
            "parch",
            "ticket",
            "fare",
            "cabin",
            "embarked",
            "gender",
        }:
            normalized[lower_key] = value
        else:
            normalized[key] = value
    return normalized
