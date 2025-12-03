from logging.config import fileConfig
import asyncio
import os
import sys

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import app modules
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base
from app.models.database import User, Project, Document, Summary  # noqa
from app.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with environment-aware value from settings
config.set_main_option("sqlalchemy.url", settings.get_database_url())

# Safety check: Confirm production migrations
if settings.is_production_db:
    # In non-interactive environments (CI/CD), require explicit confirmation
    if not os.getenv("ALEMBIC_PRODUCTION_CONFIRMED"):
        if sys.stdin.isatty():  # Interactive terminal
            db_host = settings.get_database_url().split('@')[1].split('/')[0] if '@' in settings.get_database_url() else 'unknown'
            response = input(
                f"\n⚠️  WARNING: Running migrations against PRODUCTION database!\n"
                f"   Database: {db_host}\n"
                "   Continue? (yes/no): "
            )
            if response.lower() != "yes":
                print("Migration aborted.")
                sys.exit(1)
        else:
            raise RuntimeError(
                "Attempting to run production migrations without confirmation. "
                "Set ALEMBIC_PRODUCTION_CONFIRMED=true to proceed."
            )

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # Only disable prepared statements for production (pgbouncer compatibility)
    connect_args = {"statement_cache_size": 0} if settings.is_production_db else {}

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
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
