# 앱 이름 추천 — CLOUD.SUVISDEV 영화 추천 앱

> **태그**: #suvisdev #naming #project-planning #agent #movie  
> **날짜**: 2026-05-06  
> **플랫폼**: CLOUD.SUVISDEV  
> **카테고리**: 프로젝트 구조 / 앱 네이밍

---

## 📌 프롬프트

> 영화 추천해주는 결과물을 만들고 향후 에이전트로 진화하려고 해.  
> 내 플랫폼 구조는 다음과 같고, 새로 app을 추가하는데 적당한 이름을 추천해줘.
>
> ```
> CLOUD.SUVISDEV
> └── apps/
>     ├── doro/
>     └── titanic/
> ```

---

## 🧠 컨텍스트 분석

- 기존 앱들(`doro`, `titanic`)의 네이밍 패턴: **짧고, 주제/소재를 직접 연상, 소문자**
- 신규 앱 목적: **영화 추천 → 향후 에이전트로 진화**
- 요구 조건: 기존 네이밍 톤과 일관성 유지 + 에이전트 확장성 고려

---

## ✅ 추천 결과

### 🎯 Top 추천

| 이름 | 근거 | 에이전트 확장성 |
|------|------|----------------|
| **`cine`** | cinema의 축약, 직관적·세련됨 | `CineAgent`, `CineBot` |
| **`reel`** | 필름 릴 → 영화 그 자체 | `ReelAgent` |
| **`lens`** | 영화를 "보는 시각" 은유, 추천 큐레이션 느낌 | `LensAgent` |

### 💡 보조 후보

| 이름 | 특징 |
|------|------|
| `flick` | 영어 구어체로 "영화" (a flick), 경쾌함 |
| `mova` | movie + agent 합성어 느낌 |
| `scout` | 영화를 탐색·발굴하는 에이전트 개념에 딱 |

---

## 🏆 최종 권장

> **`cine`** 채택 권장
>
> - `doro`, `titanic`과 길이·톤이 가장 잘 어울림
> - 클래스명 `CineAgent`, 모듈명 `cine.recommender` 식으로 자연스럽게 확장 가능

```
apps/
├── doro/
├── titanic/
└── cine/        ← ✅ 신규 추가
```

---

## 🔗 연결 노트

- [[CLOUD.SUVISDEV 프로젝트 구조]]
- [[Suvis AI 에이전트 설계]]
- [[doro 프로젝트]]

---

*Generated for Obsidian personal dev agent knowledge base*
