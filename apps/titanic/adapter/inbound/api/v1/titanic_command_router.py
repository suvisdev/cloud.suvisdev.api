from fastapi import APIRouter, HTTPException

from titanic.app.use_cases.caledon_validation import TitanicPredictInput, TitanicPredictOutput
from titanic.app.use_cases.titanic_command_impl import TitanicCommandImpl

titanic_router = APIRouter(prefix="/titanic", tags=["titanic-command"])


def _command() -> TitanicCommandImpl:
    return TitanicCommandImpl()


@titanic_router.post("/predict", response_model=TitanicPredictOutput)
def predict_titanic_survival(payload: TitanicPredictInput):
    try:
        return _command().predict(payload)
    except RuntimeError as e:
        raise HTTPException(status_code=410, detail=str(e)) from e
