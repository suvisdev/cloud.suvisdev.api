import logging
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

logger = logging.getLogger(__name__)


class RoseModel:
    """타이타닉 생존 예측 의사결정나무(Decision Tree) 모델 래퍼 계층(Model)."""

    def __init__(self) -> None:
        self.model = DecisionTreeClassifier(max_depth=5, random_state=42)
        self.is_trained = False
        logger.info("[RoseModel] 내부 파일 기반 모델 로딩이 비활성화되었습니다.")

    def get_model_name(self) -> str:
        """ML 모델의 알고리즘 명을 반환합니다."""
        return type(self.model).__name__

    def train_and_save(self, df: pd.DataFrame) -> None:
        """제공된 데이터프레임을 활용하여 6개 독립변수 기준으로 모델을 메모리에서만 학습시킵니다."""
        logger.info("[RoseModel] 6개 독립변수 기준 의사결정나무 모델 학습 개시...")

        # 전처리
        df_clean = df.copy()
        # 나이 결측치 처리 (중앙값 대체)
        age_median = df_clean["Age"].median()
        df_clean["Age"] = df_clean["Age"].fillna(age_median)
        # 성별 인코딩 (male=0, female=1)
        df_clean["Sex"] = df_clean["Sex"].map({"male": 0, "female": 1})

        # 특징량 및 라벨 추출
        X = df_clean[["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare"]]
        y = df_clean["Survived"]

        # 모델 피팅
        self.model.fit(X, y)
        self.is_trained = True
        logger.info("[RoseModel] 학습 완료 (내부 파일 저장 없음)")

    def predict(self, features: pd.DataFrame) -> list[int]:
        """특징량 데이터프레임을 받아 생존 여부를 예측합니다 (0: 사망, 1: 생존)."""
        if not self.is_trained:
            raise RuntimeError("모델이 아직 학습되지 않았습니다.")
        return self.model.predict(features).tolist()

    def predict_proba(self, features: pd.DataFrame) -> list[list[float]]:
        """생존 및 사망 클래스 각각에 대한 예측 확률을 구합니다."""
        if not self.is_trained:
            raise RuntimeError("모델이 아직 학습되지 않았습니다.")
        return self.model.predict_proba(features).tolist()
