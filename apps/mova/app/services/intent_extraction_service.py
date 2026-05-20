import json
import logging
import re

from matrix.app.keymaker import get_keymaker

logger = logging.getLogger(__name__)

EXTRACT_PROMPT = """사용자의 영화 추천 요청에서 DB 검색·취향 기록용 핵심 문구를 추출하세요.

규칙:
- 감정·상황·장르·분위기만 남긴 짧은 한국어 구문 1개 (15자 내외 권장, 최대 40자)
- "보여줘", "추천해줘", "오늘" 같은 말버릇은 제거
- 예: "오늘 우울하니까 신나는 영화 보여줘" → refined_query: "우울할 때 보는 신나는 영화"
- 예: "로맨스 말고 스릴러" → refined_query: "스릴러 장르"

반드시 JSON 한 줄만 출력:
{{"refined_query": "...", "keywords": ["키워드1", "키워드2"]}}

사용자 메시지:
{message}
"""

_FILLER = re.compile(
    r"^(오늘|지금|좀|그냥|please|plz)\s*|[\s,]*(보여줘|보여 줘|추천해줘|추천 해줘|알려줘|찾아줘|해줘|해 줘|있어|있나|할래|싶어)\s*$",
    re.IGNORECASE,
)


class IntentExtractionService:
    def extract(self, message: str) -> dict[str, list[str] | str]:
        text = message.strip()
        if not text:
            return {"refined_query": "", "keywords": []}

        keymaker = get_keymaker()
        if keymaker.is_gemini_ready():
            try:
                gemini = keymaker.get_gemini_model("flash")
                if gemini is not None:
                    response = gemini.generate_content(EXTRACT_PROMPT.format(message=text))
                    parsed = self._parse_json(response.text or "")
                    if parsed.get("refined_query"):
                        return parsed
            except Exception:
                logger.exception("[IntentExtractionService] Gemini 추출 실패, fallback 사용")

        return self._fallback(text)

    def _parse_json(self, raw: str) -> dict[str, list[str] | str]:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{[^{}]+\}", raw, re.DOTALL)
            if not match:
                return {"refined_query": "", "keywords": []}
            data = json.loads(match.group(0))

        refined = str(data.get("refined_query", "")).strip()[:255]
        keywords = data.get("keywords") or []
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",") if k.strip()]
        elif isinstance(keywords, list):
            keywords = [str(k).strip() for k in keywords if str(k).strip()]
        else:
            keywords = []

        return {"refined_query": refined, "keywords": keywords[:12]}

    def _fallback(self, message: str) -> dict[str, list[str] | str]:
        cleaned = _FILLER.sub("", message).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        refined = cleaned[:40] if cleaned else message[:40]
        tokens = [t for t in re.split(r"[\s,]+", cleaned) if len(t) >= 2][:8]
        return {"refined_query": refined, "keywords": tokens}
