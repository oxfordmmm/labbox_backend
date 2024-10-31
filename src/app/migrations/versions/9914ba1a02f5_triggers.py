"""triggers

Revision ID: 9914ba1a02f5
Revises: 3fa077bb79a8
Create Date: 2024-01-26 11:17:44.170371

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9914ba1a02f5"
down_revision: Union[str, None] = "3fa077bb79a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tables: Sequence[str] = [
    "drug_resistance_result_types",
    "other_types",
    "owners",
    "runs",
    "sample_detail_types",
    "specimens",
    "samples",
    "analyses",
    "sample_details",
    "spikes",
    "drug_resistances",
    "others",
    "speciations",
]


def upgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_change_columns()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """
    )
    for table in tables:
        op.execute(
            f"""
        CREATE TRIGGER before_update_trigger_{table}
        BEFORE UPDATE ON {table}
        FOR EACH ROW EXECUTE PROCEDURE update_change_columns();
        """
        )


def downgrade() -> None:
    for table in tables:
        op.execute(
            f"""
        DROP TRIGGER before_update_trigger_{table};
        """
        )
    op.execute(
        """
    DROP FUNCTION update_change_columns();
    """
    )
