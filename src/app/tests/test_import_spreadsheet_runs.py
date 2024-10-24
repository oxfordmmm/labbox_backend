from datetime import datetime
from typing import Any, Dict
import pytest
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.importers.import_spreadsheet import import_runs
from app.models import Run
from app.tests.import_spreadsheet_testing_data import (
    bad_run_data,
    run_combined_run_data,
    run_data,
    run_data2,
)

def assert_run_record_matches(run_record: Run, run_entry: Dict[str, Any]):
        assert run_record.code == run_entry["code"]
        assert (
            run_record.run_date
            == datetime.strptime(run_entry["run_date"], "%Y-%m-%d").date()
        )
        assert run_record.site == run_entry["site"]
        assert run_record.sequencing_method == run_entry["sequencing_method"]
        assert run_record.machine == run_entry["machine"]
        assert run_record.user == run_entry["user"]
        assert run_record.number_samples == run_entry["number_samples"]
        assert run_record.flowcell == run_entry["flowcell"]
        assert run_record.passed_qc == run_entry["passed_qc"]
        assert run_record.comment == run_entry["comment"]


@pytest.mark.asyncio
async def test_import_runs_update_insert(
    db_session: AsyncSession,
    logger_mock,
):
    """
    Test the import_runs function with updated run_data.

    This test ensures that the import_runs function correctly updates the existing
    run_data in the database with the new run_data2 and verifies the imported records
    against the expected combined run_data. It also checks that the logger is called
    with the expected messages.

    Args:
        db_session (AsyncSession): The database session fixture.
        logger_mock (CustomLogger): The mock logger fixture.
    """
    # intial import
    await import_runs(db_session, run_data, logger_mock, dryrun=True)
    
    result = await db_session.execute(select(Run).order_by(asc(Run.code)))
    run_records = result.scalars().all()

    # Check the record count
    assert len(run_records) == len(
        run_data
    ), f"Expected {len(run_data)} records, but found {len(run_records)}"

    # Compare the retrieved records to run_data
    for run_record, run_entry in zip(run_records, run_data):
        assert_run_record_matches(run_record, run_entry)
    
    # second import
    await import_runs(db_session, run_data2, logger_mock, dryrun=True)

    result = await db_session.execute(select(Run).order_by(asc(Run.code)))
    run_records = result.scalars().all()

    # Check the record count
    assert len(run_records) == len(
        run_combined_run_data
    ), f"Expected {len(run_combined_run_data)} records, but found {len(run_records)}"

    # Compare the retrieved records to run_data
    for run_record, run_entry in zip(run_records, run_combined_run_data):
        assert_run_record_matches(run_record, run_entry)

    # check the number of info log messages
    assert len(logger_mock.mock_calls) == 4

    # Check the log messages from the first import
    assert logger_mock.mock_calls[0][0] == "info"
    assert (
        logger_mock.mock_calls[0][1][0] == "Runs Sheet Row 2: Run Run1 does not exist"
    )
    assert logger_mock.mock_calls[1][0] == "info"
    assert (
        logger_mock.mock_calls[1][1][0] == "Runs Sheet Row 3: Run Run2 does not exist"
    )

    # Check the log messages from the second import
    assert logger_mock.mock_calls[2][0] == "info"
    assert (
        logger_mock.mock_calls[2][1][0] == "Runs Sheet Row 2: Run Run2 already exists"
    )
    assert logger_mock.mock_calls[3][0] == "info"
    assert (
        logger_mock.mock_calls[3][1][0] == "Runs Sheet Row 3: Run Run3 does not exist"
    )


@pytest.mark.asyncio
async def test_import_bad_run(
    db_session: AsyncSession,
    logger_mock,
):
    """
    Test the import_runs function with bad run_data.

    This test ensures that the import_runs function correctly logs the errors
    when importing bad run_data into the database.

    Args:
        db_session (AsyncSession): The database session fixture.
        logger_mock (CustomLogger): The mock logger fixture.
    """
    await import_runs(db_session, bad_run_data, logger_mock, dryrun=True)

    # check the number of error log messages
    assert len(logger_mock.mock_calls) == 8
    assert logger_mock.mock_calls[0][0] == "error"
    assert (
        logger_mock.mock_calls[0][1][0]
        == "Runs Sheet Row 2 ('code',) : String should have at most 20 characters"
    )
    assert logger_mock.mock_calls[1][0] == "error"
    assert (
        logger_mock.mock_calls[1][1][0]
        == "Runs Sheet Row 2 ('run_date',) : Input should be a valid date or datetime, month value is outside expected range of 1-12"
    )
    assert logger_mock.mock_calls[2][0] == "error"
    assert (
        logger_mock.mock_calls[2][1][0]
        == "Runs Sheet Row 2 ('site',) : String should have at most 20 characters"
    )
    assert logger_mock.mock_calls[3][0] == "error"
    assert (
        logger_mock.mock_calls[3][1][0]
        == "Runs Sheet Row 2 ('sequencing_method',) : Input should be 'illumina', 'ont' or 'pacbio'"
    )
    assert logger_mock.mock_calls[4][0] == "error"
    assert (
        logger_mock.mock_calls[4][1][0]
        == "Runs Sheet Row 2 ('machine',) : String should have at most 20 characters"
    )
    assert logger_mock.mock_calls[5][0] == "error"
    assert (
        logger_mock.mock_calls[5][1][0]
        == "Runs Sheet Row 2 ('user',) : Value should have at most 5 items after validation, not 9"
    )
    assert logger_mock.mock_calls[6][0] == "error"
    assert (
        logger_mock.mock_calls[6][1][0]
        == "Runs Sheet Row 2 ('number_samples',) : Input should be greater than 0"
    )
    assert logger_mock.mock_calls[7][0] == "error"
    assert (
        logger_mock.mock_calls[7][1][0]
        == "Runs Sheet Row 2 ('flowcell',) : Value should have at most 20 items after validation, not 28"
    )
