# 왓슨(Watson) 인바운드 트리아지 — 구조 · 구현 현황

> dispatch가 외부 채널(Email·Telegram·Discord)로부터 받은 이벤트를 1차 분류(Triage)해서
> 일반 업무는 내부에서 종결하고, 중요/보고서 요청은 상위 허브로 격상(Escalation)하는 파이프라인.

---

## 1. 아키텍처 컨텍스트

허브 앤 스포크(Hub-and-Spoke) 구조. 실제 패키지명 기준:

- **Hub — `ontology/`**: 온톨로지·이 4벤트 버스. `ontology.domain.events.spoke_events`에 Spoke 공용 이벤트 타입(`InboundMessageEvent`)을 정의하고, `ontology.app.use_cases.hub_report_orchestrator.HubReportOrchestrator`가 격상된 이벤트를 처리한다.
- **최고 사령탑 — `core/lol/t1_mid_faker_orchestrator.py`**: `T1MidFakerOrchestrator`. Ollama로 로컬 실행 중인 `exaone3.5:2.4b` 모델을 호출하는 오케스트레이터("페이커/Faker").
- **Communication Spoke — `dispatch/`**: Email·Telegram·Discord 등 외부 채널 인바운드/아웃바운드를 전담.
- **기타 Spoke**: `titanic/`, `silicon_valley/` 등.

> `star_craft`라는 이름은 `ontology/_docs/star-craft-pipeline.md`에 정리된 **향후 확장 계획**(Neo4j·Qdrant 기반 RAG 파이프라인)의 코드네임일 뿐, 실제 동작하는 Hub 패키지명은 `ontology`다. 코드에서 `star_craft`를 import하는 곳은 없다.

---

## 2. 라우팅 기준

`DetectiveWatsonWatcherHub._needs_escalation()` (`dispatch/adapter/inbound/watcher/detective_watson_watcher_hub.py`)이 실제 판단 로직이다.

- **Case A (일반)**: `important_client=False`이고 본문에 에스컬레이션 키워드가 없는 경우
  ➔ `HolmesInteractor.resolve()` (`dispatch/app/use_cases/holmes_interactor.py`)가 자체 종결.
- **Case B (중요/에스컬레이션)**: `important_client=True`이거나, 본문에 `_ESCALATION_KEYWORDS = ("보고서", "리포트", "report", "실적", "발행")` 중 하나라도 포함된 경우
  ➔ `HubReportOrchestrator.escalate()` (`ontology/app/use_cases/hub_report_orchestrator.py`)가 EXAONE을 호출해 보고서 초안 생성.

---

## 3. 실제 구현 파일

### 3.1 왓슨 코어 로직 (콘솔 테스트로 시작한 부분)

| 역할 | 파일 |
|------|------|
| 왓슨(Triage) | `dispatch/adapter/inbound/watcher/detective_watson_watcher_hub.py` — `DetectiveWatsonWatcherHub` |
| 홈즈(일반 업무) | `dispatch/app/use_cases/holmes_interactor.py` — `HolmesInteractor` |
| 페이커 격상 파이프라인 | `ontology/app/use_cases/hub_report_orchestrator.py` — `HubReportOrchestrator` |
| 이벤트 타입 | `ontology/domain/events/spoke_events.py` — `InboundMessageEvent` |
| 수동 테스트 하네스 | `dispatch/test/harness_watson_triage.py` — `python -m dispatch.test.harness_watson_triage`로 콘솔에서 Case A/B 시나리오 확인 가능 |

### 3.2 HTTP 진입점 (`watcher_router.py`)

Titanic Smith Captain 기준선과 동일한 레이어 구조로 노출된 자기소개 엔드포인트:

```text
GET /api/v1/dispatch/watcher/myself
```

| 레이어 | 파일 |
|--------|------|
| Router | `dispatch/adapter/inbound/api/v1/watcher_router.py` |
| Schema | `dispatch/adapter/inbound/api/schemas/watcher_schema.py` — `WatcherIntroduceSchema` |
| Dto | `dispatch/app/dtos/watcher_dto.py` — `WatcherIntroduceQuery` / `WatcherIntroduceResponse` |
| Input Port | `dispatch/app/ports/input/watcher_use_case.py` — `WatcherUseCase` |
| Interactor | `dispatch/app/use_cases/watcher_interactor.py` — `WatcherInteractor` |
| Output Port | `dispatch/app/ports/output/watcher_port.py` — `WatcherPort` |
| Repository | `dispatch/adapter/outbound/repositories/watcher_repository.py` — `WatcherRepository` |
| DI | `dispatch/dependencies/watcher_provider.py` |

> `watch`/`escalate` 실행 엔드포인트(POST)는 아직 HTTP로 노출하지 않았다 — 지금은 `/myself` 자기소개만 있다. 왓슨의 실제 트리아지 로직을 API로 열려면 3.1의 컴포넌트들을 위 레이어 구조에 맞춰 Router→Interactor→Repository로 다시 감싸야 한다 (스키마: `channel`·`sender`·`body`·`important_client` 입력 → `resolution` 출력).

### 3.3 형제 스캐폴딩 — `judge_router.py`

동일 패턴을 그대로 복제한 예시. `GET /api/v1/dispatch/judge/myself`만 구현되어 있고, 실제 판정(judge) 로직은 아직 없다. 새 채널/에이전트를 추가할 때 이 두 라우터를 템플릿으로 복사하면 된다.

---

## 4. 알려진 한계

- `HubReportOrchestrator`가 EXAONE(`exaone3.5:2.4b`)으로 보고서를 생성할 때, 소형 로컬 모델 특성상 `[날짜]`, `**굵게**` 같은 플레이스홀더·마크다운이 응답에 남는 경우가 있다 (`send_email_interactor.py`에 적용한 `_sanitize_body()` 같은 후처리가 이쪽에는 아직 없음).
- Escalation 판단은 키워드 매칭(`_ESCALATION_KEYWORDS`)뿐이라 의도 파악이 정교하지 않다.
