import logging

from mova.app.models.title_model import MovaKeyword, MovaPerson, MovaTitle
from mova.app.repositories.title_repository import TitleRepository
from mova.app.seed_data import SEED_TITLES

logger = logging.getLogger(__name__)


async def seed_mova_titles_if_empty() -> None:
    """Neon DB에 Mova 작품 데이터가 없으면 시드한다."""
    from mova.app.repositories.search_stats_repository import SearchStatsRepository

    try:
        await SearchStatsRepository().ensure_analytics_columns()
    except RuntimeError as e:
        logger.warning("Mova analytics 컬럼 확인 건너뜀 — DB 미연결: %s", e)
        return

    repo = TitleRepository()
    try:
        count = await repo.count_titles()
    except RuntimeError as e:
        logger.warning("Mova 시드 건너뜀 — DB 미연결: %s", e)
        return

    if count > 0:
        logger.info("Mova 시드 건너뜀 — 기존 작품 %s건", count)
        return

    from database import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        for item in SEED_TITLES:
            title = MovaTitle(
                slug=item["slug"],
                title=item["title"],
                year=item["year"],
                genres=item["genres"],
                country=item["country"],
                age_rating=item["age_rating"],
                rank_badge=item.get("rank_badge"),
                platform=item.get("platform"),
                poster_url=item["poster_url"],
                backdrop_url=item["backdrop_url"],
                rating=item["rating"],
                rating_count=item["rating_count"],
                rank=item.get("rank", 0),
                badge=item.get("badge"),
                synopsis=item["synopsis"],
                rating_distribution=item.get("rating_distribution", []),
                gallery=item.get("gallery", []),
                comments=item.get("comments", []),
            )
            session.add(title)
            await session.flush()

            for person in item.get("cast", []):
                session.add(
                    MovaPerson(
                        title_id=title.id,
                        name=person["name"],
                        role=person.get("role", ""),
                        photo_url=person.get("photo_url", ""),
                    ),
                )

            keywords = set(item.get("keywords", []))
            keywords.update(item["genres"])
            keywords.add(item["title"])
            for kw in keywords:
                session.add(MovaKeyword(title_id=title.id, name=kw))

        await session.commit()
    logger.info("Mova 시드 완료 — 작품 %s건", len(SEED_TITLES))
