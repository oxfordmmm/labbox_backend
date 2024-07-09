"""get view metadata

Revision ID: c1d15eeed4f0
Revises: f4183f1d16d9
Create Date: 2024-05-15 13:16:00.961585

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1d15eeed4f0"
down_revision: Union[str, None] = "f4183f1d16d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE FUNCTION get_view_columns(view_name text)
    RETURNS TABLE(column_name text, data_type text) AS $$
    BEGIN
        RETURN QUERY EXECUTE format(
            'SELECT attname AS column_name, format_type(atttypid, atttypmod) AS data_type
            FROM   pg_attribute
            WHERE  attrelid = %L::regclass
            AND    NOT attisdropped
            AND    attnum > 0
            ORDER  BY attnum;',
            view_name
        );
    END;
    $$ LANGUAGE plpgsql;
        """
    )


def downgrade() -> None:
    op.execute(
        """
    DROP FUNCTION get_view_columns(view_name text);
        """
    )
