# Mova 앱 — 영화·채팅·랭킹·리뷰 도메인

> **역할:** 영화 저장·조회·채팅·리뷰·랭킹 등 Mova 도메인 API.  
> **상위 문서:** [백엔드 CLAUDE.md](../../../../vault/suvisdev/CLAUDE.MD) — 아키텍처 전체 규칙

Titanic(James)과 **동일한 레이어 규칙**을 따른다. 아래는 Mova만의 특이점만 기록한다.

---

## A. 참조 파일

| 역할 | 파일 |
|------|------|
| Router + invoke | `adapter/inbound/api/v1/movies_router.py` |
| Input Port | `app/ports/input/movies_use_case.py` |
| Interactor | `app/use_cases/movies_interactor.py` |
| Dto | `app/dtos/movies_dto.py`, `actors_dto.py` |
| DI | `dependencies/movies_provider.py` |
| Router 집약 | `adapter/inbound/api/__init__.py` → `mova_router` |
| LLM 어댑터 | `adapter/outbound/llm/gemini_client.py` |
| ERD | [`MOVA_ERD.md`](MOVA_ERD.md) |

---

## B. Mova 특이점

### B.1 Dto → Schema 변환 (Titanic과 다름)

Mova는 Dto와 HTTP 응답 Schema가 분리되어 있다.  
Router에서 반드시 `Dto.to_schema()`를 호출한다.

```python
# mova router (표준)
return (await movies.save_movie(req)).to_schema()
```
### B.2 DB 세션

```python
from core.matrix.grid_oracle_database_manager import get_mova_db  # Mova DB
```

### B.3 Cross-metadata FK (Viewer 의존)

`chat`, `picks`, `reviews` 테이블이 `users.id`를 FK로 참조한다.  
문자열 `"users.id"` 대신 반드시:

```python
from viewer.app.dtos.user_model import User
ForeignKey(User.__table__.c.id)
```

`create_tables()` 순서상 **Viewer(SecomBase)가 먼저** 생성된 뒤 Mova(MovaBase)가 생성된다.

### B.4 LLM (Gemini)

- LLM 호출은 `adapter/outbound/llm/gemini_client.py` — outbound adapter.
- Router나 Interactor에서 직접 Gemini API 호출 금지.
- Interactor는 LLM Output Port를 통해 호출한다.

### B.5 Router 집약

```python
# adapter/inbound/api/__init__.py
from mova.adapter.inbound.api.v1.movies_router import movies_router
# ...
mova_router = APIRouter()
mova_router.include_router(movies_router)
```

`main.py`에서 `mova_router`를 prefix `/mova`로 include한다.

---

## C. 앱 내 도메인 목록

| 도메인 | Router prefix | 담당 |
|--------|---------------|------|
| Movies | `/mova/movies` | 영화 CRUD |
| Characters | `/mova/characters` | 배우·캐릭터 |
| Reviews | `/mova/reviews` | 리뷰 |
| Picks | `/mova/picks` | 찜 |
| Chat | `/mova/chat` | LLM 채팅 |
| Ranking | `/mova/ranking` | 랭킹 집계 |

---

## D. 금지·안티패턴 (Mova 추가)

| ❌ 금지 | ✅ 대신 |
|--------|--------|
| Router에서 `Dto` 직접 반환 (Mova는 Schema 계약) | `Dto.to_schema()` 호출 후 반환 |
| Interactor에서 Gemini API 직접 호출 | `LLMOutputPort` 경유 |
| `"users.id"` 문자열 FK | `ForeignKey(User.__table__.c.id)` |
| Mova 테이블을 Viewer보다 먼저 생성 | `create_tables()` 순서 유지 |
