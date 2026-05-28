from __future__ import annotations

import csv
import logging
from io import StringIO

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from titanic.app.ports.input.james_use_case import (
    JamesRowPayload,
    JamesUploadResult,
    JamesUseCase,
)

james_router = APIRouter(prefix="/titanic/james", tags=["james"])
logger = logging.getLogger(__name__)
request_logger = logging.getLogger("uvicorn.error")

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
    server_temp_path = str(getattr(file.file, "name", ""))
    if not server_temp_path:
        server_temp_path = "(in-memory)"

    print("\n================ TITANIC CSV UPLOAD START ================", flush=True)
    print(
        f"[TITANIC-UPLOAD] file={filename_raw} temp_path={server_temp_path}",
        flush=True,
    )
    print("==========================================================\n", flush=True)
    logger.info(
        "================ TITANIC CSV UPLOAD START ================",
    )
    logger.info(
        "[TITANIC-UPLOAD] file=%s temp_path=%s",
        filename_raw,
        server_temp_path,
    )
    logger.info("[TITANIC-UPLOAD] request_path=%s method=%s", request.url.path, request.method)
    request_logger.warning(
        "[TITANIC-UPLOAD-PATH] %s %s file=%s",
        request.method,
        request.url.path,
        filename_raw,
    )
    logger.info(
        "[TITANIC-UPLOAD-FLOW] walter_router -> james_use_case -> james_command -> james_repository -> james_pg_repository -> NeonDB",
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
        # Sex -> gender 변환 (모든 필드는 str 유지)
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

    logger.info(
        "[TITANIC-UPLOAD] parsed_rows=%s headers=%s",
        len(rows),
        ",".join(reader.fieldnames or []),
    )
    result = await JamesUseCase().upload_rows(rows)
    logger.info("[TITANIC-UPLOAD] saved_rows=%s", result.row_count)
    logger.info(
        "================= TITANIC CSV UPLOAD END =================",
    )
    return result