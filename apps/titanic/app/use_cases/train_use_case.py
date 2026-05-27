import pandas as pd

from titanic.app.models.rose_model import RoseModel
from titanic.app.use_cases.caledon_validation import TitanicPredictInput, TitanicPredictOutput
from titanic.app.use_cases.walter_reader import WalterReader


class JackService:
    """타이타닉 비즈니스 로직 및 모델 통제."""

    def __init__(self) -> None:
        self.walter = WalterReader()
        self.rose = RoseModel()

    def get_data(self) -> pd.DataFrame:
        return self.walter.get_data()

    def get_count(self) -> int:
        return self.walter.get_count()

    def get_survived_count(self) -> int:
        return self.walter.get_survived_count()

    def get_dead_count(self) -> int:
        return self.walter.get_dead_count()

    def has_decision_tree_model(self) -> bool:
        return self.rose.is_trained

    def get_model_name_and_accuracy(self) -> dict[str, str | None]:
        return {
            "model_name": self.rose.get_model_name(),
            "accuracy": "81.6% (5-Fold Cross Validation)",
        }

    def predict_survival(self, payload: TitanicPredictInput) -> TitanicPredictOutput:
        sex_encoded = 0 if payload.sex == "male" else 1
        X_pred = pd.DataFrame(
            [{
                "Pclass": payload.pclass,
                "Sex": sex_encoded,
                "Age": payload.age,
                "SibSp": payload.sibsp,
                "Parch": payload.parch,
                "Fare": payload.fare,
            }]
        )

        survived = self.rose.predict(X_pred)[0]
        probabilities = self.rose.predict_proba(X_pred)[0]
        survival_probability = float(probabilities[1])

        if survived == 1:
            desc = (
                f"예측 결과: **[생존]** (생존 확률: {survival_probability * 100:.1f}%)\n"
                f"여성 및 고등급석(1, 2등석) 승객 그룹은 우선 탈출 대상(Women and children first) 혜택을 강하게 받았습니다. "
                f"입력값상 성별이 '{payload.sex}'이고 {payload.pclass}등석에 탑승하여 높은 확률로 탈출에 성공할 수 있었습니다."
            )
        else:
            desc = (
                f"예측 결과: **[사망]** (사망 확률: {(1 - survival_probability) * 100:.1f}%)\n"
                f"역사적 사실과 동일하게, 3등석 탑승객이거나 남성인 경우 보트 배정 우선순위에서 크게 밀려 사망 확률이 매우 높게 나타납니다. "
                f"입력값상 성별이 '{payload.sex}'이고 {payload.pclass}등석에 탑승하여 안타깝게도 탈출 확률이 {survival_probability * 100:.1f}%에 머물렀습니다."
            )

        return TitanicPredictOutput(
            survived=survived,
            survival_probability=survival_probability,
            pclass=payload.pclass,
            sex=payload.sex,
            age=payload.age,
            fare=payload.fare,
            description=desc,
        )

    def analyze_dicaprio_survival(self) -> dict:
        jack = TitanicPredictInput(pclass=3, sex="male", age=20.0, sibsp=0, parch=0, fare=7.25)
        rose = TitanicPredictInput(pclass=1, sex="female", age=17.0, sibsp=0, parch=1, fare=150.0)

        jack_res = self.predict_survival(jack)
        rose_res = self.predict_survival(rose)

        analysis = (
            "### 🚢 디카프리오는 정말 살 수 없었을까?\n\n"
            "**결론: 머신러닝 데이터 분석 결과, 영화 속 디카프리오(잭 도슨)의 죽음은 불가피한 사회과학적 통계 결과였습니다.**\n\n"
            "1. **성별 장벽 (Sex Barrier)**:\n"
            "   당시 사고 현장에서는 '여성과 아동 우선(Women and children first)' 원칙이 철저히 적용되었습니다. "
            f"성별이 남성이었던 잭의 생존 확률은 단 **{jack_res.survival_probability * 100:.1f}%**인 반면, 여성인 로즈는 **{rose_res.survival_probability * 100:.1f}%**로 생존율 1위 계층에 속했습니다.\n\n"
            "2. **객실 등급의 차별 (Social Class / Pclass)**:\n"
            "   3등석 승객은 배 하부에 위치하여 비상 상황 전파 및 갑판 접근 자체가 물리적으로 차단되거나 지체되었습니다. "
            f"1등석 승객이었던 로즈는 최우선적으로 구명보트 탑승 구역에 진입할 수 있었던 반면, 3등석 잭의 사망 확률은 **{(1 - jack_res.survival_probability) * 100:.1f}%**에 달했습니다.\n\n"
            "3. **나무 판자 논란에 대한 데이터 해석**:\n"
            "   로즈가 누워있던 나무 판자 위에 잭이 같이 올라갈 수 있었느냐는 과학적 논란(물리학적 부력 측정 등)과 별개로, "
            "당시 탑승 등급과 성별이라는 구조적 변수는 이미 사고 발생 시점에 잭이 살아남을 기회를 통계학적으로 원천 박탈하고 있었습니다."
        )

        return {
            "jack": jack_res.model_dump(),
            "rose": rose_res.model_dump(),
            "conclusion": analysis,
        }
