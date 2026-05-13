import sys
from pathlib import Path

# 어디서 실행하든 `apps`가 모듈 루트로 잡히도록 (adapters, database, titanic 등)
_APPS_ROOT = Path(__file__).resolve().parent
if str(_APPS_ROOT) not in sys.path:
    sys.path.insert(0, str(_APPS_ROOT))

from fastapi import FastAPI

from adapters.db_health_adapter import DbHealthAdapter
from doro.app.doro_director import DoroDirector
from titanic.app.james_controller import JamesController

app = FastAPI(title="Suvisdev Main Page")

@app.get("/")
def read_root():
    return {"message": "FAST API 메인 페이지", "docs": "/docs"}


@app.get("/db-check")
async def check_db():
    return await DbHealthAdapter.check_neon()

@app.get("/titanic/data")
def read_titanic_data():
    james = JamesController()
    df = james.get_data()
    return df.to_dict(orient="records")

@app.get("/titanic/count")
def read_titanic_count():
    james = JamesController()
    count = james.get_count()
    return {"count": count}

@app.get("/titanic/count/survived")
def read_titanic_count_survived():
    james = JamesController()
    survived_count = james.get_survived_count()
    return {"survived_count": survived_count}

@app.get("/titanic/count/dead")
def read_titanic_count_dead():
    james = JamesController()
    dead_count = james.get_dead_count()
    return {"dead_count": dead_count}

@app.get("/titanic/dead/count")
def read_titanic_dead_count():
    james = JamesController()
    dead_count = james.get_dead_count()
    return {"dead_count": dead_count}

@app.get("/titanic/tree")
def read_titanic_tree():
    james = JamesController()
    tree = james.has_decision_tree_model()
    return {"tree": tree}

@app.get("/titanic/model")
def read_titanic_model():
    james = JamesController()
    info = james.get_model_name_and_accuracy()
    return {"model": info["model_name"], "accuracy": info["accuracy"]}


@app.get("/doro/data")
def read_doro_data():
    doro_director = DoroDirector()
    df = doro_director.get_data()
    return df.to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    