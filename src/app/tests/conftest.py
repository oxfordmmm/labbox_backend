from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio  # type: ignore
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.db import migrate_db_tests
from app.logs import CustomLogger


@pytest_asyncio.fixture(scope="function")
async def db_session(postgresql) -> AsyncGenerator[AsyncSession, None]:
    """Fixture to create a database session for testing."""
    
    # Create a SQLAlchemy engine using the URL provided by pytest-postgresql
    connection = f"postgresql+asyncpg://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"

    # Run the migrations
    await migrate_db_tests(connection)

    engine = create_async_engine(connection, poolclass=NullPool)

    session = AsyncSession(engine)

    try:
        yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()
        await engine.dispose()


@pytest.fixture(scope="function")
def logger_mock(mocker):
    """Fixture to create a mock logger."""
    return mocker.MagicMock(spec=CustomLogger)
