from titanic.app.jack_service import JackService


class JamesController:
    def __init__(self) -> None:
        self.service = JackService()

    def get_data(self):
        return self.service.get_data()

    def get_count(self) -> int:
        return self.service.get_count()

    def get_survived_count(self) -> int:
        return self.service.get_survived_count()

    def get_dead_count(self) -> int:
        return self.service.get_dead_count()

    def has_decision_tree_model(self) -> bool:
        return self.service.has_decision_tree_model()

    def get_model_name_and_accuracy(self):
        return self.service.get_model_name_and_accuracy()