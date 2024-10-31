import asyncio, sys, os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

import app.models as models  # noqa: F401
from app.config import app_config
from app.db import Model

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", app_config.DATABASE_URL)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Model.metadata


ignored_views = [
    "alembic_version",
    "flattened_sample_details_view",
    "flattened_specimen_details_view",
    "flattened_others_view",
]


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in ignored_views:
        return False
    return True


def run_migrations_online():    
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        render_as_batch=True,
        include_object=include_object,
    )
    connectable = context.config.attributes.get("connection", None)
    if connectable is None:
        config_section = context.config.get_section(context.config.config_ini_section)
        if config_section is None:
            raise ValueError("Configuration section not found")
        connectable = AsyncEngine(
            engine_from_config(
                config_section,
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
                future=True,
            )
        )

    if isinstance(connectable, AsyncEngine):
        asyncio.run(run_async_migrations(connectable))
    else:
        do_run_migrations(connectable)


async def run_async_migrations(connectable):
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


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
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
