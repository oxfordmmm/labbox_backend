import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.importers.import_spreadsheet import owner
from app.models import Owner
from app.upload_models import SpecimensImport

from app.tests.import_spreadsheet_testing_data import specimen_data

@pytest.mark.asyncio
async def test_import_owners(db_session: AsyncSession, logger_mock):
    """ Test the import_owners function with initial specimen_data.
    
    This test ensures that the import_owners function correctly imports the initial
    specimen_data into the database and verifies the imported records against the expected specimen_data.

    Args:
        db_session (AsyncSession): The database session fixture.
        logger_mock (_type_): The mock logger fixture.
    """
    
    # yes i know you should not have loops in a test but this is a simple test
    # Add the owners in the specimen_data to the database
    for index, row in enumerate(specimen_data):
        specimen_import = SpecimensImport(**row)
        
        owner_record = await owner(db_session, index, specimen_import, logger_mock, dryrun=False)
        
        assert owner_record.site == specimen_import.owner_site
        assert owner_record.user == specimen_import.owner_user
    
    result = await db_session.execute(select(Owner))
    owner_records = result.scalars().all()
    
    # check the record count, we should have 1 owner record as we are adding the same owner twice
    assert len(owner_records) == 1, f"Expected 1 record, but found {len(owner_records)}"
    
    assert logger_mock.info.call_count == 1
    
        # Check the log messages from the import
    assert logger_mock.mock_calls[0][0] == "info"
    assert logger_mock.mock_calls[0][1][0] == 'Specimens Sheet Row 2: Owner blah owner, blah site does not exist, adding'