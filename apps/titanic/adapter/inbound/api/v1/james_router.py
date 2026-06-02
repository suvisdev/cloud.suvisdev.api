from __future__ import annotations

import csv
import logging
from io import StringIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError

from titanic.adapter.inbound.api.schemas.james_schema import TitanicRowSchema
from titanic.app.ports.input.james_use_case import JamesUseCase
from titanic.app.use_cases.james_interactor import JamesInteractor

james_router = APIRouter(prefix="/james", tags=["james"])

logger = logging.getLogger(__name__)



def _normalize_titanic_row(row: dict) -> dict:
    normalized: dict[str, str] = {}
    for raw_key, value in row.items():
        if raw_key is None:
            continue
        key = raw_key.strip()
        lower_key = key.lower()
        if lower_key == "sex":
            normalized["gender"] = value
        elif lower_key in {
            "passengerid",
            "survived",
            "pclass",
            "name",
            "age",
            "sib_sp",
            "parch",
            "ticket",
            "fare",
            "cabin",
            "embarked",
            "gender",
        }:
            if lower_key == "passengerid":
                normalized["passenger_id"] = value

            else:
                normalized[lower_key] = value
        else:
            normalized[key] = value
    return normalized


@james_router.post("/upload", response_model=int)
async def upload_titanic_file(file: UploadFile = File(...)) -> int:
    """타이타닉 승객 데이터 CSV 파일 업로드."""
    if file.content_type not in {"text/csv", "application/vnd.ms-excel", "text/plain"}:
        raise HTTPException(status_code=400, detail="CSV 파일을 업로드해주세요.")

    raw = await file.read()
    text = raw.decode("utf-8-sig", errors="replace")
    if not text.strip():
        raise HTTPException(status_code=400, detail="빈 CSV 파일입니다.")

    reader = csv.DictReader(StringIO(text))
    if reader.fieldnames is None:
        raise HTTPException(status_code=400, detail="CSV 헤더를 읽을 수 없습니다.")

    schemas = [
        TitanicRowSchema(**_normalize_titanic_row(row))
        for row in reader
    ]

    preview_count = min(5, len(schemas))
    # 🎁로그 코드 시작
    logger.info(
        "🤖 [JamesRouter] TitanicRowSchema 파싱 완료 — total=%s, 미리보기 %s건",
        len(schemas),
        preview_count,
    )
    # 🎁로그 코드 끝
    for index, schema in enumerate(schemas[:preview_count], start=1):
        # 🎁로그 코드 시작
        logger.info(
            "🤖 [JamesRouter] TitanicRowSchema[%s/%s] — %s",
            index,
            preview_count,
            schema.model_dump(),
        )
        # 🎁로그 코드 끝
    
    use_case: JamesUseCase = JamesInteractor()

    await use_case.receive_uploaded_records(schemas)


    return len(schemas)
