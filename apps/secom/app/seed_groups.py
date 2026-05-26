"""groups 마스터 시드."""

import logging

from sqlalchemy import select

from database import get_secom_session_factory
from secom.app.models.group_model import Group

logger = logging.getLogger(__name__)

GROUP_DEFS = (
    ("platform_admin", "플랫폼 관리자", "Secom·import API 등 전체 관리"),
    ("mova_admin", "Mova 관리자", "Mova 카탈로그·랭킹·태그 관리"),
    ("mova_member", "Mova 회원", "Mova 앱 일반 이용"),
)


async def seed_groups_if_empty() -> None:
    factory = get_secom_session_factory()
    async with factory() as session:
        result = await session.execute(select(Group.id).limit(1))
        if result.scalar_one_or_none() is not None:
            return
        for code, name, description in GROUP_DEFS:
            session.add(Group(code=code, name=name, description=description))
        await session.commit()
        logger.info("[secom.seed_groups] groups %s건 생성", len(GROUP_DEFS))
