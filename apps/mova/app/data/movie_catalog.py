"""프론트 정적 카탈로그와 맞춘 canonical slug (한글 제목·DB slug 불일치 방지)."""

TITLE_TO_CANONICAL_SLUG: dict[str, str] = {
    "원더풀스": "wonderfuls",
    "암살": "assassination",
    "인터스텔라": "interstellar",
    "듄: 파트2": "dune-2",
    "오펜하이머": "oppenheimer",
    "기생충": "parasite",
    "블레이드 러너 2049": "blade-runner-2049",
    "라라랜드": "lalaland",
    "매트릭스": "matrix",
    "인셉션": "inception",
    "다크 나이트": "dark-knight",
    "오징어 게임": "squid-game",
}


def resolve_canonical_slug(key: str, *, title: str | None = None) -> str:
    k = key.strip()
    if not k and title:
        k = title.strip()
    if k in TITLE_TO_CANONICAL_SLUG:
        return TITLE_TO_CANONICAL_SLUG[k]
    if title:
        t = title.strip()
        if t in TITLE_TO_CANONICAL_SLUG:
            return TITLE_TO_CANONICAL_SLUG[t]
    return k or "movie"


def title_for_canonical_slug(canonical: str) -> str | None:
    for title, slug in TITLE_TO_CANONICAL_SLUG.items():
        if slug == canonical.strip():
            return title
    return None
