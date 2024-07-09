"""add views for samples, specimens, runs and storage

Revision ID: 14a2313333c1
Revises: c1d15eeed4f0
Create Date: 2024-05-15 14:57:12.950870

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "14a2313333c1"
down_revision: Union[str, None] = "c1d15eeed4f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
    CREATE VIEW samples_view AS
    select
        samples.id,
        specimens.accession,
        specimens.collection_date,
        runs.code as run_code,
        runs.run_date,
        samples.guid,
        samples.sample_category,
        samples.nucleic_acid_type,
        details.extraction_method,
        details.extraction_protocol,
        details.extraction_date,
        details.extraction_user,
        details.dna_amplification,
        details.pre_sequence_concentration,
        details.dilution_post_initial_concentration,
        details.input_volume,
        details.prep_kit,
        details.illumina_index,
        details.ont_barcode,
        details.library_pool_concentration,
        details.comment
    from
        samples
    inner join flattened_sample_details_view as details on samples.id = details.sample_id
    inner join specimens on samples.specimen_id = specimens.id
    inner join runs on samples.run_id = runs.id;
        """
    )

    op.execute(
        """
    CREATE VIEW specimens_view AS
    select
        specimens.id,
        owners."user",
        owners.site,
        specimens.accession,
        specimens.collection_date,
        specimens.country_sample_taken_code,
        specimens.specimen_type,
        specimens.specimen_qr_code,
        specimens.bar_code,
        details.organism,
        details.host,
        details.host_diseases,
        details.isolation_source,
        details.lat,
        details.lon
    from
        specimens
    inner join flattened_specimen_details_view as details on specimens.id = details.specimen_id
    inner join owners on specimens.owner_id = owners.id;
        """
    )

    op.execute(
        """
    CREATE VIEW runs_view AS
    select
        runs.id,
        runs.code,
        runs.run_date,
        runs.site,
        runs.sequencing_method,
        runs.machine,
        runs."user",
        runs.number_samples,
        runs.flowcell,
        runs.passed_qc,
        runs.comment
    from
        runs;
    """
    )

    op.execute(
        """
    CREATE VIEW storages_view AS
    select
        storages.id,
        specimens.accession,
        specimens.collection_date,
        storages.storage_qr_code,
        storages.date_into_storage,
        storages.freezer,
        storages.shelf,
        storages.rack,
        storages.tray,
        storages.box,
        storages.box_location,
        storages.notes
    from
        storages
    inner join specimens on storages.specimen_id = specimens.id
    """
    )


def downgrade() -> None:
    op.execute("DROP VIEW samples_view;")
    op.execute("DROP VIEW specimens_view;")
    op.execute("DROP VIEW runs_view;")
    op.execute("DROP VIEW storages_view;")
