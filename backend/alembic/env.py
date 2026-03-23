"""Alembic environment configuration."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, JSON
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.dialects import sqlite

from app.core.config import settings
from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def setup_jsonb_for_sqlite():
    """Setup JSONB compatibility for SQLite."""
    import app.models.scenario
    import app.models.practice
    import app.models.dialogue
    import app.models.payment
    import app.models.custom_scenario
    
    modules = [
        app.models.scenario,
        app.models.practice,
        app.models.dialogue,
        app.models.payment,
        app.models.custom_scenario,
    ]
    
    for module in modules:
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and hasattr(obj, '__table__'):
                for column in obj.__table__.columns:
                    if hasattr(column.type, '__class__') and column.type.__class__.__name__ == 'JSONB':
                        column.type = JSON()

def get_url() -> str:
    """Get database URL from settings."""
    return settings.database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    if "sqlite" in url:
        setup_jsonb_for_sqlite()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with connection."""
    if "sqlite" in str(connection.engine.url):
        setup_jsonb_for_sqlite()
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
