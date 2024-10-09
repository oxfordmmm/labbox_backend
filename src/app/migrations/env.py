import ast
import asyncio
from logging.config import fileConfig

import astor  # type: ignore
from alembic import context
from alembic.script import ScriptDirectory
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

import app.models as models  # noqa: F401
from app.config import config as app_config
from app.db import Model

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Model.metadata

config.set_main_option("sqlalchemy.url", app_config.DATABASE_URL)

ignored_views = [
    "alembic_version",
    "flattened_sample_details_view",
    "flattened_specimen_details_view",
    "flattened_others_view",
]

sqlalchemy_url = config.get_main_option("sqlalchemy.url")
if sqlalchemy_url is None:
    raise ValueError("Database URL must not be None.")

engine: AsyncEngine = create_async_engine(sqlalchemy_url, pool_size=10, max_overflow=20)


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in ignored_views:
        return False
    return True


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


def do_run_migrations(connection: Connection) -> None:
    """Run sql migrations.

    Args:
        connection (Connection): The connection string
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

    head_revision = ScriptDirectory.from_config(config).as_revision_number("head")
    with open("src/app/__init__.py", "r") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__dbrevision__"
        ):
            node.value = ast.Constant(value=head_revision)

    with open("src/app/__init__.py", "w") as f:
        f.write(astor.to_source(tree))


async def run_async_migrations() -> None:
    """Create an Engine.

    Associate a connection with the context.
    """
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
