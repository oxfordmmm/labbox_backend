from collections.abc import AsyncGenerator
from datetime import date

import pytest_asyncio  # type: ignore
from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app import models


@pytest_asyncio.fixture(scope="function")
async def db_session(postgresql) -> AsyncGenerator[AsyncSession, None]:
    """Fixture to create a database session for testing."""
    # Create a SQLAlchemy engine using the URL provided by pytest-postgresql
    connection = f"postgresql+asyncpg://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"
    engine = create_async_engine(connection, poolclass=NullPool)

    # Configure Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", connection)

    # Define a wrapper function to run Alembic migrations
    def run_migrations(connection):
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")

    # Run Alembic migrations
    async with engine.begin() as conn:
        await conn.run_sync(run_migrations)

    session = AsyncSession(engine)

    async with session.begin():
        ## Add owners
        session.add(models.Owner(site="SiteC", user="User3"))
        session.add(models.Owner(site="blah", user="blah-user"))

        ## add countries
        session.add(
            models.Country(
                code="GBR", name="United Kingdom", code2="UK", lat=54.0, lon=-2.0
            )
        )

        ## add specimen_detail_types, omitting description as not really needed for testing
        specimen_detail_types = [
            {"code": "host", "description": "", "value_type": "str"},
            {"code": "host_diseases", "description": "", "value_type": "str"},
            {"code": "isolation_source", "description": "", "value_type": "int"},
            {"code": "lat", "description": "", "value_type": "float"},
            {"code": "lon", "description": "", "value_type": "float"},
        ]
        for detail_type in specimen_detail_types:
            session.add(models.SpecimenDetailType(**detail_type))

        ## add sample_detail_types
        sample_detail_types = [
            {"code": "extraction_method", "description": "", "value_type": "str"},
            {"code": "extraction_protocol", "description": "", "value_type": "float"},
            {"code": "extraction_date", "description": "", "value_type": "date"},
            {"code": "extraction_user", "description": "", "value_type": "str"},
            {"code": "dna_amplification", "description": "", "value_type": "bool"},
            {
                "code": "pre_sequence_concentration",
                "description": "",
                "value_type": "float",
            },
            {
                "code": "dilution_post_initial_concentration",
                "description": "",
                "value_type": "bool",
            },
            {"code": "input_volume", "description": "", "value_type": "float"},
        ]
        for detail_type in sample_detail_types:
            session.add(models.SampleDetailType(**detail_type))

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
