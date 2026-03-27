"""Create or update the admin user. Run inside the container:
    python scripts/create_admin.py
"""
import asyncio
import os
import sys

sys.path.insert(0, "/app")

import bcrypt
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.player import Player

DATABASE_URL = os.environ.get(
    "AURORA_DATABASE_URL",
    "postgresql+asyncpg://aurora:aurora@db:5432/aurora",
)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "aurora_admin_2024"
ADMIN_NAME = "Admin"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def main():
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        result = await session.execute(select(Player).where(Player.username == ADMIN_USERNAME))
        admin = result.scalar_one_or_none()

        if admin:
            admin.password_hash = hash_password(ADMIN_PASSWORD)
            admin.is_admin = True
            print(f"Updated existing admin user '{ADMIN_USERNAME}'")
        else:
            admin = Player(
                username=ADMIN_USERNAME,
                password_hash=hash_password(ADMIN_PASSWORD),
                name=ADMIN_NAME,
                is_admin=True,
            )
            session.add(admin)
            print(f"Created admin user '{ADMIN_USERNAME}'")

        await session.commit()
        await session.refresh(admin)
        print(f"  ID       : {admin.id}")
        print(f"  Username : {admin.username}")
        print(f"  Password : {ADMIN_PASSWORD}")
        print(f"  is_admin : {admin.is_admin}")

    await engine.dispose()


asyncio.run(main())
