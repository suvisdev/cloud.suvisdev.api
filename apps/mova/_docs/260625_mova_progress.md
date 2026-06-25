# Mova 진행 상태 점검 보고서

> **점검일:** 2026-06-25
> **대상:** `suvisdev/apps/mova/` (백엔드, Clean Architecture + Hexagonal)
> **방법:** 파일 시스템 직접 탐색 (레이어별 파일 존재·라인 수·코드 내용 확인)
> **갱신(2026-06-25):** picks 도메인 레이어 완성 + `RecommendationPort`·`UserPreferenceQueryPort` 도입으로 Phase 2 미비 항목 해소 (§3·§5 반영).
> **갱신(2026-06-25 #2):** rankings `chat_trend` 집계 Use Case 완료 + LLM 어댑터 예외 경계 정돈(`gemini_client` → 도메인 예외) 완료 + `tests/` 신설 (§3·§4·§5·§7 반영).

---

## 프로젝트 컨텍스트 (이 문서를 처음 보는 사람/AI용)

- **Mova** = 영화·시리즈 추천 플랫폼의 백엔드 도메인 앱. 채팅으로 취향을 말하면 Gemini가 작품을 추천한다.
- **스택:** Python · FastAPI · SQLAlchemy 2.0(async) · PostgreSQL(Neon) · Google Gemini.
- **아키텍처:** Clean Architecture + Hexagonal(Ports & Adapters). 요청 흐름은
  `Router(Schema) → Input Port(UseCase ABC) → Interactor → Output Port(Repository ABC) → PgRepository(ORM) → DB`.
  도메인 코어는 FastAPI·DB·HTTP에 의존하지 않으며, 구현체(Adapter)는 `adapter/`에 둔다.
- **레이어 용어:** *Entity/VO* = 도메인 모델, *Port* = 추상 인터페이스(ABC), *Interactor* = 유스케이스 구현(얇게 유지),
  *PgRepository* = DB 어댑터, *DTO/Command* = 레이어 간 데이터 객체, *provider* = FastAPI 의존성 주입(DI).
- **기준 구현:** `apps/titanic/` 앱이 헥사고날 기준선이고, Mova는 동일 레이어 규칙을 따른다.
- **이 문서의 목적:** Mova 백엔드의 Phase별 완료/미완 현황과 다음 작업 순서를 한 장에 정리한 스냅샷.

---

## 0. 핵심 요약 (TL;DR)

| 구분 | 상태 |
|------|------|
| **Phase 1** (영화 카탈로그: movies·actors·characters·tags·assistants) | ✅ **완료** — 전 레이어 구현, 스키마도 ERD와 일치 |
| **Phase 2** (chat 추천) | ✅ 채팅 추천 동작 + LLM 출력 포트 추상화·콜드스타트 포트·picks 도메인 엔티티 **완료** (2026-06-25) |
| **Phase 3** (reviews·rankings·collections) | 🚧 reviews ✅ / rankings **`chat_trend` 집계 Use Case 완료**(2026-06-25) / collections는 **ORM 테이블만** |

**먼저 알아둘 점 2가지**
1. **네이밍 컨벤션 변경됨** — 코드는 도메인 그룹 접두사(`studio_`/`market_`/`platform_`)를 사용. 일부 문서(ERD·CLAUDE.md)는 옛 짧은 이름을 그대로 참조 → **문서 경로 stale** (§6).
2. **얇은 인터랙터(10~13줄)는 스텁이 아님** — 아키텍처 규칙(Interactor 얇게, 로직은 Repository)대로 구현된 **완성된 위임 인터랙터**.

**네이밍 매핑**

| 그룹 | 의미 | 도메인 |
|------|------|--------|
| `studio_` | 콘텐츠/카탈로그 | movies, actors, characters, tags, search, import |
| `market_` | 추천/시장 | chat, picks, collections, rankings, reviews |
| `platform_` | 계정/페르소나 | assistants, users, admins, groups |

---

## 1. 폴더 구조 & titanic 비교

```
apps/mova/
├── adapter/
│   ├── inbound/api/{schemas, v1}/      # studio_*/market_*/platform_*
│   └── outbound/
│       ├── orm/   studio_(movies,actors,characters,tags)
│       │          market_(chat,picks,collections,rankings,reviews)
│       │          platform_(assistants,users,admins,groups) + base_orm
│       ├── pg/    *_pg_repository (11)
│       ├── llm/   gemini_client, intent_extraction(310), chat_prompt(124), chat_reply(165)
│       └── http/  kofic_adapter, tmdb_adapter
├── app/{dtos, ports/{input,output}, use_cases}/
├── dependencies/   *_provider (11)
├── domain/{entities(13), value_objects(13)}
└── _docs/
```

| 항목 | titanic (기준선) | mova | 비고 |
|------|------------------|------|------|
| 헥사고날 레이어 | ✅ | ✅ | 동일 규칙 |
| 리포지토리 폴더 | `repositories/` | **`pg/`** | mova는 `suvisdev/CLAUDE.md` C.4 템플릿(pg/) 준수 |
| 매퍼 | `mappers/` | **없음** | pg에 인라인 매핑 |
| 외부 어댑터 | `ml/` | **`llm/`, `http/`** | Gemini·KOFIC·TMDB |
| **`tests/`** | **있음** | **✅ 있음** | collections·chat_trend 랭킹·LLM 예외 핸들링 (2026-06-25) |

---

## 2. Phase 1 — 영화 카탈로그 ✅

| 항목 | 실제 파일 | 상태 |
|------|-----------|:---:|
| movies ORM | `studio_movies_orm.py` | ✅ |
| actors ORM | `studio_actors_orm.py` | ✅ |
| characters ORM | `studio_characters_orm.py` | ✅ |
| tags ORM | `studio_tags_orm.py` | ✅ |
| assistants ORM | `platform_assistants_orm.py` | ✅ |
| Movie Entity + VO | `studio_movies_entity/_vo.py` | ✅ |
| Actor Entity + VO | `studio_actors_entity/_vo.py` | ✅ |
| Character Entity + VO | `studio_characters_entity/_vo.py` | ✅ |
| Tag Entity + VO | `studio_tags_entity/_vo.py` | ✅ |
| Assistant Entity + VO | `platform_assistants_entity/_vo.py` | ✅ |
| Repository Port/Adapter (movies·actors·characters·tags·assistants) | ports/output + pg 전부 | ✅ |
| Use Cases (GetMovieDetail·SearchMovies·GetActor 등) | movies·search·actors·characters·tags 인터랙터 | ✅ |
| Schema/DTO | studio_* schema + dto 전부 | ✅ |
| Router | studio_*_router 전부 | ✅ |
| MOVA_ERD.md 동기화 | 스키마 ✅ / 파일 경로 stale | 🚧 |

---

## 3. Phase 2 — chat 추천 ✅

| 항목 | 실제 | 상태 |
|------|------|:---:|
| chat ORM + Entity + Repository | `market_chat_orm`·`_entity`·`_repository`(43)+pg | ✅ |
| picks ORM + Entity + Repository | ORM·port·pg ✅ + **Entity·VO 추가** — `market_picks_entity`(PickEntity, `from_orm`) · `_vo`(PickRank 1~3, Feedback) | ✅ |
| RecommendationPort + GeminiRecommendationAdapter | **`llm_output_port.py`(ABC) + `gemini_recommendation_adapter.py` 도입** — ChatInteractor가 포트 경유 (DIP 해소) | ✅ |
| UserPreferenceQueryPort (콜드스타트) | **`user_preference_query_port.py`(ABC) + `user_preference_pg_repository.py` 분리** — `UserPreferenceDto`(empty/has_genre_signal) | ✅ |
| 채팅 추천 Use Case | `market_chat_interactor`(의도추출→검색→포트 추천→chat/picks 저장) | ✅ |

> 핵심 채팅 추천 동작 + `mova/_docs/CLAUDE.md` B.4("Interactor는 LLM Output Port 경유") **적용 완료**. 추천 신호 고도화(콜드스타트 분기 등)는 후속 과제.

---

## 4. Phase 3 — reviews·rankings·collections 🚧

| 항목 | 실제 | 상태 |
|------|------|:---:|
| reviews ORM + Entity | `market_reviews_orm`·`_entity`(+port 33·interactor 31) | ✅ |
| rankings ORM + Entity | `market_rankings_orm`·`_entity`·`_vo` | ✅ 스키마 |
| rankings `chat_trend` 집계 Use Case | `GenerateChatTrendRankingUseCase`/Interactor + `aggregate_chat_trend`/`save_chat_trend_ranking` + `POST /rankings/refresh` | ✅ **완료**(2026-06-25) — picks×chat.hit_count 가중합·오늘자 스냅샷 덮어쓰기. box_office(KOFIC) 미변경 |
| collections ORM + Entity | `market_collections_orm.py`(17줄) ✅ / **Entity·VO·Repo·UseCase·Router 전부 ❌** | 🚧 |

> collections는 ORM 테이블만 존재(movies.collection_id FK 타깃).

---

## 5. 다음 작업 순서 (FK 의존성 + 가치 기준)

FK 루트: `collections → movies → (characters/tags/rankings/reviews/picks)`, `chat → picks/rankings`, `users → chat/reviews/picks`.

**완료 (2026-06-25):**
- ~~picks Entity + VO~~ ✅ `PickEntity`(`from_orm`) · `PickRank`(1~3) · `Feedback`(like/dislike/null)
- ~~LLMOutputPort(RecommendationPort) 추상화~~ ✅ `RecommendationPort` + `GeminiRecommendationAdapter` (DIP 해소)
- ~~UserPreferenceQueryPort(콜드스타트)~~ ✅ 전용 쿼리 포트 분리 + `UserPreferenceDto`
- ~~rankings `chat_trend` 집계 Use Case~~ ✅ picks×chat.hit_count 가중합 → 오늘자 스냅샷 덮어쓰기 + `POST /rankings/refresh`
- ~~LLM 어댑터 예외 경계 정돈~~ ✅ `gemini_client` HTTPException → 도메인 예외(`LLMError` 등), 전역 핸들러 단일 변환

**남은 작업:**
1. **collections 풀스택** (Entity→Repo→UseCase→Router) — FK 타깃·시리즈 그룹화. movies는 collection 없이 동작하므로 우선순위 낮음.
2. **ERD·CLAUDE.md 파일 경로 동기화** (§6).
3. *(선택)* picks 읽기 메서드(`PickEntity` 소비처 생성) · rankings 집계 SQL의 DB 통합 테스트(현재 Use Case 단위 테스트만) · `chat_trend` 정기 실행(스케줄러) 연동.

---

## 6. MOVA_ERD.md 동기화 상태

- **테이블 스키마(컬럼·관계·제약):** 코드와 **동기화됨** ✅
- **"ORM 매핑" 표 파일 경로:** **stale** ❌ — 10개 중 8개 옛 이름

| 테이블 | ERD 표기 | 실제 파일 | 일치 |
|--------|----------|-----------|:---:|
| movies | `studio_movies_orm.py` | 동일 | ✅ |
| collections | `market_collections_orm.py` | 동일 | ✅ |
| actors | `actors_orm.py` | `studio_actors_orm.py` | ❌ |
| characters | `characters_orm.py` | `studio_characters_orm.py` | ❌ |
| tags | `tags_orm.py` | `studio_tags_orm.py` | ❌ |
| rankings | `rankings_orm.py` | `market_rankings_orm.py` | ❌ |
| chat | `chat_orm.py` | `market_chat_orm.py` | ❌ |
| picks | `picks_orm.py` | `market_picks_orm.py` | ❌ |
| reviews | `reviews_orm.py` | `market_reviews_orm.py` | ❌ |
| assistants | `assistants_orm.py` | `platform_assistants_orm.py` | ❌ |

> 같은 stale 경로가 `suvisdev/CLAUDE.md`(J절)·`mova/_docs/CLAUDE.md`(A절)에도 존재. 파일 리네이밍 후 문서 경로 미갱신.

---

## 7. 2026-06-25 작업 로그

### 7.1 rankings `chat_trend` 집계 Use Case
- 흐름: `POST /mova/rankings/refresh?source=chat_trend&days=N&limit=K` → `aggregate_chat_trend`(최근 N일 picks 횟수 + `chat.hit_count` 합산 상위 K) → `chat_trend_score`(가중 `pick×3+hit×1`)로 랭크 → `save_chat_trend_ranking`(오늘자 스냅샷 덮어쓰기).
- 결정: 덮어쓰기는 오늘자(`ranked_at=today`) 행만 삭제(일별 히스토리 보존), 대표 `chat_id`는 None 단순화, box_office/KOFIC·마이그레이션 미변경.
- 파일: `market_rankings_vo`/`_dto`/output·input port/`market_rankings_pg_repository`/`market_rankings_interactor`/`market_rankings_provider`/`market_rankings_schema`/`market_rankings_router` + `tests/test_chat_trend_ranking_interactor.py`.

### 7.2 LLM 예외 어댑터 경계 정돈 (CLAUDE.md E.3 / B.4)
- 아웃바운드 `gemini_client`가 FastAPI `HTTPException`에 의존하던 구조 → `app/exceptions.py`의 도메인 예외(`LLMError`/`LLMTimeoutError`/`LLMUnavailableError`)로 교체, `fastapi` import 제거.
- HTTP 변환은 `adapter/inbound/api/exception_handlers.py`의 전역 핸들러 한 곳에서만(`main.py`가 등록). `gemini_reply` 세 호출처(mova chat·main `/chat`·titanic) 모두 기존 상태코드(429/502/400/503)·메시지 보존.
- 파일: `app/exceptions.py`(신규)·`gemini_client.py`·`exception_handlers.py`(신규)·`main.py` + `tests/test_llm_error_handling.py`.

### 7.3 검증
- `pytest apps/mova/tests/` → **16 passed**. `apps/mova/adapter/outbound/`에 `fastapi`/`HTTPException` 의존 0건.

---

*본 보고서는 2026-06-25 시점 코드 기준이며, 이후 변경 시 재점검이 필요합니다.*
