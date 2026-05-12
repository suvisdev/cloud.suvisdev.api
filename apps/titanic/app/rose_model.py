from sklearn.tree import DecisionTreeClassifier


class RoseModel:
    def __init__(self) -> None:
        self.model = DecisionTreeClassifier()

    def get_model_name(self) -> str:
        return type(self.model).__name__