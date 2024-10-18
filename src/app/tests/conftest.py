from collections.abc import AsyncGenerator
from datetime import date

import pytest_asyncio  # type: ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app import models
from app.db import migrate_db_tests


@pytest_asyncio.fixture(scope="function")
async def db_session(postgresql) -> AsyncGenerator[AsyncSession, None]:
    """Fixture to create a database session for testing."""
    # Create a SQLAlchemy engine using the URL provided by pytest-postgresql
    connection = f"postgresql+asyncpg://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"

    # Run the migrations
    await migrate_db_tests(connection)

    engine = create_async_engine(connection, poolclass=NullPool)

    session = AsyncSession(engine)

    async with session.begin():
        ## Add owners
        session.add(models.Owner(site="SiteC", user="User3"))
        session.add(models.Owner(site="blah", user="blah-user"))

        ## add runs
        session.add(
            models.Run(
                code="Run1",
                site="SiteA",
                sequencing_method="Illumina",
                machine="Machine1",
            )
        )
        session.add(
            models.Run(
                code="test1",
                run_date=date.fromisoformat("2024-01-01"),
                site="Oxford",
                sequencing_method="Illumina",
                machine="test_m1",
                user="blah",
                number_samples=2,
                flowcell="fc2",
                passed_qc=True,
                comment="test_comment",
            )
        )

        ## add specimens
        owner = (
            await session.execute(select(models.Owner).limit(1))
        ).scalar_one_or_none()
        session.add(
            models.Specimen(
                accession="123test",
                collection_date=date.fromisoformat("2021-01-01"),
                organism="TestOrganism",
                country_sample_taken_code="GBR",
                owner=owner,
            )
        )

    try:
        yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()
        await engine.dispose()
