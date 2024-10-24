from datetime import datetime
from typing import Any, Dict, List, Optional
import pytest
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.importers.import_spreadsheet import import_specimens
from app.models import Specimen, SpecimenDetail

from app.tests.import_spreadsheet_testing_data import specimen_data, specimen_data_details

def find_detail_by_code(details, code: str) -> Optional[SpecimenDetail]:
    """
    Helper function to find a detail record by its type code.

    Args:
        details (List[SpecimenDetail]): The list of specimen details.
        code (str): The detail type code to search for.

    Returns:
        Optional[SpecimenDetail]: The detail record if found, otherwise None.
    """
    return next((detail for detail in details if detail.specimen_detail_type_code == code), None)

@pytest.mark.asyncio
async def test_import_specimens_details(
    db_session: AsyncSession, logger_mock
):
    # Import the first set of specimen data
    await import_specimens(db_session, specimen_data, logger_mock)
    
    # Check that the specimen data is imported correctly for accession "adfs1"
    specimen_record: Optional[Specimen] = await db_session.scalar(
        select(Specimen).options(joinedload(Specimen.details)).filter(Specimen.accession == "adfs1")
    )
    
    # Ensure that a record is returned
    assert specimen_record is not None, "Expected a specimen record with accession 'adfs1'"
    
    specimen_details = specimen_record.details
    
    # Check the value of a detail record with a code of "host"
    detail_host: Optional[SpecimenDetail] = find_detail_by_code(specimen_details, "host")
    assert detail_host is not None, "Expected a detail record with a code of 'host'"
    assert detail_host.value_str == specimen_data[0]["host"], f"Expected a value of '{specimen_data[0]['host']}' but found '{detail_host.value_str}'"
    
    # Check that there is no detail record with a code of "host_diseases"
    detail_host_diseases: Optional[SpecimenDetail] = find_detail_by_code(specimen_details, "host_diseases")
    assert detail_host_diseases is None, "Expected no detail record with a code of 'host_diseases'"
    
    # Check the value of a detail record with a code of "isolation_source"
    detail_isolation_source: Optional[SpecimenDetail] = find_detail_by_code(specimen_details, "isolation_source")
    assert detail_isolation_source is not None, "Expected a detail record with a code of 'isolation_source'"
    assert detail_isolation_source.value_str == specimen_data[0]["isolation_source"], f"Expected a value of '{specimen_data[0]['isolation_source']}' but found '{detail_isolation_source.value_str}'"
    
    # Check the value of a detail record with a code of "lat"
    detail_lat: Optional[SpecimenDetail] = find_detail_by_code(specimen_details, "lat")
    assert detail_lat is not None, "Expected a detail record with a code of 'lat'"
    assert detail_lat.value_float == specimen_data[0]["lat"], f"Expected a value of '{specimen_data[0]['lat']}' but found '{detail_lat.value_float}'"

    # Check the value of a detail record with a code of "lon"
    detail_lon: Optional[SpecimenDetail] = find_detail_by_code(specimen_details, "lon")
    assert detail_lon is not None, "Expected a detail record with a code of 'lon'"
    assert detail_lon.value_float == specimen_data[0]["lon"], f"Expected a value of '{specimen_data[0]['lon']}' but found '{detail_lon.value_float}'"
    
    # Update the specimen data with the specimen details for Specimen accession "asdf1"
    # Need to use flush and expire_all here to make the delete on the details to make the 
    # session aware of the changes. Could also use a commit here but that would write to the db
    await import_specimens(db_session, specimen_data_details, logger_mock, dryrun=True)
    await db_session.flush()
    db_session.expire_all()
    
    # Check that the specimen data is imported correctly for accession "adfs1"
    updated_specimen_record: Optional[Specimen] = await db_session.scalar(
        select(Specimen).options(joinedload(Specimen.details)).filter(Specimen.accession == "adfs1")
    )
    
    # Ensure that a record is returned
    assert updated_specimen_record is not None, "Expected a specimen record with accession 'adfs1'"
    
    updated_specimen_details = updated_specimen_record.details
    
    # Check the value of a detail record with a code of "host"
    update_detail_host: Optional[SpecimenDetail] = find_detail_by_code(updated_specimen_details, "host")
    assert update_detail_host is not None, "Expected a detail record with a code of 'host'"
    assert update_detail_host.value_str == specimen_data_details[0]["host"], f"Expected a value of '{specimen_data_details[0]['host']}' but found '{update_detail_host.value_str}'"
    
    # Check the value of a detail record with a code of "host_diseases"
    updated_detail_host_diseases: Optional[SpecimenDetail] = find_detail_by_code(updated_specimen_details, "host_diseases")
    assert updated_detail_host_diseases is not None, "Expected a detail record with a code of 'host_diseases'"
    assert updated_detail_host_diseases.value_str == specimen_data_details[0]["host_diseases"], f"Expected a value of '{specimen_data_details[0]['host_diseases']}' but found '{updated_detail_host_diseases.value_str}'"
    
    # Check that there is no detail record with a code of "isolation_source"
    updated_detail_isolation_source: Optional[SpecimenDetail] = find_detail_by_code(updated_specimen_details, "isolation_source")
    assert updated_detail_isolation_source is None, "Expected no detail record with a code of 'isolation_source'"
    
    # Check the value of a detail record with a code of "lat"
    updated_detail_lat: Optional[SpecimenDetail] = find_detail_by_code(updated_specimen_details, "lat")
    assert updated_detail_lat is not None, "Expected a detail record with a code of 'lat'"
    assert updated_detail_lat.value_float == specimen_data_details[0]["lat"], f"Expected a value of '{specimen_data_details[0]['lat']}' but found '{updated_detail_lat.value_float}'"

    # Check the value of a detail record with a code of "lon"
    updated_detail_lon: Optional[SpecimenDetail] = find_detail_by_code(updated_specimen_details, "lon")
    assert updated_detail_lon is not None, "Expected a detail record with a code of 'lon'"
    assert updated_detail_lon.value_float == specimen_data_details[0]["lon"], f"Expected a value of '{specimen_data_details[0]['lon']}' but found '{updated_detail_lon.value_float}'"
    
