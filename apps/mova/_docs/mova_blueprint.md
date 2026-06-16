# 프로젝트: mova (영화 추천 플랫폼) 🎬
**컨셉:** 스티브 잡스의 미니멀리즘 + 철학적 사유 + Python/FlutterFlow 풀스택 개발

---

## 1. 프로젝트 개요
- **핵심 목표:** 단순 장르 추천을 넘어 사용자의 '가치관'과 '철학적 상태'를 분석하여 영화를 연결함.
- **디자인 철학:** "Less is More" (스티브 잡스 스타일). 블랙 테마, 글래스모피즘, 스와이프 카드 UI.
- **브랜드 네이밍:** 
  - **Main:** mova (Logos)
  - **Sub:** Being (고전/불변), Becoming (트렌드/변화), Flow (사용자 경험)

---

## 2. 개발 스택 및 구조
### Backend (Python/Pandas)
- `producer.py`: 비즈니스 로직 및 전체 제작 관리.
- `director.py`: 영화의 시각적/예술적 데이터 분석.
- `screenwriter.py`: 시나리오 키워드 및 대사 기반 추천.
- `casting_director.py`: 인물(배우/스태프) 관계망 분석.

### Frontend (FlutterFlow)
- **UI:** `SwipeableStack`을 활용한 몰입형 카드 레이아웃.
- **Data:** Firebase 연동 및 Custom Data Type(`Movie`) 정의.
- **Interaction:** Haptic Feedback 및 Dynamic Color 적용.

---

## 3. AI 생성용 프롬프트 (Core Prompt)
FlutterFlow Instant Generation 또는 에이전트 개발 시 사용:
> "A minimalist movie recommendation app with a large swiping card for movie posters, dark mode theme, and simple navigation. The UI should feel premium like Apple's design, using glassmorphism and subtle animations."

---

## 4. 개인 개발 에이전트용 지식 데이터
- **추천 로직:** 사용자가 '불변' 키워드 선택 시 `philosophy_tag == 'Being'` 필터링 수행.
- **차별화 포인트:** 기존 플랫폼(왓챠, 넷플릭스)이 놓친 '인문학적 큐레이션' 제공.