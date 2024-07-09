from logging import Logger
from typing import Any, Dict, List

from app import models
from app.constants import tb_drugs
from app.upload_models import GpasSummary, Mutations
from app.utils.utils import merge_lists
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session


async def import_summary(
    session: Session,
    Summary: List[Dict[str, Any]],
    Mapping: List[Dict[str, Any]],
    logger: Logger,
    dryrun: bool = False,
):
    logger.info(
        f"Verifying and uploading data to database from Summary CSV. {'Dry run enabled' if dryrun else ''}"
    )

    merged_list = merge_lists(Summary, Mapping, "Sample ID", "remote_sample_name")

    try:
        for index, row in enumerate(merged_list):
            try:
                gpas_summary = GpasSummary(
                    **row,
                )

                analysis_record = await analysis(
                    session, gpas_summary, index, dryrun, logger
                )
                await session.flush()

                await speciation(
                    session, gpas_summary, index, dryrun, analysis_record, logger
                )
                await session.flush()

                await drugs(
                    session, gpas_summary, index, dryrun, analysis_record, logger
                )
                await session.flush()

                await details(session, gpas_summary, analysis_record)
                await session.flush()

            except ValidationError as err:
                for error in err.errors():
                    logger.error(
                        f"Summary Row {index+2} {error['loc']} : {error['msg']}"
                    )
            except DBAPIError as err:
                logger.error(f"Summary Row {index+2} : {err}")

            except ValueError as err:
                logger.error(f"Summary Row {index+2} : {err}")

    except Exception as e:
        logger.error(f"Failed to upload data: {e}")

    if logger.error_occurred:
        session.rollback()
        logger.error("Upload failed, please see log messages for details")
        return False

    if dryrun:
        logger.info("Dry run mode, no data was uploaded")
        session.rollback()
    else:
        logger.info("Data uploaded successfully")
        session.commit()

    return True


async def find_samples(session: Session, guid: str) -> models.Sample:
    result = await session.execute(
        select(models.Sample).filter(models.Sample.guid == guid)
    )
    sample = result.scalars().first()
    if not sample:
        raise ValueError(f"Sample guid {guid} does not exist")
    return sample


async def analysis(
    session: Session,
    row_model: GpasSummary | Mutations,
    index: int,
    dryrun: bool,
    logger: Logger,
):
    sample = await find_samples(session, row_model.sample_name)
    result = await session.execute(
        select(models.Analysis)
        .filter(models.Analysis.sample_id == sample.id)
        .filter(models.Analysis.batch_name == row_model.batch)
    )

    if analysis := (result.scalars().first()):
        analysis.assay_system = "GPAS TB"
    else:
        analysis = models.Analysis(
            sample=sample,
            batch_name=row_model.batch,
            assay_system="GPAS TB",
        )
        session.add(analysis)
        logger.info(
            f"Row {index+2}: Batch {row_model.batch}, Sample {row_model.sample_name} does not exist{'' if dryrun else ', adding'}"
        )

    return analysis


async def speciation(
    session: Session,
    gpas_summary: GpasSummary,
    index: int,
    dryrun: bool,
    analysis_record: models.Analysis,
    logger: Logger,
):
    if gpas_summary.species is None:
        logger.info(
            f"Summary row {index+2}: Speciation for Batch {gpas_summary.batch}, Sample {gpas_summary.sample_name} not found"
        )
        return None

    speciation = None
    if analysis_record and analysis_record.id:
        result = await session.execute(
            select(models.Speciation)
            .filter(models.Speciation.analysis == analysis_record)
            .filter(models.Speciation.species_number == 1)
        )
        speciation = result.scalars().first()

    if not speciation:
        speciation = models.Speciation(analysis=analysis_record, species_number=1)
        session.add(speciation)
        logger.info(
            f"Summary row {index+2}: Speciation for Batch {gpas_summary.batch}, Sample {gpas_summary.sample_name} does not exist{'' if dryrun else ', adding'}"
        )
    else:
        logger.info(
            f"Summary row {index+2}: Speciation for Batch {gpas_summary.batch}, Sample {gpas_summary.sample_name} already exists{'' if dryrun else ', updating'}"
        )

    speciation.species = gpas_summary.species
    speciation.sub_species = gpas_summary.sub_species
    speciation.analysis_date = gpas_summary.run_date

    return speciation


async def drugs(
    session: Session,
    gpas_summary: GpasSummary,
    index: int,
    dryrun: bool,
    analysis_record: models.Analysis,
    logger: Logger,
):
    if gpas_summary.resistance_prediction is None:
        logger.info(
            f"Summary row {index+2}: Drug Resistance for Batch {gpas_summary.batch}, Sample {gpas_summary.sample_name} Empty"
        )
        return

    for key, value in tb_drugs.items():
        result = await session.execute(
            select(models.DrugResistance)
            .filter(models.DrugResistance.analysis == analysis_record)
            .filter(models.DrugResistance.antibiotic == value)
        )
        if drug_resistance := (result.scalars().first()):
            logger.info(
                f"Summary row {index+2}: Drug Resistance for Batch {gpas_summary.batch}, Sample {gpas_summary.sample_name}, Antibiotic {value} already exists{'' if dryrun else ', updating'}"
            )
        else:
            drug_resistance = models.DrugResistance(
                analysis=analysis_record,
                antibiotic=value,
            )
            session.add(drug_resistance)
        drug_resistance.drug_resistance_result_type_code = (
            gpas_summary.resistance_prediction[key]
        )


async def details(
    sesion: Session, gpas_summary: GpasSummary, analysis_record: models.Analysis
):
    result = await sesion.execute(select(models.OtherType))
    other_types = result.scalars().all()
    for other_type in other_types:
        value = gpas_summary[other_type.code]

        result = await sesion.execute(
            select(models.Other)
            .filter(models.Other.analysis == analysis_record)
            .filter(models.Other.other_type_code == other_type.code)
        )
        other_record = result.scalars().first()

        if value is None:
            if other_record:
                sesion.delete(other_record)
            continue

        if not other_record:
            other_record = models.Other(
                analysis=analysis_record,
                other_type_code=other_type.code,
            )
            sesion.add(other_record)

        other_record["value" + other_type.value_type] = value


async def import_mutation(
    session: Session,
    Mutation: List[Dict[str, Any]],
    Mapping: List[Dict[str, Any]],
    logger: Logger,
    dryrun: bool = False,
):
    """upload data from a mutation csv"""
    logger.info(
        f"verifying and uploading data to database from mutation csv. {'dry run enabled' if dryrun else ''}"
    )

    try:
        merged_list = merge_lists(Mutation, Mapping, "Sample ID", "remote_sample_name")

        for index, row in enumerate(merged_list):
            try:
                mut = Mutations(
                    **row,
                )

                analysis_record = await analysis(session, mut, index, dryrun, logger)
                await session.flush()

                await mutation(session, mut, index, dryrun, analysis_record, logger)
                await session.flush()

            except ValidationError as err:
                for error in err.errors():
                    logger.error(
                        f"Mutation Row {index+2} {error['loc']} : {error['msg']}"
                    )
            except DBAPIError as err:
                logger.error(f"Mutation Row {index+2} : {err}")

            except ValueError as err:
                logger.error(f"Mutation Row {index+2} : {err}")

    except Exception as e:
        logger.error(f"Failed to upload data: {e}")

    if logger.error_occurred:
        session.rollback()
        logger.error("Upload failed, please see log messages for details")
        return False

    if dryrun:
        logger.info("Dry run mode, no data was uploaded")
        session.rollback()
    else:
        logger.info("Data uploaded successfully")
        session.commit()

    return True


async def mutation(
    session: Session,
    mutation: Mutations,
    index: int,
    dryrun: bool,
    analysis_record: models.Analysis,
    logger: Logger,
) -> models.Mutations | None:
    result = await session.execute(
        select(models.Mutations)
        .filter(models.Mutations.analysis == analysis_record)
        .filter(models.Mutations.species == mutation.species)
        .filter(models.Mutations.drug == mutation.drug)
        .filter(models.Mutations.gene == mutation.gene)
        .filter(models.Mutations.mutation == mutation.mutation)
    )
    if mut := (result.scalars().first()):
        logger.info(
            f"Mutation row {index+2}: Mutation for Batch {mutation.batch}, Sample {mutation.sample_name}, Gene {mutation.gene}, Position {mutation.position} already exists{'' if dryrun else ', updating'}"
        )
    else:
        mut = models.Mutations(
            analysis=analysis_record,
            species=mutation.species,
            drug=mutation.drug,
            gene=mutation.gene,
            mutation=mutation.mutation,
        )
        session.add(mut)
        logger.info(
            f"Mutation row {index+2}: Mutation for Batch {mutation.batch}, Sample {mutation.sample_name}, Species {mutation.species}, Drug {mutation.drug}, Gene {mutation.gene}, Mutation {mutation.mutation} does not exist{'' if dryrun else ', adding'}"
        )

    mut.position = mutation.position
    mut.ref = mutation.ref
    mut.alt = mutation.alt
    mut.coverage = mutation.coverage
    mut.prediction = mutation.prediction
    mut.evidence = mutation.evidence
    mut.evidence_json = mutation.evidence_json  # type: ignore

    return mut