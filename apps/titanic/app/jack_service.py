from pathlib import Path

from titanic.app.rose_model import RoseModel
from titanic.app.walter_reader import WalterReader

_MODEL_PATH = Path(__file__).resolve().parent / "models" / "titanic_decision_tree.joblib"


class JackService:
    def __init__(self) -> None:
        self.walter = WalterReader()
        self.rose = RoseModel()

    def get_data(self):
        return self.walter.get_data()

    def get_count(self) -> int:
        return self.walter.get_count()

    def has_decision_tree_model(self) -> bool:
        return _MODEL_PATH.is_file()

    def get_model_name_and_accuracy(self) -> dict[str, str | None]:
        return {
            "model_name": self.rose.get_model_name(),
            "accuracy": None,
        }