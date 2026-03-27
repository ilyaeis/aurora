import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import all models so autogenerate detects them
from app.models.database import Base
from app.models.player import Player  # noqa: F401
from app.models.world import WorldChunk, NPC, WorldEvent  # noqa: F401
from app.models.items import Item, Enemy  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Override DB URL with env var if present (swap asyncpg -> psycopg2 for sync migrations)
def get_url():
    url = os.environ.get(
        "AURORA_DATABASE_URL",
        "postgresql+asyncpg://aurora:aurora@db:5432/aurora",
    )
    # Alembic needs a sync driver
    return url.replace("postgresql+asyncpg://", "postgresql://")


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
