import pytest
from sqlalchemy import select

from app import models


@pytest.mark.asyncio
async def test_some_database_interaction(db_session):
    # Use test_session directly here to interact with the database

    async with db_session.begin():
        result: models.Owner = (
            await db_session.execute(select(models.Owner).limit(1))
        ).scalar_one_or_none()

    assert result is not None
