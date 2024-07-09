"""flatten sample details

Revision ID: fa75ffba1cf6
Revises: 5fb8a9b2fea7
Create Date: 2024-04-08 11:30:13.597551

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "fa75ffba1cf6"
down_revision: Union[str, None] = "5fb8a9b2fea7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE FUNCTION create_flattened_sample_details_view()
    RETURNS void AS $$
    DECLARE
        type_record record;
        -- can not use replace view here as it complains about columns being dropped
        sql_start TEXT := 'DROP VIEW IF EXISTS flattened_sample_details_view; CREATE VIEW flattened_sample_details_view AS SELECT s.id as sample_id';
        sql_columns TEXT := '';
        sql_joins TEXT := ' FROM samples s';
        column_alias TEXT;
        value_field TEXT;
    BEGIN
        -- Loop through each sample detail type to build the dynamic columns and joins
        FOR type_record IN SELECT * FROM sample_detail_types LOOP
            column_alias := 'sd_' || type_record.code::text;
            value_field := type_record.value_type::text;

            sql_joins := sql_joins || ' LEFT JOIN sample_details ' || column_alias || ' ON s.id = ' || column_alias || '.sample_id AND ' || column_alias || '.sample_detail_type_code = ' || quote_literal(type_record.code);

            sql_columns := sql_columns || ', ' || column_alias || '.value_' || value_field || ' AS ' || quote_ident(type_record.code);
        END LOOP;

        -- Combine parts to form the final SQL
        raise notice 'joins (%)', sql_joins;
        raise notice 'columns (%)', sql_columns;
        EXECUTE sql_start || sql_columns || sql_joins;
    END;
    $$ LANGUAGE plpgsql;
    """
    )
    # create the view for the first time
    op.execute("SELECT create_flattened_sample_details_view();")
    # create a function that returns a trigger to update the view
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
    # create a trigger to update the view when a sample is inserted or updated or deleted
    op.execute(
        """
    CREATE TRIGGER update_flattened_sample_details_view_trigger
    AFTER INSERT OR UPDATE OR DELETE ON sample_detail_types
    FOR EACH STATEMENT
    EXECUTE FUNCTION update_flattened_sample_details_view();
    """
    )


def downgrade() -> None:
    op.execute(
        """
    DROP TRIGGER update_flattened_sample_details_view_trigger ON samples;
    DROP FUNCTION update_flattened_sample_details_view();
    DROP VIEW flattened_sample_details_view;
    DROP FUNCTION create_flattened_sample_details_view();
    """
    )
