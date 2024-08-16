"""Dependant views need to be recreated

Revision ID: 85ef6de80849
Revises: 14a2313333c1
Create Date: 2024-08-16 13:49:39.094377

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "85ef6de80849"
down_revision: Union[str, None] = "14a2313333c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_flattened_specimen_details_view()
    RETURNS TRIGGER AS $$
    BEGIN
        -- Drop the dependent view first
        DROP VIEW IF EXISTS specimens_view;

        -- Call the function to recreate the flattened view
        PERFORM create_flattened_specimen_details_view();
        
        -- Recreate the dependent view
        CREATE VIEW specimens_view AS
        SELECT specimens.id,
            owners."user",
            owners.site,
            specimens.accession,
            specimens.collection_date,
            specimens.country_sample_taken_code,
            specimens.specimen_type,
            specimens.specimen_qr_code,
            specimens.bar_code,
            details.*
        FROM specimens
            JOIN flattened_specimen_details_view details ON specimens.id = details.specimen_id
            JOIN owners ON specimens.owner_id = owners.id;
            
        RETURN NULL;
    END;
    $$ language 'plpgsql';
    """
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_flattened_sample_details_view()
    RETURNS TRIGGER AS $$
    BEGIN
        -- Drop the dependent view first
        DROP VIEW IF EXISTS samples_view;
    
        -- Call the function to recreate the flattened view
        PERFORM create_flattened_sample_details_view();
        
        -- Recreate the dependent view
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
            details.*
        from
            samples
        inner join flattened_sample_details_view as details on samples.id = details.sample_id
        inner join specimens on samples.specimen_id = specimens.id
        inner join runs on samples.run_id = runs.id;
        
        RETURN NULL;
    END;
    $$ language 'plpgsql';
    """
    )


def downgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_flattened_specimen_details_view()
    RETURNS TRIGGER AS $$
    BEGIN
        PERFORM create_flattened_specimen_details_view();
        RETURN NULL;
    END;
    $$ language 'plpgsql';
    """
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_flattened_sample_details_view()
    RETURNS TRIGGER AS $$
    BEGIN
        PERFORM create_flattened_sample_details_view();
        RETURN NULL;
    END;
    $$ language 'plpgsql';
    """
    )
