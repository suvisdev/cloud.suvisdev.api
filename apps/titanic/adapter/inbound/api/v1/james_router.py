from __future__ import annotations

import csv
import logging
from io import StringIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError

from titanic.adapter.inbound.api.schemas.james_schema import JamesRowSchema
from titanic.app.ports.input.james_use_case import JamesUseCase

james_router = APIRouter(prefix="/titanic/james", tags=["james"])
logger = logging.getLogger(__name__)

_REQUIRED_HEADERS = [
    "PassengerId",
    "Survived",
    "Pclass",
    "Name",
    "Sex",
    "Age",
    "SibSp",
    "Parch",
    "Ticket",
    "Fare",
    "Cabin",
    "Embarked",
]


@james_router.post("/upload", response_model=int)
async def upload_titanic_csv(file: UploadFile = File(...)) -> int:
    filename = file.filename or ""
    
    james_use_case = JamesUseCase()
    """타이타닉 승객 데이터 csv 파일 업로드 코드"""

    logger.info("🤖 [JamesRouter] upload_titanic_csv 진입 — file=%s", filename)

    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드할 수 있습니다.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")

    # csv 파일의 내용을 JamesRowSchema 형식으로 변환
    reader = csv.DictReader(StringIO(raw.decode("utf-8-sig", errors="replace")))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV 헤더를 찾을 수 없습니다.")

    missing = [h for h in _REQUIRED_HEADERS if h not in reader.fieldnames]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"필수 컬럼이 없습니다: {', '.join(missing)}",
        )

    records: list[JamesRowSchema] = [
        JamesRowSchema.model_validate(row) for row in reader
    ]

    # records에 상위 5줄 출력하는 로그
    print(f"[제임스 라우터] 업로드된 csv 파일에서 파싱된 상위 5개 레코드:")
    preview_count = min(5, len(records))
    logger.info(
        "🤖 [JamesRouter] records 파싱 완료 — total=%s, 미리보기 %s건",
        len(records),
        preview_count,
    )
    for index, record in enumerate(records[:5], start=1):
        logger.info(
            "🤖 [JamesRouter] records[%s/%s] — %s",
            index,
            preview_count,
            record.model_dump(),
        )

    try:
        result = await JamesInteractor(JamesPgRepository()).receive_upload_records(
            [record.model_dump() for record in records],
        )
    except RuntimeError as exc:
        logger.exception("🤖 [JamesRouter] DB 연결 실패")
        raise HTTPException(
            status_code=503,
            detail=f"DB에 연결할 수 없습니다. backend/.env 의 DATABASE_URL을 확인하세요. ({exc})",
        ) from exc
    except SQLAlchemyError as exc:
        logger.exception("🤖 [JamesRouter] DB 저장 실패")
        raise HTTPException(
            status_code=500,
            detail=f"DB 저장에 실패했습니다: {exc}",
        ) from exc

    logger.info(
        "🤖 [JamesRouter] upload_titanic_csv 완료 — saved_rows=%s",
        result.row_count,
    )
    return result.row_count
