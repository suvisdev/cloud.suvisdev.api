from __future__ import annotations

import asyncio
import logging
import re

import pandas as pd
from pandas import DataFrame

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import ChatSchema, SmithCaptainSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse, SmithChatResponse
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterUseCase
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.output.crew_smith_captain_port import SmithCaptainPort

logger = logging.getLogger(__name__)


class SmithCaptainInteractor(SmithCaptainUseCase):
    def __init__(self, repository: SmithCaptainPort,
                 andrews: AndrewsArchitectUseCase,
                 jack: JackTrainerUseCase,
                 cal: CalTesterUseCase,
                 walter: WalterUseCase):
        self._repository = repository
        self.andrews = andrews
        self.jack = jack
        self.cal = cal
        self.walter = walter

    async def chat(self, schema: ChatSchema) -> SmithChatResponse:

        # schema 내용 로그로 출력
        logger.info(f"[SmithCaptainInteractor] chat | messages={schema.messages}")
        train_set: DataFrame = await self.walter.get_train_set()
        test_set: DataFrame = await self.walter.get_test_set()
        train_result: dict = await self.jack.train_model(train_set, test_set)
        test_result = await self.cal.get_test_model(test_set, train_result)
        last_user_msg = next(
            (m.content for m in reversed(schema.messages) if m.role == "user"),
            "",
        )
        question: dict = await asyncio.to_thread(self.andrews.analyze_intent, last_user_msg)
        ''' question에 따라 train_result와 test_result를 거쳐서 가장 정답률이 높은
            알고리즘을 장착한 로즈 모델의 답변을 반환한다. accuracy를 같이 첨부하여 리턴한다.
        '''
        best = test_result.best
        intent = question.get("intent", "UNKNOWN")

        predictions: list[float] = test_result.predictions
        test_meta: pd.DataFrame | None = train_result.get("test_meta")
        n_test = len(predictions)
        n_train = train_result.get("train_samples", 0)
        n_sur_all = sum(1 for p in predictions if p >= 0.5)
        rate_all = n_sur_all / n_test if n_test else 0

        def predict_subset(mask: pd.Series) -> tuple[int, int, float]:
            positions = mask[mask].index.tolist()
            preds = [predictions[i] for i in positions if i < n_test]
            n = len(preds)
            n_sur = sum(1 for p in preds if p >= 0.5)
            return n, n_sur, (n_sur / n if n else 0.0)

        # 패턴 감지 (원문 직접 검사 — 인텐트보다 신뢰도 높음)
        gender_map = {"여성": "female", "여자": "female", "남성": "male", "남자": "male"}
        age_group_map = {
            "유아": (0, 5), "아기": (0, 5),
            "어린이": (0, 12), "아이": (0, 12),
            "청소년": (12, 18), "십대": (13, 19),
            "청년": (18, 35),
            "중년": (35, 60),
            "노인": (60, 120), "어르신": (60, 120),
        }
        age_match = re.search(r"(\d+)대", last_user_msg)
        age_group_kw = next((k for k in age_group_map if k in last_user_msg), None)
        gender_kw = next((k for k in gender_map if k in last_user_msg), None)
        pclass_match = re.search(r"([1-3])등석", last_user_msg)
        is_avg_age = any(w in last_user_msg for w in ["평균 나이", "평균나이", "나이 평균", "평균 연령", "몇살"])
        is_total = any(w in last_user_msg for w in ["탑승객", "총 몇", "몇명이야", "몇 명이야", "인원"])
        is_class_stat = "등급" in last_user_msg or "통계" in last_user_msg

        # ── 패턴 우선 응답 ──
        if "선장" in last_user_msg:
            reply = (
                "에드워드 존 스미스 선장은 타이타닉과 운명을 함께했습니다. "
                "승객 탈출을 지휘한 뒤 배와 함께 침몰해 생존하지 못했습니다. "
                f"({best.strategy} 모델 기준 미확인 승객 전체 생존 예측률 {rate_all:.1%})"
            )
        elif is_total:
            reply = (
                f"데이터셋 기준 총 {n_train + n_test}명 탑승 "
                f"(생존여부 확인 {n_train}명 + 미확인 {n_test}명). "
                f"미확인 승객 중 {best.strategy} 모델이 {n_sur_all}명({rate_all:.1%}) 생존 예측."
            )
        elif is_avg_age and test_meta is not None:
            avg = test_meta["age"].dropna().mean()
            reply = f"미확인 승객 {n_test}명의 평균 나이는 {avg:.1f}세입니다."
        elif age_match and test_meta is not None:
            age_start = int(age_match.group(1))
            mask = (test_meta["age"] >= age_start) & (test_meta["age"] < age_start + 10)
            n, n_sur, rate = predict_subset(mask)
            reply = f"{age_start}대 미확인 승객 {n}명 중 {n_sur}명({rate:.1%}) 생존 예측 ({best.strategy})"
        elif age_group_kw and test_meta is not None:
            start, end = age_group_map[age_group_kw]
            mask = (test_meta["age"] >= start) & (test_meta["age"] < end)
            n, n_sur, rate = predict_subset(mask)
            reply = f"{age_group_kw} 미확인 승객 {n}명 중 {n_sur}명({rate:.1%}) 생존 예측 ({best.strategy})"
        elif gender_kw and test_meta is not None:
            g = gender_map[gender_kw]
            mask = test_meta["gender"] == g
            n, n_sur, rate = predict_subset(mask)
            reply = f"{gender_kw} 미확인 승객 {n}명 중 {n_sur}명({rate:.1%}) 생존 예측 ({best.strategy})"
        elif pclass_match and test_meta is not None:
            cls = int(pclass_match.group(1))
            mask = test_meta["pclass"] == cls
            n, n_sur, rate = predict_subset(mask)
            reply = f"{cls}등석 미확인 승객 {n}명 중 {n_sur}명({rate:.1%}) 생존 예측 ({best.strategy})"
        elif is_class_stat and test_meta is not None:
            lines = []
            for cls in sorted(test_meta["pclass"].unique()):
                mask = test_meta["pclass"] == cls
                n, n_sur, rate = predict_subset(mask)
                lines.append(f"{cls}등석({n_sur}/{n}명 {rate:.1%})")
            reply = (
                f"등급별 생존 예측({best.strategy}): {', '.join(lines)}. "
                f"전체 {n_test}명 중 {n_sur_all}명({rate_all:.1%}) 생존 예측."
            )
        # ── 인텐트 기반 응답 ──
        elif intent == "TITANIC_FACTS":
            reply = (
                f"1912년 4월 15일 빙산 충돌로 침몰. "
                f"{best.strategy} 모델이 미확인 승객 {n_test}명 중 "
                f"{n_sur_all}명({rate_all:.1%}) 생존을 예측합니다."
            )
        elif intent == "SURVIVAL_PREDICT":
            male_rate = None
            female_rate = None
            if test_meta is not None:
                _, _, male_rate = predict_subset(test_meta["gender"] == "male")
                _, _, female_rate = predict_subset(test_meta["gender"] == "female")
            reply = (
                f"{best.strategy} 기준 미확인 승객 {n_test}명 중 {n_sur_all}명({rate_all:.1%}) 생존 예측. "
                + (f"여성 {female_rate:.1%}, 남성 {male_rate:.1%}." if female_rate is not None else "")
            )
        elif intent == "STATISTICS" and test_meta is not None:
            lines = []
            for cls in sorted(test_meta["pclass"].unique()):
                mask = test_meta["pclass"] == cls
                n, n_sur, rate = predict_subset(mask)
                lines.append(f"{cls}등석({n_sur}/{n}명 생존 예측)")
            reply = (
                f"미확인 승객 {n_test}명 — 생존 {n_sur_all}명({rate_all:.1%}). "
                f"등급별: {', '.join(lines)}. ({best.strategy})"
            )
        elif intent == "MODEL_TRAIN":
            trained = train_result.get("trained_models", [])
            reply = (
                f"총 {len(trained)}개 모델 훈련 완료. "
                f"최고 성능: {best.strategy} (정확도 {best.accuracy:.1%})"
            )
        else:
            reply = (
                f"{best.strategy} 모델 기준 미확인 승객 {n_test}명 중 "
                f"{n_sur_all}명({rate_all:.1%}) 생존 예측. 정확도 {best.accuracy:.1%}."
            )

        logger.info(f"[SmithCaptainInteractor] chat 완료 | intent={intent} best={best.strategy} accuracy={best.accuracy:.1%}")
        return SmithChatResponse(reply=reply)
    
    
    
    async def introduce_myself(self, schemas: SmithCaptainSchema) -> SmithCaptainResponse:
        return await self._repository.introduce_myself(SmithCaptainQuery(
            id=schemas.id,
            name=schemas.name,
        ))


