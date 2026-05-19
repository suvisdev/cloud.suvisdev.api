import logging

from sqlalchemy import select

from database import get_session_factory
from mova.app.models.title_model import MovaTitle

logger = logging.getLogger(__name__)

MOVA_SYSTEM_PROMPT = """당신은 영화·시리즈 추천 AI 'Mova'입니다.
- 사용자 취향(장르, 분위기, 배우, OTT 등)을 듣고 맞춤 작품을 추천합니다.
- 아래 카탈로그에 있는 작품을 우선 추천하고, 없으면 일반적으로 알려진 작품을 제안할 수 있습니다.
- 답변은 자연스러운 한국어로, 2~4문단 이내로 간결하게 작성합니다.
- 추천 시 작품 제목을 굵게 표시할 필요는 없고, 이유를 한 줄씩 덧붙여 주세요.

[현재 Mova 카탈로그]
{catalog}
"""


class MovaChatService:
    async def build_catalog_snippet(self, limit: int = 12) -> str:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaTitle)
                .order_by(MovaTitle.search_count.desc(), MovaTitle.rank.asc())
                .limit(limit),
            )
            titles = result.scalars().all()
        if not titles:
            return "(카탈로그 로딩 중)"
        lines = []
        for t in titles:
            genres = ", ".join(t.genres or [])
            lines.append(f"- {t.title} ({t.year}) | {genres} | ★{t.rating}")
        return "\n".join(lines)

    def build_prompt(
        self,
        catalog: str,
        history: list[dict[str, str]],
        message: str,
    ) -> str:
        parts = [MOVA_SYSTEM_PROMPT.format(catalog=catalog), "", "[대화]"]
        for item in history[-8:]:
            role = item.get("role", "user")
            label = "사용자" if role == "user" else "Mova"
            parts.append(f"{label}: {item.get('content', '')}")
        parts.append(f"사용자: {message}")
        parts.append("Mova:")
        return "\n".join(parts)
