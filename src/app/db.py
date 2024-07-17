import logging
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config as alembic_config
from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app import __dbrevision__
from app.config import config

logger = logging.getLogger()


async def db_revision_ok(session: AsyncSession) -> bool:
    result = await session.execute(text("SELECT MAX(version_num) FROM alembic_version"))
    db_revision = result.scalars().first()
    if db_revision != __dbrevision__:
        logger.error(
            f"Database revision {db_revision} does not match the expected revision {__dbrevision__}"
        )
        return False
    return True


class Model(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


@asynccontextmanager
async def get_session():
    engine = create_async_engine(config.DATABASE_URL)
    session = AsyncSession(engine)
    try:
        yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.commit()
        await session.close()
        await engine.dispose()


# this is run synchronously at startup
def run_alembic_upgrade_to_head():
    alembic_cfg = alembic_config("alembic.ini")
    try:
        command.upgrade(alembic_cfg, "head")
        logging.info("Alembic upgrade completed successfully.")
    except Exception as e:
        logging.error(f"Alembic upgrade failed: {e}")
        raise
