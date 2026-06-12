# cloud.suvisdev 백엔드 인수인계

> **대상:** Claude Code·Cursor 등 코딩 에이전트.  
> **목적:** Clean Architecture + Hexagonal + FastAPI + SOLID(SRP·ISP·DIP) 규칙을 한 문서에서 인수인계한다.  
> **기준 구현:** `apps/titanic/` (James/Walter) — Mova·Viewer는 **동일 레이어 규칙**으로 맞춘 상태.  
> **상위 원칙:** [루트 CLAUDE.md](../CLAUDE.md) — Karpathy 네 원칙 (항상 유효)

---

## A. 에이전트가 코드를 쓰기 전에 읽을 것

| 순서 | 문서 | 용도 |
|------|------|------|
| 1 | **본 파일** (`suvisdev/_claude/CLAUDE.md`) | 아키텍처·레이어·SOLID·패턴 |
| 2 | `.cursorrules` | Cursor 하네스 요약 |
| 3 | `_claude/ENTITY_RULE.md` | PK `id` int 자동증감 |
| 4 | `apps/mova/_docs/MOVA_ERD.md` | Mova 테이블 관계 (해당 시) |
| 5 | `AGENTS.md` | 앱별 경로·삭제된 옛 경로 금지 목록 |

**규칙 문서를 읽지 않고 관례를 추측하여 구현하지 않는다.**

### 충돌 시 우선순위

1. 사용자의 **더 구체적·최근** 지시  
2. **`_claude/`** · **`apps/*/_docs/`** 내 해당 영역 규칙 MD  
3. 본 `CLAUDE.md` 백엔드 인수인계  
4. `.cursorrules` 요약  

Karpathy 네 원칙(묵시적 가정 금지·최소 diff)은 **항상** 유지한다.

---

## B. 저장소 앱 구조 (`apps/`)

| 앱 | 역할 | 표준 참조 |
|----|------|-----------|
| `titanic/` | CSV 업로드(James)·조회(Walter) — **헥사고날 기준선** | [`titanic/_docs/CLAUDE.md`](apps/titanic/_docs/CLAUDE.md) |
| `mova/` | 영화·채팅·랭킹·리뷰 등 도메인 API | James와 **동일 레이어** |
| `viewer/` | 인증(`groups`, `admins`, `users`) — login/signup | James와 **동일 레이어** |

- **인증은 `viewer/`** — `friday13th`는 수업용, 프로덕션 login/signup은 viewer만 사용.
- **DB:** Neon PostgreSQL. Mova·Viewer(Secom)는 동일 DB URL을 공유하는 경우가 많음 (`DATABASE_URL` / `MOVA_DATABASE_URL` / `SECOM_DATABASE_URL`).
- **진입점:** `main.py` — lifespan에서 `verify_connection()` → `create_tables()` → `seed_secom_if_empty()`.

---

## C. 아키텍처: Clean Architecture + Hexagonal (Ports & Adapters)

### C.1 개념

- **Clean Architecture:** 의존 방향은 **바깥 → 안쪽**. 도메인(앱 코어)은 FastAPI·SQLAlchemy·HTTP에 의존하지 않는다.
- **Hexagonal:** **입력 포트**(Use Case ABC)와 **출력 포트**(Repository ABC)로 외부와 연결. 구현체(Adapter)는 `adapter/`에 둔다.

### C.2 표준 요청 흐름 (James = Mova = Viewer)

```text
[Inbound Adapter]  Router (FastAPI)
       │  Schema in
       ▼
[Input Port]         XxxUseCase (ABC)     ← Schema in, Dto out
       │
       ▼
[Application]      XxxInteractor        ← Schema → Command → Repository
       │
       ▼
[Output Port]      XxxRepository (ABC)  ← Command in
       │
       ▼
[Outbound Adapter] XxxPgRepository      ← ORM read/write
       │
       ▼
[DB]               PostgreSQL (Neon)
```

**응답 경로 (Mova·Viewer):**

```text
ORM row → Dto.from_orm() → Interactor 반환
       → Router에서 Dto.to_schema() → HTTP JSON (OpenAPI response_model)
```

**James/Walter 예외:** 응답 DTO(`JamesResponse`, `WalterResponse`)가 곧 HTTP 계약이면 router에서 **변환 없이** 반환해도 된다.

### C.3 레이어별 책임 (반드시 지킬 것)

| 레이어 | 위치 | 할 수 있는 것 | 하면 안 되는 것 |
|--------|------|---------------|-----------------|
| **Router** | `adapter/inbound/api/v1/*_router.py` | Schema 수신, `Depends`, `await use_case`, Dto→Schema | 비즈니스 로직, DB 직접 접근, Repository 직접 생성 |
| **Input Port** | `app/ports/input/*_use_case.py` | ABC, Schema in / Dto out 시그니처 | 구현 코드, DB |
| **Interactor** | `app/use_cases/*_interactor.py` | Schema→Command, port 호출, Dto 반환 | `to_schema()`, `HTTPException`, ORM import |
| **Output Port** | `app/ports/output/*_repository.py` | ABC, Command in | 구현 코드 |
| **PgRepository** | `adapter/outbound/pg/*_pg_repository.py` | Command 처리, ORM, `RepositoryError` | `HTTPException`, Use Case import |
| **ORM** | `adapter/outbound/orm/` 또는 `app/dtos/*_model.py` | 테이블 매핑 | Router·Interactor에서 직접 쓰지 않음(Repository 경유) |
| **Dto / Command** | `app/dtos/` | `from_schema`, `from_orm`, `to_schema`(Dto만) | HTTP·DB 세션 |
| **DI** | `dependencies/*_provider.py` | `get_*_use_case`, 구체 Repository→Interactor 조립 | 비즈니스 로직 |
| **Schema** | `adapter/inbound/api/schemas/` | Pydantic, OpenAPI | Repository·ORM |

### C.4 디렉터리 템플릿 (앱 하나 기준)

```text
apps/{app}/
├── adapter/
│   ├── inbound/api/
│   │   ├── __init__.py         # v1 라우터 집약 (`mova_router` lazy export)
│   │   ├── schemas/            # Pydantic Request/Response
│   │   └── v1/*_router.py      # FastAPI Router
│   └── outbound/
│       ├── pg/*_pg_repository.py
│       ├── orm/                # (mova/titanic) SQLAlchemy ORM
│       └── llm/                # (mova) Gemini 등 외부 LLM
├── app/
│   ├── dtos/                   # Command + Dto dataclass
│   ├── ports/
│   │   ├── input/*_use_case.py
│   │   └── output/*_repository.py
│   └── use_cases/*_interactor.py
└── dependencies/*_provider.py    # FastAPI Depends DI
```

---

## D. 데이터 객체 규칙

### D.1 종류와 역할

| 타입 | 예시 | 생성 | 사용처 |
|------|------|------|--------|
| **Schema** | `MovieCreateSchema`, `LoginSchema` | Pydantic | Router in, Input Port in, OpenAPI |
| **Command** | `MovieUpsertCommand`, `LoginUserCommand` | `from_schema()` | Interactor → Output Port → PgRepository |
| **Dto** | `MovieDto`, `LoginResponseDto` | `from_orm()` 또는 interactor 조립 | Input Port out, Interactor return |
| **ORM** | `MovaMovie`, `User` | SQLAlchemy | PgRepository 내부만 |

### D.2 변환 규칙

```python
# Interactor (표준)
command = MovieUpsertCommand.from_schema(payload)
row = await self._repository.upsert(command)
return MovieDto.from_orm(row)

# Router (Mova — HTTP 계약이 Schema일 때)
return (await movies.save_movie(req)).to_schema()

# Router (Titanic — DTO = HTTP 계약)
return await walter.introduce_myself(schema)  # WalterResponse
```

- **`model_dump()` → dict → Command** 패턴은 **금지**. 반드시 `Command.from_schema(schema)`.
- Interactor·Use Case 레이어에서 **`to_schema()` 호출 금지** — inbound adapter(Router) 책임.
- Command에 **`to_dict()` / `to_payload()`** 넣지 않음 — Repository는 Command 객체를 직접 받는다.
- Dto의 `to_schema()`는 **lazy import**로 Schema를 가져와 순환 import를 피한다 (`TYPE_CHECKING` + 메서드 내부 import).

### D.3 엔티티 PK (`ENTITY_RULE` 요약)

- 모든 테이블 PK: **`id`**, 타입 **`int`**, **자동 증가**.
- 비즈니스 키(`slug`, `username`)는 **UNIQUE 별도 컬럼**.
- FK: `{entity}_id` → `{table}.id`

---

## E. FastAPI 규칙

### E.1 Router

```python
@movies_router.post("/movies", response_model=MovieSchema, status_code=201)
async def save_movie(
    req: MovieCreateSchema,
    movies: MoviesUseCase = Depends(get_movies_use_case),
) -> MovieSchema:
    return (await movies.save_movie(req)).to_schema()
```

- Router는 **얇게(thin)** — 파라미터·DI·`await use_case`·Dto→Schema만.
- Use Case는 **전역 변수 주입 금지** — `Depends(get_*_use_case)`만 사용.
- `adapter/inbound/api/__init__.py`에서 `xxx_use_case = ...` 로 묶지 **않는다** (viewer 구식 패턴 제거됨).

### E.2 DI (`dependencies/*_provider.py`)

```python
def get_james_director(db: AsyncSession = Depends(get_db)) -> JamesUseCase:
    repository: JamesRepository = CrewJamesDirectorPgRepository(session=db)
    return CrewJamesDirectorInteractor(repository=repository)
```

- Interactor는 **Output Port(ABC)만** 생성자로 받는다 — 구체 PgRepository를 interactor 내부에서 `new` 하지 않는다.
- Mova: `get_db()` → `get_mova_db()`
- Viewer: `get_secom_db()`
- Interactor가 다른 Use Case가 필요하면 **Input Port**를 DI로 주입 (`MoviesInteractor` ← `CharactersUseCase`, `ReviewsUseCase`).

### E.3 예외 처리

- **Titanic·Mova:** Router에서 `await use_case` 직접 호출. PgRepository는 `HTTPException`을 쓰지 않는다.
- **Viewer:** Router에서 `await use_case` + `XxxRepositoryError` → `HTTPException` 변환 (Titanic/Mova와 동일한 thin router).
- 외부 LLM(Gemini): `mova/adapter/outbound/llm/gemini_client.py` — inbound adapter가 아닌 outbound adapter.

### E.4 async

- Repository·Use Case·Router handler: **`async def`**
- DB: SQLAlchemy 2.0 **async** (`AsyncSession`, `postgresql+psycopg://`)

---

## F. SOLID — 적용 현황

| 원칙 | 상태 | 본 프로젝트에서의 의미 |
|------|------|------------------------|
| **SRP** | ✅ 적용 | Router=HTTP, Interactor=유스케이스, Repository=persistence 각각 한 책임 |
| **ISP** | ✅ 적용 | 도메인별 `MoviesUseCase`, `LoginUseCase` 등 **작은 입력 포트** 분리 |
| **DIP** | ✅ 적용 | Interactor → Port ABC; `dependencies/`에서 구현체 주입 |
| **OCP** | 🔄 학습 중 | 새 import 소스·집계를 plugin으로 확장하는 구조는 **아직 의도적으로 미적용** |
| **LSP** | 🔄 학습 중 | Port 구현체 교체·계약 검증은 **아직 엄격히 강제하지 않음** |

**에이전트 지침:** OCP/LSP를 이유로 **과한 추상·팩토리·전략 패턴 남발 금지**. 요청 범위 안에서 SRP·ISP·DIP만 지키면 된다.

---

## G. 사용 중인 디자인 패턴

| 패턴 | 위치 | 설명 |
|------|------|------|
| **Ports & Adapters (Hexagonal)** | `app/ports/`, `adapter/` | Use Case·Repository ABC + inbound/outbound adapter |
| **Use Case / Interactor** | `*_use_case.py`, `*_interactor.py` | 애플리케이션 서비스; port 구현 |
| **Repository** | `*_repository.py`, `*_pg_repository.py` | 영속성 추상화 |
| **DTO** | `app/dtos/` | 계층 간 전달 객체 (Command / Response Dto) |
| **Command Object** | `*Command`, `*UpsertCommand` | 쓰기 요청을 Repository로 전달 |
| **Dependency Injection** | `dependencies/*.py`, FastAPI `Depends` | 구성(composition root) |
| **Adapter** | Router, PgRepository, LLM adapter | 외부 기술을 port에 맞게 변환 |
| **Factory (제한적)** | `get_*_session_factory()`, `from_schema` | 세션·객체 생성만; 범용 Abstract Factory 지양 |

---

## H. DB·스키마 관리

### H.1 `create_tables()` 순서 (`core/matrix/grid_oracle_database_manager.py`)

1. **Titanic** (`TitanicBase`)
2. **Viewer/Secom** (`SecomBase`) — `groups`, `admins`, `users` **먼저**
3. **Mova** (`MovaBase`) — `chat`/`picks`/`reviews`가 `users.id` FK 참조

### H.2 Cross-metadata FK

Mova ORM과 Viewer ORM은 **서로 다른 `DeclarativeBase`** 이다. 문자열 `"users.id"` FK 대신:

```python
ForeignKey(User.__table__.c.id)
```

### H.3 검증 스크립트

```powershell
cd suvisdev
python scripts/verify_db_tables.py
```

성공 시: `전체 PASS` — 연결, 14 public 테이블, cross-FK, secom seed 확인.

### H.4 Viewer 시드

- `seed_secom_if_empty()` — `groups`(2), `admins`(1) 등 기본 데이터.

---

## I. Import 경로 규칙

| 범위 | 규칙 | 예시 |
|------|------|------|
| **앱 모듈** | `suvisdev.apps.` 접두사 생략 — `apps/`를 import root로 취급 | `from mova.app.ports.input.movies_use_case import MoviesUseCase` |
| **Core 모듈** | `core.*` (main.py가 `suvisdev/`를 path에 추가) | `from core.matrix.grid_oracle_database_manager import get_db` |
| **경로 불명 시** | `AGENTS.md` 먼저 확인 — 절대 추측하지 않는다 | — |

---

## J. 앱별 참조 파일

### Titanic (기준선) → [`apps/titanic/_docs/CLAUDE.md`](apps/titanic/_docs/CLAUDE.md)

### Mova (Dto + Schema 변환) → [`apps/mova/_docs/CLAUDE.md`](apps/mova/_docs/CLAUDE.md)

| 역할 | 파일 |
|------|------|
| Router + invoke | `mova/adapter/inbound/api/v1/movies_router.py` |
| Input Port | `mova/app/ports/input/movies_use_case.py` |
| Interactor | `mova/app/use_cases/movies_interactor.py` |
| Dto | `mova/app/dtos/movies_dto.py`, `actors_dto.py` |
| DI | `mova/dependencies/movies_provider.py` |
| Router 집약 | `mova/adapter/inbound/api/__init__.py` → `mova_router` |

### Viewer (인증) → [`apps/viewer/_docs/CLAUDE.md`](apps/viewer/_docs/CLAUDE.md)

| API | 경로 |
|-----|------|
| Login | `POST /viewer/login/login` |
| Signup | `POST /viewer/signup/signup` |

| 역할 | 파일 |
|------|------|
| Router | `viewer/adapter/inbound/api/v1/login_router.py` |
| DI | `viewer/dependencies/login.py` (`get_secom_db`) |
| Dto | `viewer/app/dtos/auth_command_dto.py` |
| ORM | `viewer/app/dtos/user_model.py`, `admin_model.py`, `group_model.py` |

---

## K. 금지·안티패턴

| ❌ 금지 | ✅ 대신 |
|--------|--------|
| Router에서 Repository 직접 호출 | Use Case port 경유 |
| Interactor에서 `HTTPException` | `RepositoryError` → router `invoke` |
| Interactor에서 `to_schema()` | Router에서 `Dto.to_schema()` |
| `model_dump()` dict로 Command 생성 | `Command.from_schema(schema)` |
| `adapter/__init__.py` 전역 use case 주입 | `dependencies/*.py` + `Depends` |
| Interactor 내부 `XxxPgRepository()` | 생성자 주입 (DIP) |
| Repository에서 FastAPI import | 순수 예외 클래스 |
| 요청 없는 OCP용 인터페이스 남발 | YAGNI — Karpathy 단순성 우선 |
| PK를 slug/username만으로 | `id` PK + UNIQUE 보조키 |
| `from suvisdev.apps.*` 긴 접두사 | `from mova.*` / `from titanic.*` |
| 삭제된 경로 참조 (`friday13th/jason`, `james_command.py` 등) | `AGENTS.md` 확인 |

---

## L. 새 API 추가 체크리스트

1. [ ] `schemas/*_schema.py` — Request/Response Pydantic
2. [ ] `app/dtos/` — `*Command.from_schema`, `*Dto.from_orm`, `to_schema`
3. [ ] `app/ports/input/*_use_case.py` — ABC (Schema in, Dto out)
4. [ ] `app/ports/output/*_repository.py` — ABC (Command in)
5. [ ] `app/use_cases/*_interactor.py` — Schema→Command→Repo→Dto
6. [ ] `adapter/outbound/pg/*_pg_repository.py` — Command 처리, `RepositoryError`
7. [ ] `adapter/outbound/llm/*_llm_adapter.py` — LLM 어댑터 (필요 시)
8. [ ] `dependencies/*.py` — `get_*_use_case`
9. [ ] `adapter/inbound/api/v1/*_router.py` — `Depends`, `invoke`, `to_schema`
10. [ ] `main.py` 또는 상위 router에 include
11. [ ] `python -c "import main"` — import 오류 없음 확인
12. [ ] `python scripts/verify_db_tables.py` — 새 ORM 테이블 추가 시

---

## M. 한 줄 요약 (에이전트용)

> **Router(Schema) → Input Port(Schema→Dto) → Interactor(Schema→Command→Port) → PgRepository(Command→ORM) → Dto → Router(`to_schema`)**  
> **SRP·ISP·DIP 지킨다. OCP·LSP는 아직 확장하지 않는다. James 패턴과 레이어를 완전히 동일하게 맞춘다.**

---

## N. 관련 문서

| 문서 | 경로 |
|------|------|
| 루트 Karpathy 원칙 | [`../CLAUDE.md`](../CLAUDE.md) |
| Titanic 앱 기준선 | [`apps/titanic/_docs/CLAUDE.md`](apps/titanic/_docs/CLAUDE.md) |
| 에이전트 경로 안내 | `AGENTS.md` |
| Cursor 하네스 | `.cursorrules` |
| 엔티티 PK | `_claude/ENTITY_RULE.md` |
| Mova ERD | `apps/mova/_docs/MOVA_ERD.md` |
| Titanic ERD | `apps/titanic/_docs/TITANIC_ERD.md` |
