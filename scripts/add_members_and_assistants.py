"""members, groups, member_groups, assistants 테이블 및 chat FK 추가.

Usage (backend 폴더에서):
  python scripts/add_members_and_assistants.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / "apps"
sys.path.insert(0, str(APPS))


async def column_exists(conn, table: str, column: str) -> bool:
    from sqlalchemy import text

    r = await conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = :t AND column_name = :c"
        ),
        {"t": table, "c": column},
    )
    return r.scalar() is not None


async def table_exists(conn, table: str) -> bool:
    from sqlalchemy import text

    r = await conn.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = :t"
        ),
        {"t": table},
    )
    return r.scalar() is not None


async def main() -> None:
    from database import create_tables, dispose_engine, get_engine, reload_env
    from secom.app.repositories.member_repository import MemberRepository
    from secom.app.seed_groups import seed_groups_if_empty
    from mova.adapter.outbound.pg.assistants_pg_repository import seed_assistants_if_empty

    from sqlalchemy import select
    from secom.app.models.user_model import User

    reload_env()
    await create_tables()

    engine = get_engine()
    async with engine.begin() as conn:
        if not await column_exists(conn, "chat", "member_id"):
            from sqlalchemy import text

            print("ALTER chat ADD member_id, assistant_id")
            await conn.execute(text("ALTER TABLE chat ADD COLUMN member_id INTEGER NULL"))
            await conn.execute(text("ALTER TABLE chat ADD COLUMN assistant_id INTEGER NULL"))
            await conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_chat_member_id ON chat (member_id)"
                ),
            )
            await conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_chat_assistant_id ON chat (assistant_id)"
                ),
            )

        if await table_exists(conn, "members") and await table_exists(conn, "assistants"):
            if not await column_exists(conn, "chat", "member_id"):
                pass
            else:
                from sqlalchemy import text

                fk_member = await conn.execute(
                    text(
                        "SELECT 1 FROM information_schema.table_constraints "
                        "WHERE constraint_name = 'fk_chat_member_id_members'"
                    ),
                )
                if fk_member.scalar() is None:
                    await conn.execute(
                        text(
                            "ALTER TABLE chat ADD CONSTRAINT fk_chat_member_id_members "
                            "FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE SET NULL"
                        ),
                    )
                fk_ast = await conn.execute(
                    text(
                        "SELECT 1 FROM information_schema.table_constraints "
                        "WHERE constraint_name = 'fk_chat_assistant_id_assistants'"
                    ),
                )
                if fk_ast.scalar() is None:
                    await conn.execute(
                        text(
                            "ALTER TABLE chat ADD CONSTRAINT fk_chat_assistant_id_assistants "
                            "FOREIGN KEY (assistant_id) REFERENCES assistants (id) ON DELETE SET NULL"
                        ),
                    )

    await seed_groups_if_empty()
    await seed_assistants_if_empty()

    from database import get_secom_session_factory

    factory = get_secom_session_factory()
    member_repo = MemberRepository()
    async with factory() as session:
        result = await session.execute(select(User.id, User.role))
        rows = list(result.all())
    for user_id, role in rows:
        if await member_repo.get_by_user_id(user_id) is None:
            await member_repo.create_for_user(user_id, user_role=role or "user")
            print(f"member backfill user_id={user_id}")

    await dispose_engine()
    print("done.")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
