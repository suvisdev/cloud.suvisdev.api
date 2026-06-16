# MOVA — FlutterFlow 화면 설계서

> **태그**: #mova #flutterflow #ui-design #movie-recommendation #suvisdev  
> **날짜**: 2026-05-06  
> **앱명**: mova  
> **플랫폼**: CLOUD.SUVISDEV / apps/mova  
> **버전**: v0.1 (Prototype)

---

## 📋 화면 목록 (Page Flow)

```
[1] LoginPage
       ↓ (Google 로그인 버튼 클릭 → 무조건 성공 처리)
[2] MovieHomePage
```

---

---

# 🖥️ Page 1 — LoginPage

## 개요

| 항목 | 내용 |
|------|------|
| Page 이름 | `LoginPage` |
| Route | `/login` |
| 목적 | Google 계정으로 로그인, 등록된 이메일만 허용 |
| 프로토타입 동작 | 버튼 클릭 시 무조건 로그인 성공 → MovieHomePage 이동 |

---

## 레이아웃 구조

```
┌─────────────────────────────────┐
│                                 │
│         [상단 여백 spacer]        │
│                                 │
│       🎬  mova                  │  ← AppTitle (로고 + 앱명)
│    당신의 영화 취향을 발견하세요      │  ← SubTitle
│                                 │
│         [중간 여백 spacer]        │
│                                 │
│  ┌─────────────────────────┐    │
│  │  G  Google로 로그인      │    │  ← GoogleLoginButton
│  └─────────────────────────┘    │
│                                 │
│   등록된 계정만 이용 가능합니다.    │  ← InfoText
│                                 │
│         [하단 여백 spacer]        │
│                                 │
└─────────────────────────────────┘
```

---

## 위젯 상세 스펙

### 🔹 배경 (Background)
- **Type**: Scaffold / Container
- **Color**: `#0D0D0D` (다크 배경) 또는 `Color.fromARGB(255, 13, 13, 13)`
- **Gradient (선택)**: 상단 `#1A1A2E` → 하단 `#0D0D0D` (세로 Linear Gradient)

---

### 🔹 AppTitle
- **Widget**: Text
- **Text**: `mova`
- **Font Size**: `48sp`
- **Font Weight**: Bold
- **Color**: `#FFFFFF`
- **Alignment**: Center
- **상단 아이콘**: 🎬 아이콘 or 영화 필름 SVG (선택)

---

### 🔹 SubTitle
- **Widget**: Text
- **Text**: `당신의 영화 취향을 발견하세요`
- **Font Size**: `16sp`
- **Color**: `#AAAAAA`
- **Alignment**: Center
- **Margin**: Top `8px`

---

### 🔹 GoogleLoginButton
- **Widget**: ElevatedButton 또는 OutlinedButton
- **Width**: `화면 너비의 80%` (maxWidth: 320px)
- **Height**: `52px`
- **Border Radius**: `12px`
- **Background Color**: `#FFFFFF`
- **Text Color**: `#3C3C3C`
- **Text**: `Google로 로그인`
- **Font Size**: `16sp`
- **Font Weight**: Medium
- **아이콘**: Google 'G' 로고 (좌측 배치, 크기 24px)
- **Border**: `1px solid #DDDDDD`
- **Shadow**: Elevation 2

#### ⚡ OnTap 액션 (프로토타입)
```
Action 1: Navigate To → MovieHomePage
  (조건 없이 무조건 이동 — 추후 Firebase Auth + 이메일 화이트리스트 검증으로 교체 예정)
```

> **📌 향후 실제 구현 시 교체 로직**
> ```
> 1. Google Sign-In 실행
> 2. 로그인된 이메일을 Firestore/DB의 allowedUsers 컬렉션과 대조
> 3. 등록된 이메일이면 → MovieHomePage 이동
> 4. 미등록 이메일이면 → 에러 다이얼로그 표시 ("접근 권한이 없는 계정입니다.")
> ```

---

### 🔹 InfoText
- **Widget**: Text
- **Text**: `등록된 계정만 이용 가능합니다.`
- **Font Size**: `12sp`
- **Color**: `#666666`
- **Alignment**: Center
- **Margin**: Top `16px`

---

---

# 🖥️ Page 2 — MovieHomePage

## 개요

| 항목 | 내용 |
|------|------|
| Page 이름 | `MovieHomePage` |
| Route | `/home` |
| 목적 | 장르 선택 + 자연어 검색으로 영화 추천 요청 |
| 진입 조건 | LoginPage에서 로그인 성공 후 |

---

## 레이아웃 구조

```
┌─────────────────────────────────┐
│  mova                    👤     │  ← AppBar (앱명 + 유저 아이콘)
├─────────────────────────────────┤
│                                 │
│  어떤 영화를 찾고 계신가요?          │  ← SectionTitle
│                                 │
│  ┌───────────────────────────┐  │
│  │ 🔍  영화 분위기, 장면 묘사...  │  │  ← SearchInputField
│  └───────────────────────────┘  │
│                                 │
│  ─────── 장르 선택 ───────        │  ← GenreSectionLabel
│                                 │
│  [액션] [로맨스] [공포] [코미디]    │  ← GenreChipRow 1
│  [SF]  [애니]  [다큐] [스릴러]    │  ← GenreChipRow 2
│  [드라마] [판타지] [범죄] [기타]   │  ← GenreChipRow 3
│                                 │
│         [하단 여백]               │
│                                 │
│  ┌─────────────────────────┐    │
│  │     🎬  영화 추천받기      │    │  ← RecommendButton (CTA)
│  └─────────────────────────┘    │
│                                 │
└─────────────────────────────────┘
```

---

## 위젯 상세 스펙

### 🔹 AppBar
- **Type**: AppBar
- **배경**: `#0D0D0D` 또는 Transparent
- **Title**: `mova` (White, Bold, 20sp)
- **우측 Action**: CircleAvatar (유저 프로필 아이콘, 크기 32px)
- **Elevation**: 0 (구분선 없음)

---

### 🔹 SectionTitle
- **Widget**: Text
- **Text**: `어떤 영화를 찾고 계신가요?`
- **Font Size**: `22sp`
- **Font Weight**: SemiBold
- **Color**: `#FFFFFF`
- **Margin**: Top `24px`, Left `20px`

---

### 🔹 SearchInputField
- **Widget**: TextField
- **Hint Text**: `영화 분위기, 장면 묘사, 배우 이름 등을 입력하세요`
- **Hint Color**: `#888888`
- **Text Color**: `#FFFFFF`
- **Background**: `#1E1E1E`
- **Border Radius**: `16px`
- **Border**: `1px solid #333333`
- **Prefix Icon**: 🔍 (search icon, Color: `#888888`)
- **Padding**: `14px horizontal, 16px vertical`
- **Margin**: `16px horizontal, 12px top`
- **MaxLines**: 3 (멀티라인 허용)
- **TextInputAction**: `done`

---

### 🔹 GenreSectionLabel
- **Widget**: Text
- **Text**: `장르 선택`
- **Font Size**: `15sp`
- **Color**: `#AAAAAA`
- **Margin**: Top `24px`, Left `20px`, Bottom `10px`

---

### 🔹 GenreChipList
- **Widget**: Wrap (자동 줄바꿈)
- **Spacing**: `8px horizontal, 8px vertical`
- **Padding**: `0 20px`

#### GenreChip 개별 스펙

| 상태 | 배경색 | 텍스트색 | 테두리 |
|------|--------|----------|--------|
| 비선택 | `#1E1E1E` | `#AAAAAA` | `1px solid #444444` |
| 선택됨 | `#E50914` (넷플릭스 레드 계열) | `#FFFFFF` | 없음 |

- **Border Radius**: `20px` (pill shape)
- **Padding**: `8px 16px`
- **Font Size**: `14sp`
- **다중 선택 가능** (선택된 장르 State 리스트로 관리)

#### 장르 목록
```
액션 / 로맨스 / 공포 / 코미디 / SF / 애니메이션 / 다큐멘터리 / 스릴러 / 드라마 / 판타지 / 범죄 / 기타
```

---

### 🔹 RecommendButton (CTA)
- **Widget**: ElevatedButton
- **Text**: `🎬  영화 추천받기`
- **Width**: `화면 너비의 90%`
- **Height**: `56px`
- **Border Radius**: `16px`
- **Background**: `#E50914` (강조 레드)
- **Text Color**: `#FFFFFF`
- **Font Size**: `17sp`
- **Font Weight**: Bold
- **Position**: 화면 하단 고정 (Pinned Bottom) 또는 Column 마지막

#### ⚡ OnTap 액션 (프로토타입)
```
Action: Navigate To → (추후 결과 페이지 or AI 추천 API 호출)
현재: SnackBar 표시 → "추천 기능을 준비 중입니다 🎬"
```

---

## 상태 관리 (State Variables)

| 변수명 | 타입 | 초기값 | 설명 |
|--------|------|--------|------|
| `selectedGenres` | `List<String>` | `[]` | 선택된 장르 목록 |
| `searchQuery` | `String` | `""` | 검색 입력 텍스트 |

---

---

# 🎨 디자인 시스템 요약

| 토큰 | 값 |
|------|----|
| Primary Background | `#0D0D0D` |
| Surface | `#1E1E1E` |
| Accent (CTA) | `#E50914` |
| Text Primary | `#FFFFFF` |
| Text Secondary | `#AAAAAA` |
| Text Muted | `#666666` |
| Border | `#333333` |
| Border Selected | `#E50914` |
| Font | `Pretendard` 또는 `Noto Sans KR` |

---

# 🗺️ 향후 진화 로드맵

```
v0.1 (현재) : UI 프로토타입, 로그인 무조건 성공, 추천 버튼 미구현
     ↓
v0.2         : Firebase Auth 연동, 이메일 화이트리스트 검증
     ↓
v0.3         : Claude API 연동 → 장르 + 검색어 기반 영화 추천 응답
     ↓
v1.0 (Agent) : MovaAgent — 대화형 영화 추천 에이전트 완성
```

---

## 🔗 연결 노트

- [[CLOUD.SUVISDEV 프로젝트 구조]]
- [[cine_app_naming]] → mova로 최종 확정
- [[Suvis AI 에이전트 설계]]

---

*Generated for MOVA FlutterFlow Design Spec — CLOUD.SUVISDEV*
