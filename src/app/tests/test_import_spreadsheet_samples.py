import pytest
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.importers.import_spreadsheet import import_samples, import_specimens, import_runs
from app.models import Sample
from app.tests.import_spreadsheet_testing_data import sample_data, specimen_data, run_data


@pytest.mark.asyncio
async def test_import_samples_update_insert(db_session: AsyncSession, logger_mock):
    
    # both Specimens and Runs data are required as Samples are children of both
    await import_specimens(db_session, specimen_data, logger_mock, dryrun=False)
    await import_runs(db_session, run_data, logger_mock, dryrun=False)
    
    # Import the first set of sample data
    await import_samples(db_session, sample_data, logger_mock, dryrun=False)

    result = await db_session.execute(select(Sample))
    sample_records = result.scalars().all()

    # check the record count
    assert len(sample_records) == len(
        sample_data
    ), f"Expected {len(sample_data)} records, but found {len(sample_records)}"
    
    