import logging
import pandas as pd
from titanic.app.services.jack_service import JackService
from titanic.app.schemas.caledon_validation import TitanicPredictInput, TitanicPredictOutput

logger = logging.getLogger(__name__)


class JamesController:
    """타이타닉 요청 처리 및 제어를 담당하는 웹 컨트롤러 계층(Controller)."""

    def __init__(self) -> None:
        self.service = JackService()

    def get_data(self) -> pd.DataFrame:
        """탑승자 데이터프레임의 대표 데이터를 조회합니다."""
        return self.service.get_data()

    def get_count(self) -> int:
        """전체 탑승객 수 집계를 반환합니다."""
        return self.service.get_count()

    def get_survived_count(self) -> int:
        """총 생존 승객 수 집계를 반환합니다."""
        return self.service.get_survived_count()

    def get_dead_count(self) -> int:
        """총 사망 승객 수 집계를 반환합니다."""
        return self.service.get_dead_count()

    def has_decision_tree_model(self) -> bool:
        """예측을 위한 ML 모델 로드 가능 여부를 조회합니다."""
        return self.service.has_decision_tree_model()

    def get_model_name_and_accuracy(self) -> dict:
        """사용 중인 생존 분류 모델의 알고리즘과 정확도를 조회합니다."""
        return self.service.get_model_name_and_accuracy()

    def predict(self, payload: TitanicPredictInput) -> TitanicPredictOutput:
        """사용자 승객 데이터를 입력받아 생존 여부 및 분석 결과를 예측합니다."""
        logger.info("[JamesController] 생존 예측 진행 — Pclass=%s Sex=%s Age=%s", payload.pclass, payload.sex, payload.age)
        return self.service.predict_survival(payload)

    def analyze_dicaprio_survival(self) -> dict:
        """디카프리오(잭)와 로즈의 승객 조건 비교 및 생존 가능성 데이터 심층 분석을 조회합니다."""
        logger.info("[JamesController] 디카프리오 생존 통계 분석 요청 수신")
        return self.service.analyze_dicaprio_survival()
