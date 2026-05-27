from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from titanic.app.use_cases.titanic_query_impl import TitanicQueryImpl

titanic_router = APIRouter(prefix="/titanic", tags=["titanic-query"])

_FILE_READ_REMOVED = (
    "프로젝트 내부 파일 읽기 기능이 제거되었습니다. 외부 저장소/DB 연동으로 전환해 주세요."
)


def _query() -> TitanicQueryImpl:
    return TitanicQueryImpl()


@titanic_router.get("/data")
def read_titanic_data():
    raise HTTPException(status_code=410, detail=_FILE_READ_REMOVED)


@titanic_router.get("/count")
def read_titanic_count():
    raise HTTPException(status_code=410, detail=_FILE_READ_REMOVED)


@titanic_router.get("/count/survived")
def read_titanic_count_survived():
    raise HTTPException(status_code=410, detail=_FILE_READ_REMOVED)


@titanic_router.get("/count/dead")
def read_titanic_count_dead():
    raise HTTPException(status_code=410, detail=_FILE_READ_REMOVED)


@titanic_router.get("/dead/count")
def read_titanic_dead_count():
    raise HTTPException(status_code=410, detail=_FILE_READ_REMOVED)


@titanic_router.get("/tree")
def read_titanic_tree():
    tree = _query().has_decision_tree_model()
    return {"tree": tree}


@titanic_router.get("/model")
def read_titanic_model():
    model_name = _query().get_model_name_and_accuracy()
    return JSONResponse(content=jsonable_encoder(model_name))


@titanic_router.get("/predict/dicaprio")
def analyze_titanic_dicaprio():
    try:
        return _query().analyze_dicaprio_survival()
    except RuntimeError as e:
        raise HTTPException(status_code=410, detail=str(e)) from e
