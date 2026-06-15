# 🎬 Mova App: Agent DTO Architecture Specification

### (스튜디오 vs 흥행 시장 vs 서비스 플랫폼 구조)

본 문서는 `mova` 애플리케이션의 `adapter/inbound/api/schemas` 패키지 내에 위치할 **12개 ERD 테이블 기반 DTO 명세서**입니다. 영화 추천 시스템의 데이터 흐름을 직관적으로 파악할 수 있도록 **[스튜디오 / 제작 계층]**, **[흥행 시장 / 분석 계층]**, **[서비스 플랫폼 / 운영 계층]** 의 3대 구도로 분류했습니다.

*(참고: ERD 원본은 [`MOVA_ERD.md`](./MOVA_ERD.md) 를 기준으로 합니다.)*

---

## 1. Studio 그룹 (`studio`) — 제작 계층

> **Description:** 영화 콘텐츠의 핵심 원천 데이터를 생산·보관·분류합니다. 카탈로그 저장, 인물 관리, 영화-배우 연결, 감성/장르/캐스트 키워드 라벨링을 담당하는 카테고리입니다.

### **studio_director_catalog_dto.py**

* **테이블:** `movies`
* **캐릭터:** 감독 (Director)
* **역할 (`keyword`):** `catalog`
* **드라마 설정 및 시스템 기능:** 한 편의 영화를 완성하고 지휘하는 연출자. `movies` 테이블의 핵심 엔티티로, `slug` · `title` · `release_year` · `rating` · `poster_url` · `platform` · `genres(JSONB)` 를 보관합니다. 모든 추천·랭킹·리뷰는 이 테이블의 `id`를 FK 기준점으로 삼습니다.

### **studio_actor_performer_dto.py**

* **테이블:** `actors`
* **캐릭터:** 배우 (Actor)
* **역할 (`keyword`):** `performer`
* **드라마 설정 및 시스템 기능:** 스크린을 채우는 실제 인물 데이터. `actors` 테이블에서 `name` · `role_type(actor | director)` · `profile_photo_url` 를 관리합니다. `(name, role_type)` UNIQUE 제약으로 동명이인 충돌을 방지하며, 채팅 `search_filters.similar_to.actors` 검색 시 조회 대상이 됩니다.

### **studio_casting_connector_dto.py**

* **테이블:** `characters`
* **캐릭터:** 캐스팅 감독 (Casting Director)
* **역할 (`keyword`):** `connector`
* **드라마 설정 및 시스템 기능:** 영화와 배우를 연결하는 중간자. `characters` 테이블은 `movies` ↔ `actors` N:M 관계를 중계하는 조인 테이블입니다. `(movie_id, actor_id)` UNIQUE 복합키로 중복 출연을 방지하고, `tags.character_id` FK 를 통해 `cast` 태그와 연결되어 배우 검색을 지원합니다.

### **studio_publicist_tagger_dto.py**

* **테이블:** `tags`
* **캐릭터:** 홍보 담당자 (Publicist)
* **역할 (`keyword`):** `tagger`
* **드라마 설정 및 시스템 기능:** 영화의 분위기·장르·인물을 대중 언어로 표현하는 홍보 전문가. `tags` 테이블에서 `tag_kind(mood | genre | cast)` · `slug` · `label` · `description` 을 관리합니다. `chat.refined_query` 가 `tags.label` ILIKE 검색을 통해 영화를 찾는 핵심 경로이며, `cast` 태그는 `character_id` FK 로 배우-영화 연결을 검색에 노출합니다.

---

## 2. Market 그룹 (`market`) — 흥행 분석 계층

> **Description:** 사용자의 행동 데이터와 AI 추천 결과를 집계하고 분석합니다. 흥행 순위 생성, 채팅 의도 해석, 추천 큐레이션, 반응·리뷰 기록을 담당하는 카테고리입니다.

### **market_producer_ranker_dto.py**

* **테이블:** `rankings`
* **캐릭터:** 프로듀서 (Producer)
* **역할 (`keyword`):** `ranker`
* **드라마 설정 및 시스템 기능:** 흥행 성적을 숫자로 증명하는 제작 총괄. `rankings` 테이블에서 `source(chat_trend | box_office | manual)` · `rank` · `score` · `badge` · `ranked_at` 을 관리합니다. `chat_trend` 는 `picks`·`chat.hit_count` 집계 결과이고, `box_office` 는 KOFIC 스냅샷입니다. `(rank, ranked_at, source)` UNIQUE 로 같은 날 두 출처의 랭킹이 공존합니다.

### **market_screenwriter_intent_dto.py**

* **테이블:** `chat`
* **캐릭터:** 시나리오 작가 (Screenwriter)
* **역할 (`keyword`):** `intent`
* **드라마 설정 및 시스템 기능:** 사용자의 말 속 숨은 의도를 정제된 문장으로 번역하는 작가. `chat` 테이블에서 `raw_message` → `refined_query` · `keywords(JSONB)` · `intent_type(filter_and | similar_person | mood)` · `search_filters(JSONB)` 를 저장합니다. `hit_count` 로 동일 의도 재사용을 집계하고, `assistant_id` FK 로 응답 AI 페르소나를 연결합니다.

### **market_distributor_curator_dto.py**

* **테이블:** `picks`
* **캐릭터:** 배급 담당자 (Distributor)
* **역할 (`keyword`):** `curator`
* **드라마 설정 및 시스템 기능:** AI가 선정한 작품을 사용자에게 배급하는 큐레이터. `picks` 테이블에서 한 번의 채팅 응답에서 나온 추천 3편을 `batch_at` 으로 묶어 기록합니다. `pick_rank` · `hook(한 줄 추천 이유)` · `title_snapshot` 을 보관하며, `picks` 행은 `rankings` 집계(`source=chat_trend`)의 입력 신호가 됩니다.

### **market_critic_reviewer_dto.py**

* **테이블:** `reviews`
* **캐릭터:** 평론가 (Critic)
* **역할 (`keyword`):** `reviewer`
* **드라마 설정 및 시스템 기능:** 작품에 대한 반응을 언어와 별점으로 기록하는 비평가. `reviews` 테이블에서 `action_type(favorite | watched | click | not_interested | review)` 를 단일 테이블로 통합 관리합니다. `action_type=review` 일 때 `rating(1~5)` · `body` 가 함께 저장되며, `(user_id, movie_id)` partial UNIQUE 로 중복 리뷰를 방지합니다.

---

## 3. Platform 그룹 (`platform`) — 서비스 운영 계층

> **Description:** 서비스를 운영하는 플랫폼 계층입니다. AI 페르소나 설정, 권한 그룹 관리, 시스템 관리자 운영, 일반 사용자 프로필을 담당하는 카테고리입니다.
>
> **소유권 참고:** `assistants` 는 Mova DB 테이블. `groups` · `admins` · `users` 는 `viewer` 앱(Secom DB)이 소유하며 Mova 는 `user_id` FK 로 참조만 합니다. viewer 가 독립 서비스로 분리될 경우 해당 3개 캐릭터를 `viewer/_docs/` 로 이동하세요.

### **platform_concierge_persona_dto.py**

* **테이블:** `assistants`
* **캐릭터:** AI 컨시어지 (AI Concierge)
* **역할 (`keyword`):** `persona`
* **드라마 설정 및 시스템 기능:** 극장 입구에서 관객을 맞이하는 AI 상담사. `assistants` 테이블에서 `slug(mova-concierge)` · `display_name` · `avatar_url` · `system_prompt` · `default_model` · `is_active` 를 관리합니다. `chat.assistant_id` FK 로 어떤 페르소나가 응답했는지 추적하며, 시드 스크립트(`seed_assistants_if_empty`)로 초기 데이터를 주입합니다.

### **platform_guild_authority_dto.py**

* **테이블:** `groups`
* **캐릭터:** 길드 (Guild)
* **역할 (`keyword`):** `authority`
* **드라마 설정 및 시스템 기능:** 극장 조직의 직책 체계를 정의하는 규약집. `groups` 테이블에서 `code(admin | user)` UNIQUE 로 권한 역할을 구분합니다. `admins.group_id` 와 `users.group_id` 양쪽의 FK 참조 기준이 되며, `seed_groups_if_empty()` 로 `admin`·`user` 두 코드가 시드됩니다.

### **platform_executive_gatekeeper_dto.py**

* **테이블:** `admins`
* **캐릭터:** 총지배인 (Executive)
* **역할 (`keyword`):** `gatekeeper`
* **드라마 설정 및 시스템 기능:** 극장 전체를 관리하는 최고 책임자. `admins` 테이블에서 `username(UNIQUE)` · `password_hash` · `nickname` · `email` 을 관리합니다. `group_id → groups(code=admin)` FK 로 권한이 부여되며, `seed_admin_if_empty()` 로 최초 1명이 시드됩니다. Mova 도메인(`chat`·`reviews`·`picks`) FK 는 `users.id` 만 참조하므로 관리자 행동은 별도로 처리합니다.

### **platform_audience_profile_dto.py**

* **테이블:** `users`
* **캐릭터:** 관객 (Audience)
* **역할 (`keyword`):** `profile`
* **드라마 설정 및 시스템 기능:** 서비스를 이용하는 일반 사용자이자 모든 Mova 데이터의 실질적 주체. `users` 테이블에서 `username` · `password_hash` · `nickname` · `email` 외에 `gender` · `age_group` · `birth_year` · `preferred_genres(JSONB)` · `bio` 등 Mova 개인화 프로필을 함께 관리합니다. `chat.user_id` · `picks.user_id` · `reviews.user_id` 의 공통 FK 원점이며, 비로그인 상태에서는 `NULL` 로 전역 집계에 기여합니다.

---

## ERD 테이블 ↔ DTO 매핑 요약

| 그룹 | 파일명 | 테이블 | 캐릭터 | keyword |
|------|--------|--------|--------|---------|
| `studio` | `studio_director_catalog_dto.py` | `movies` | 감독 | `catalog` |
| `studio` | `studio_actor_performer_dto.py` | `actors` | 배우 | `performer` |
| `studio` | `studio_casting_connector_dto.py` | `characters` | 캐스팅 감독 | `connector` |
| `studio` | `studio_publicist_tagger_dto.py` | `tags` | 홍보 담당자 | `tagger` |
| `market` | `market_producer_ranker_dto.py` | `rankings` | 프로듀서 | `ranker` |
| `market` | `market_screenwriter_intent_dto.py` | `chat` | 시나리오 작가 | `intent` |
| `market` | `market_distributor_curator_dto.py` | `picks` | 배급 담당자 | `curator` |
| `market` | `market_critic_reviewer_dto.py` | `reviews` | 평론가 | `reviewer` |
| `platform` | `platform_concierge_persona_dto.py` | `assistants` | AI 컨시어지 | `persona` |
| `platform` | `platform_guild_authority_dto.py` | `groups` | 길드 | `authority` |
| `platform` | `platform_executive_gatekeeper_dto.py` | `admins` | 총지배인 | `gatekeeper` |
| `platform` | `platform_audience_profile_dto.py` | `users` | 관객 | `profile` |
