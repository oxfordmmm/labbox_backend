from datetime import datetime
from typing import Any, Dict
import pytest
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.importers.import_spreadsheet import import_specimens
from app.models import Specimen
from app.tests.import_spreadsheet_testing_data import (
    specimen_data,
    specimen_data2,
    combined_specimen_data,
    bad_specimen_data,
)


def assert_specimen_record_matches(
    specimen_record: Specimen, specimen_entry: Dict[str, Any]
):
    """Test that the specimen record matches the specimen entry.

    This function asserts that the specimen record matches the specimen entry by comparing the
    specimen_record fields to the specimen_entry fields.

    Args:
        specimen_record (Specimen): The specimen record to check.
        specimen_entry (Dict[str, Any]): The specimen entry to check.
    """
    assert specimen_record.accession == specimen_entry["accession"]
    assert (
        specimen_record.collection_date
        == datetime.strptime(specimen_entry["collection_date"], "%Y-%m-%d").date()
    )
    assert specimen_record.organism == specimen_entry["organism"]
    assert (
        specimen_record.country_sample_taken_code
        == specimen_entry["country_sample_taken_code"]
    )
    assert specimen_record.specimen_type == specimen_entry["specimen_type"]
    assert specimen_record.specimen_qr_code == specimen_entry["specimen_qr_code"]
    assert specimen_record.bar_code == specimen_entry["bar_code"]


@pytest.mark.asyncio
async def test_import_specimens_update_insert(db_session: AsyncSession, logger_mock):
    """Test the import_specimens function when updating and inserting specimens.

    This test ensures that the import_specimens function correctly inserts and updates the
    specimen_data into the database and verifies the imported records against the expected
    combined_specimen_data. It also checks that the logger is called with the expected messages.

    Args:
        db_session (AsyncSession): The database session fixture.
        logger_mock (_type_): The mock logger fixture.
    """
    # Import the first set of specimen data
    await import_specimens(db_session, specimen_data, logger_mock, dryrun=True)

    result = await db_session.execute(
        select(Specimen).order_by(asc(Specimen.accession))
    )
    specimen_records = result.scalars().all()

    # check the record count
    assert len(specimen_records) == len(
        specimen_data
    ), f"Expected {len(specimen_data)} records, but found {len(specimen_records)}"

    # compare the retrieved records to specimen_data
    for specimen_record, specimen_entry in zip(specimen_records, specimen_data):
        assert_specimen_record_matches(specimen_record, specimen_entry)

    # Import the second set of specimen data
    await import_specimens(db_session, specimen_data2, logger_mock, dryrun=True)

    result = await db_session.execute(
        select(Specimen).order_by(asc(Specimen.accession))
    )
    specimen_records = result.scalars().all()

    # check the record count
    assert (
        len(specimen_records) == len(combined_specimen_data)
    ), f"Expected {len(combined_specimen_data)} records, but found {len(specimen_records)}"

    # compare the retrieved records to combined_specimen_data
    for specimen_record, specimen_entry in zip(
        specimen_records, combined_specimen_data
    ):
        assert_specimen_record_matches(specimen_record, specimen_entry)

    # check the logger messages
    assert len(logger_mock.mock_calls) == 5

    # Check the log messages from the first import
    assert logger_mock.mock_calls[0][0] == "info"
    assert (
        logger_mock.mock_calls[0][1][0]
        == "Specimens Sheet Row 2: Owner blah owner, blah site does not exist"
    )
    assert logger_mock.mock_calls[1][0] == "info"
    assert (
        logger_mock.mock_calls[1][1][0]
        == "Specimens Sheet Row 2: Specimen adfs1, 2024-01-01, sponge bob does not exist"
    )
    assert logger_mock.mock_calls[2][0] == "info"
    assert (
        logger_mock.mock_calls[2][1][0]
        == "Specimens Sheet Row 3: Specimen adfs2, 2024-01-01, square pants does not exist"
    )

    # Check the log messages from the second import
    assert logger_mock.mock_calls[3][0] == "info"
    assert (
        logger_mock.mock_calls[3][1][0]
        == "Specimens Sheet Row 2: Specimen adfs2, 2024-01-01, square pants already exists"
    )
    assert logger_mock.mock_calls[4][0] == "info"
    assert (
        logger_mock.mock_calls[4][1][0]
        == "Specimens Sheet Row 3: Specimen adfs3, 2024-03-01, krusty krab does not exist"
    )


@pytest.mark.asyncio
async def test_import_bad_specimen(
    db_session: AsyncSession,
    logger_mock,
):
    """Test the import_specimens function with bad specimen data.

    This test ensures that the import_specimens function correctly handles bad specimen data
    and does not import any records into the database. It also checks that the logger is called
    with the expected messages.

    Args:
        db_session (AsyncSession): The database session fixture.
        logger_mock (_type_): The mock logger fixture.
    """
    await import_specimens(db_session, bad_specimen_data, logger_mock, dryrun=True)

    result = await db_session.execute(
        select(Specimen).order_by(asc(Specimen.accession))
    )
    specimen_records = result.scalars().all()

    # check the record count
    assert (
        len(specimen_records) == 0
    ), f"Expected 0 records, but found {len(specimen_records)}"

    # check the logger messages
    assert len(logger_mock.mock_calls) == 3

    # Check the log messages from the import
    assert logger_mock.mock_calls[0][0] == "error"
    assert (
        logger_mock.mock_calls[0][1][0]
        == "Specimens Sheet Row 2 ('accession',) : String should have at most 20 characters"
    )

    assert logger_mock.mock_calls[1][0] == "error"
    assert (
        logger_mock.mock_calls[1][1][0]
        == "Specimens Sheet Row 2 ('collection_date',) : Input should be a valid date or datetime, month value is outside expected range of 1-12"
    )

    assert logger_mock.mock_calls[2][0] == "error"
    assert (
        logger_mock.mock_calls[2][1][0]
        == "Specimens Sheet Row 2 ('country_sample_taken_code',) : String should have at least 3 characters"
    )
