# Watson 트리아지 하네스 명세 (실제 코드베이스 매핑판)

> 원본 스펙은 은유적 코드네임으로 작성되어 있었다. 본 문서는 이를 **이 저장소의 실제 앱·모듈 이름**에 매핑한 버전이다.
> Karpathy 원칙(단순성 우선)에 따라 프로덕션 라우트는 건드리지 않고 **독립 실행 테스트 하네스**로 구현한다.

## 1. 코드네임 → 실제 매핑

| 스펙 코드네임 | 실제 코드베이스 | 비고 |
|---|---|---|
| Faker / EXAONE (최고 사령탑) | `core/lol/t1_mid_faker_orchestrator.py` | 그대로 존재 |
| `star_craft/` (온톨로지 버스) | `apps/ontology/` | Hub. DB명이 `starcraft` |
| `sherlock_homes/` (커뮤니케이션 스포크) | `apps/dispatch/` | email·telegram·discord 일치 |
| Watson (Watcher Hub) | `dispatch/adapter/inbound/watcher/detective_watson_watcher_hub.py` | 신규 |
| Holmes (Case A 처리) | `dispatch/app/use_cases/holmes_interactor.py` | 신규 |
| 인바운드 이벤트 | `ontology/domain/events/spoke_events.py :: InboundMessageEvent` | 신규 |

## 2. 라우팅 기준 (Watson Triage)

- **Case A (일반)**: 일반 거래처 · 단순 문의 → `HolmesInteractor.resolve()`가 dispatch 내부에서 종결.
- **Case B (중요/에스컬레이션)**: `important_client=True` 이거나 본문에 보고서 키워드(`보고서·리포트·report·실적·발행`) 포함
  → `HubReportOrchestrator.escalate()`가 온톨로지 버스를 경유해 페이커(EXAONE)를 기상시켜 보고서 생성.

## 3. 스타-토폴로지 준수

```
Watson(dispatch/Spoke) ──▶ Holmes(dispatch 내부)                        # Case A
Watson(dispatch/Spoke) ──▶ HubReportOrchestrator(ontology/Hub) ──▶ Faker(core/lol)   # Case B
```

- Spoke → Hub ✅ · Hub → core ✅ · Spoke 간 직접 import ❌ (해당 없음)
- `.importlinter` 계약(hub-independence, spoke-independence) 위반 없음.

## 4. 실행

```bash
cd suvisdev
python -m dispatch.test.harness_watson_triage
```

- Mock 이벤트 2종(일반 telegram / VIP discord)이 Watson → Holmes 또는 Watson → 온톨로지 → Faker로 흐르며,
  전체 멀티에이전트 저니가 콘솔 서사 로그로 출력된다.
- EXAONE(Ollama)이 미가동이면 `HubReportOrchestrator`가 폴백 보고서로 대체하므로 하네스는 항상 완주한다.

## 5. 관련 파일

| 역할 | 경로 |
|------|------|
| 인바운드 이벤트 | `apps/ontology/domain/events/spoke_events.py` |
| Hub 격상 오케스트레이터 | `apps/ontology/app/use_cases/hub_report_orchestrator.py` |
| Holmes (Case A) | `apps/dispatch/app/use_cases/holmes_interactor.py` |
| Watson (Watcher Hub) | `apps/dispatch/adapter/inbound/watcher/detective_watson_watcher_hub.py` |
| 하네스 실행 스크립트 | `apps/dispatch/test/harness_watson_triage.py` |
