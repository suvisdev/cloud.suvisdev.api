# gildle — 반려견 사계절 산책로 매칭 (헥사고날 · Clean · DDD)

길(가로수길) + 엮다 = "길을 엮다". 서울 기준으로 봄·가을엔 가로수(벚나무/느티나무)길을
우대하고, 겨울엔 결빙 사고 다발지역을 회피하는 반려견 친화 보행 경로를 계산한다.

## 아키텍처 컨벤션

`apps/titanic` 레이어 구조를 그대로 따른다(저장소 표준). 프롬프트 원안의
`application/`·`adapters/`(복수)·`domain/services` 대신 레포 컨벤션에 맞췄다.

```
gildle/
├── domain/                      # 순수 도메인 (외부 의존 0)
│   ├── value_objects/           # Coordinate, TreeSpecies, SeasonMode, RouteWeight, RouteEdge
│   ├── entities/                # TreeSegment, HazardZone (from_orm 팩토리)
│   └── services/                # RouteWeightCalculator (모드별 가중치 규칙)
├── app/
│   ├── ports/input/             # *_use_case.py (ABC)
│   ├── ports/output/            # Repository/Geocoding/Graph 포트 (ABC)
│   └── use_cases/               # *_interactor.py (생성자 주입)
├── adapter/
│   ├── inbound/api/             # FastAPI Router + schemas (gildle_router 집약)
│   └── outbound/                # CSV·Kakao(httpx)·NetworkX 어댑터 + SQLAlchemy ORM
├── dependencies/                # *_provider.py (Composition Root: 구체 어댑터 조립)
└── data/                        # 데모용 샘플 데이터
```

의존 방향: Router → 입력 포트(ABC) → Interactor → 출력 포트(ABC) → 어댑터 → DB/외부.
도메인은 `pandas`/`networkx`/`httpx`/`fastapi`를 import하지 않는다(DIP). 구체 어댑터를
아는 곳은 `dependencies/*_provider.py`(+`main.py`)뿐이다.

## 엔드포인트

`main.py`에서 `gildle_router`를 `prefix="/api"`로 include → 실제 경로는 `/api/gildle/...`.

| 메서드 | 경로 | 유스케이스 |
|--------|------|------------|
| POST | `/api/gildle/routes` | CalculateDogFriendlyRoute |
| GET  | `/api/gildle/map-data?mode=spring_autumn` | GetMapVisualizationData |

예시:

```bash
curl -X POST localhost:8000/api/gildle/routes \
  -H 'Content-Type: application/json' \
  -d '{"start_lat":37.5260,"start_lng":126.9245,"end_lat":37.5270,"end_lng":126.9290,"mode":"spring_autumn"}'
# {"path":["N1","N2","N5"]}   (봄/가을: 벚나무 '여의대로' 30% 감면 경로)

curl 'localhost:8000/api/gildle/map-data?mode=winter_safety'
```

## 데이터 소스 (가정)

- 가로수: data.go.kr "전국가로수길정보표준데이터"(서울 자치구). 시작/종료 위경도 포함.
- 결빙구간: 한국도로교통공단 "결빙 교통사고 다발지역". `시도='서울특별시'` 필터.
- 보행로 그래프: 운영은 OpenStreetMap(osmnx, `network_type='walk'`). 현재는
  `data/sample_walk_graph.json`이 그 자리를 대신한다(데모/테스트용).

> **CSV 컬럼명 가정:** 실제 다운로드 헤더와 다르면 각 어댑터 상단의 `_COL_*` 상수만
> 맞추면 된다. Kakao geocoding은 `KAKAO_API_KEY` 환경변수 + 좌표 결측 보완 fallback 전용.
> CSV/그래프 경로는 `GILDLE_TREE_CSV` / `GILDLE_HAZARD_CSV` / `GILDLE_WALK_GRAPH`로 덮어쓴다.

## 테스트

```bash
cd suvisdev
python -m pytest apps/gildle/tests -q   # 83 passed
```

TDD(Red→Green)로 도메인 → 애플리케이션 → 어댑터 → 인바운드 순으로 구현했다.
