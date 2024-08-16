import re
from datetime import date
from typing import Any, Dict, List

from pydantic import ValidationError
from sqlalchemy import not_, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

import app.models as models
from app.logs import CustomLogger
from app.upload_models import RunImport, SamplesImport, SpecimensImport, StoragesImport
from app.utils.utils import is_none_or_nan


async def import_data(
    session: AsyncSession,
    Runs: List[Dict[str, Any]],
    Specimens: List[Dict[str, Any]],
    Samples: List[Dict[str, Any]],
    Storage: List[Dict[str, Any]],
    logger: CustomLogger,
    dryrun: bool = False,
) -> bool:
    logger.info(
        f"Verifying and uploading data to database from Excel Workbook. {'Dry run enabled' if dryrun else ''}"
    )

    try:
        await import_runs(session, data=Runs, dryrun=dryrun, logger=logger)
        await session.flush()

        await import_specimens(session, data=Specimens, dryrun=dryrun, logger=logger)
        await session.flush()

        await import_samples(session, data=Samples, dryrun=dryrun, logger=logger)
        await session.flush()

        await import_storage(session, data=Storage, dryrun=dryrun, logger=logger)
        await session.flush()

    except Exception as e:
        logger.error(f"Failed to upload data: {e}")

    finally:
        if logger.error_occurred:  # type: ignore
            await session.rollback()
            logger.error("Upload failed, please see log messages for details")
            return False

        if dryrun:
            logger.info("Dry run mode, no data was uploaded")
            await session.rollback()
        else:
            logger.info("Data uploaded successfully")
            await session.commit()

    return True


async def import_runs(
    session: AsyncSession,
    data: List[Dict[str, Any]],
    logger: CustomLogger,
    dryrun: bool = False,
):
    for index, row in enumerate(data):
        try:
            run_import = RunImport(**row)

            run_record: models.Run | None = await session.scalar(
                select(models.Run).filter(models.Run.code == run_import.code)
            )
            if run_record:
                logger.info(
                    f"Runs Sheet Row {index+2}: Run {run_import.code} already exists{'' if dryrun else ', updating'}"
                )
            else:
                # add the run record
                run_record = models.Run(code=run_import.code)
                session.add(run_record)
                logger.info(
                    f"Runs Sheet Row {index+2}: Run {run_import.code} does not exist{'' if dryrun else ', adding'}"
                )
            run_record.update_from_importmodel(run_import)

        except ValidationError as err:
            for error in err.errors():
                logger.error(
                    f"Runs Sheet Row {index+2} {error['loc']} : {error['msg']}"
                )
        except DBAPIError as err:
            logger.error(f"Runs Sheet Row {index+2} : {err}")


async def import_specimens(
    session: AsyncSession,
    data: List[Dict[str, Any]],
    logger: CustomLogger,
    dryrun: bool = False,
):
    for index, row in enumerate(data):
        try:
            specimen_import = SpecimensImport(**row)

            # get the specimen owner
            owner_record = await owner(session, index, specimen_import, logger, dryrun)

            specimen_record: models.Specimen | None = await session.scalar(
                select(models.Specimen)
                .filter(models.Specimen.accession == specimen_import.accession)
                .filter(
                    models.Specimen.collection_date == specimen_import.collection_date
                )
                .filter(models.Specimen.organism == specimen_import.organism)
            )
            if specimen_record:
                logger.info(
                    f"Specimens Sheet Row {index+2}: Specimen {specimen_import.accession}, {specimen_import.collection_date}, {specimen_import.organism} already exists{'' if dryrun else ', updating'}"
                )
            else:
                specimen_record = models.Specimen(
                    accession=specimen_import.accession,
                    collection_date=specimen_import.collection_date,
                    organism=specimen_import.organism,
                )
                session.add(specimen_record)
                logger.info(
                    f"Specimens Sheet Row {index+2}: Specimen {specimen_import.accession}, {specimen_import.collection_date}, {specimen_import.organism} does not exist{'' if dryrun else ', adding'}"
                )
            specimen_record.update_from_importmodel(specimen_import)
            specimen_record.owner = owner_record
            await session.flush()

            await specimen_detail(session, specimen_record, specimen_import, logger)

        except ValidationError as err:
            for error in err.errors():
                logger.error(
                    f"Specimens Sheet Row {index+2} {error['loc']} : {error['msg']}"
                )
        except DBAPIError as err:
            logger.error(f"Specimens Sheet Row {index+2} : {err}")


async def owner(
    session: AsyncSession,
    index: int,
    specimen_import: SpecimensImport,
    logger: CustomLogger,
    dryrun: bool,
) -> models.Owner:
    owner_record: models.Owner | None = await session.scalar(
        select(models.Owner)
        .filter(models.Owner.site == specimen_import.owner_site)
        .filter(models.Owner.user == specimen_import.owner_user)
        .limit(1)
    )
    if not owner_record:
        owner_record = models.Owner(
            site=specimen_import.owner_site, user=specimen_import.owner_user
        )
        session.add(owner_record)
        logger.info(
            f"Specimens Sheet Row {index+2}: Owner {specimen_import.owner_site}, {specimen_import.owner_user} does not exist{'' if dryrun else ', adding'}"
        )
    return owner_record


async def specimen_detail(
    session: AsyncSession,
    specimen_record: models.Specimen,
    specimen_import: SpecimensImport,
    logger: CustomLogger,
) -> None:
    specimen_detail_types = await session.execute(select(models.SpecimenDetailType))

    for specimen_detail_type in specimen_detail_types.scalars().all():
        value = specimen_import[specimen_detail_type.code]

        specimen_detail_record: models.SpecimenDetail | None = await session.scalar(
            select(models.SpecimenDetail)
            .filter(models.SpecimenDetail.specimen == specimen_record)
            .filter(
                models.SpecimenDetail.specimen_detail_type_code
                == specimen_detail_type.code
            )
            .limit(1)
        )

        if value is None:
            if specimen_detail_record:
                await session.delete(specimen_detail_record)
            continue

        if not specimen_detail_record:
            specimen_detail_record = models.SpecimenDetail(
                specimen=specimen_record,
                specimen_detail_type_code=specimen_detail_type.code,
            )
            session.add(specimen_detail_record)

        specimen_detail_record["value_" + specimen_detail_type.value_type] = value


async def import_samples(
    session: AsyncSession,
    data: List[Dict[str, Any]],
    logger: CustomLogger,
    dryrun: bool = False,
):
    for index, row in enumerate(data):
        try:
            sample_import = SamplesImport(**row)

            run_record = await find_run(session, sample_import.run_code)
            specimen_record = await find_specimen(
                session,
                sample_import.accession,
                sample_import.collection_date,
                sample_import.organism,
            )

            sample_record: models.Sample | None = await session.scalar(
                select(models.Sample)
                .filter(models.Sample.guid == sample_import.guid)
                .limit(1)
            )

            if sample_record:
                logger.info(
                    f"Samples Sheet Row {index+2}: Sample {sample_import.guid} already exists{'' if dryrun else ', updating'}"
                )
            else:
                sample_record = models.Sample()
                session.add(sample_record)
                logger.info(
                    f"Samples Sheet Row {index+2}: Sample {sample_import.guid} does not exist{'' if dryrun else ', adding'}"
                )
            sample_record.update_from_importmodel(sample_import)
            sample_record.run = run_record
            sample_record.specimen = specimen_record

            await session.flush()

            await sample_detail(session, sample_record, sample_import)

            await spikes(session, sample_record, sample_import, index, logger)

        except ValidationError as err:
            for error in err.errors():
                logger.error(
                    f"Samples Sheet Row {index+2} {error['loc']} : {error['msg']}"
                )
        except ValueError as err:
            logger.error(f"Samples Sheet Row {index+2} : {err}")


async def find_run(session: AsyncSession, run_code: str) -> models.Run:
    run_record: models.Run | None = await session.scalar(
        select(models.Run).filter(models.Run.code == run_code).limit(1)
    )
    if not run_record:
        raise ValueError(f"Run {run_code} not found")
    return run_record


async def find_specimen(
    session: AsyncSession, accession: str, collection_date: date, organism: str | None
) -> models.Specimen:
    specimen_record: models.Specimen | None = await session.scalar(
        select(models.Specimen)
        .filter(models.Specimen.accession == accession)
        .filter(models.Specimen.collection_date == collection_date)
        .filter(models.Specimen.organism == organism)
        .limit(1)
    )
    if not specimen_record:
        raise ValueError(
            f"Specimen {accession}, {collection_date}, {organism} not found"
        )
    return specimen_record


async def sample_detail(
    session: AsyncSession, sample_record: models.Sample, sample_import: SamplesImport
) -> None:
    sample_detail_types = await session.execute(select(models.SampleDetailType))

    for sample_detail_type in sample_detail_types.scalars().all():
        value = sample_import[sample_detail_type.code]

        sample_detail_record: models.SampleDetail | None = await session.scalar(
            select(models.SampleDetail)
            .filter(models.SampleDetail.sample == sample_record)
            .filter(
                models.SampleDetail.sample_detail_type_code == sample_detail_type.code
            )
            .limit(1)
        )

        if value is None:
            if sample_detail_record:
                await session.delete(sample_detail_record)
            continue

        if not sample_detail_record:
            sample_detail_record = models.SampleDetail(
                sample=sample_record,
                sample_detail_type_code=sample_detail_type.code,
            )
            session.add(sample_detail_record)

        sample_detail_record["value_" + sample_detail_type.value_type] = value


async def spikes(
    session: AsyncSession,
    sample_record: models.Sample,
    sample_import: SamplesImport,
    index: int,
    logger: CustomLogger,
) -> None:
    spikes_names: dict = {
        k: v
        for k, v in sample_import.model_dump().items()
        if k.startswith("spike_name_")
    }
    spike_quantities: dict = {
        k: v
        for k, v in sample_import.model_dump().items()
        if k.startswith("spike_quantity_")
    }
    spike_fields = spikes_names | spike_quantities

    suffixes: List = []
    for k in spike_fields:
        match = re.search(r"\d+$", k)
        if match is not None:
            suffixes.append(int(match.group()))
    # make sure the suffixes are unique
    suffixes = list(set(suffixes))

    for i in suffixes:
        spike_name: str = sample_import.get(f"spike_name_{i}", "")
        spike_quantity: str = sample_import.get(f"spike_quantity_{i}", "")

        if is_none_or_nan(spike_name) or is_none_or_nan(spike_quantity):
            continue
        if is_none_or_nan(spike_name):
            logger.error(f"Samples Sheet Row {index+2} : Spike name is required")
            continue

        spike_record: models.Spike | None = await session.scalar(
            select(models.Spike)
            .filter(models.Spike.sample == sample_record)
            .filter(models.Spike.name == spike_name)
            .limit(1)
        )

        if not spike_record:
            spike_record = models.Spike(sample=sample_record, name=spike_name)
            session.add(spike_record)

        spike_record.quantity = spike_quantity

        clean_spike_names = [x for x in spikes_names.values() if not is_none_or_nan(x)]

        rs_to_delete = await session.scalars(
            select(models.Spike)
            .filter(not_(models.Spike.name.in_(clean_spike_names)))
            .filter(models.Spike.sample == sample_record)
        )
        for record in rs_to_delete:
            await session.delete(record)


async def import_storage(
    session: AsyncSession,
    data: List[Dict[str, Any]],
    logger: CustomLogger,
    dryrun: bool = False,
):
    for index, row in enumerate(data):
        try:
            storage_import = StoragesImport(**row)

            specimen_record = await find_specimen(
                session,
                storage_import.accession,
                storage_import.collection_date,
                storage_import.organism,
            )

            storage_record: models.Storage | None = await session.scalar(
                select(models.Storage)
                .filter(
                    models.Storage.storage_qr_code == storage_import.storage_qr_code
                )
                .limit(1)
            )

            if storage_record:
                logger.info(
                    f"Storage Sheet Row {index+2}: Storage {storage_import.storage_qr_code} already exists{'' if dryrun else ', updating'}"
                )
            else:
                storage_record = models.Storage()
                session.add(storage_record)
                logger.info(
                    f"Storage Sheet Row {index+2}: Storage {storage_import.storage_qr_code} does not exist{'' if dryrun else ', adding'}"
                )
            storage_record.update_from_importmodel(storage_import)
            storage_record.specimen = specimen_record

        except ValidationError as err:
            for error in err.errors():
                logger.error(
                    f"Storage Sheet Row {index+2} {error['loc']} : {error['msg']}"
                )
        except ValueError as err:
            logger.error(f"Storage Sheet Row {index+2} : {err}")
