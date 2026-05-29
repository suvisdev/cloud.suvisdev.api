from __future__ import annotations

import csv
import logging
from io import StringIO

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from titanic.app.dtos.james_dto import JamesRowPayload, JamesUploadResult
from titanic.app.use_cases.james_command import JamesCommand

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


@james_router.post("/upload", response_model=JamesUploadResult)
async def upload_titanic_csv(
    request: Request,
    file: UploadFile = File(...),
) -> JamesUploadResult:
    filename_raw = file.filename or ""
    filename = filename_raw.lower()
    logger.info(
        "🤖 [JamesRouter] upload_titanic_csv 진입 — file=%s path=%s",
        filename_raw,
        request.url.path,
    )

    if not filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드할 수 있습니다.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")

    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(StringIO(text))

    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV 헤더를 찾을 수 없습니다.")

    missing = [h for h in _REQUIRED_HEADERS if h not in reader.fieldnames]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"필수 컬럼이 없습니다: {', '.join(missing)}",
        )

    rows: list[JamesRowPayload] = []
    for row in reader:
        rows.append(
            JamesRowPayload(
                passenger_id=str(row.get("PassengerId", "") or ""),
                survived=str(row.get("Survived", "") or ""),
                pclass=str(row.get("Pclass", "") or ""),
                name=str(row.get("Name", "") or ""),
                gender=str(row.get("Sex", "") or ""),
                age=str(row.get("Age", "") or ""),
                sibsp=str(row.get("SibSp", "") or ""),
                parch=str(row.get("Parch", "") or ""),
                ticket=str(row.get("Ticket", "") or ""),
                fare=str(row.get("Fare", "") or ""),
                cabin=str(row.get("Cabin", "") or ""),
                embarked=str(row.get("Embarked", "") or ""),
            )
        )

    logger.info("🤖 [JamesRouter] parsed_rows=%s", len(rows))

    try:
        result = await JamesCommand().receive_upload_records(
            [row.model_dump() for row in rows],
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
    return result
