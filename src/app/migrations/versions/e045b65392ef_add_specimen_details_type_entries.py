"""Add specimen details type entries

Revision ID: e045b65392ef
Revises: 65638549e2b6
Create Date: 2024-02-20 10:59:27.191757

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e045b65392ef"
down_revision: Union[str, None] = "65638549e2b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

specimen_detail_types_data = [
    {
        "code": "organism",
        "description": "most descriptive organism name (to species if possible)",
        "value_type": "str",
    },
    {
        "code": "host",
        "description": "natural host of organism using full taxonomic name e.g., Homo sapiens",
        "value_type": "str",
    },
    {
        "code": "host_diseases",
        "description": "name of relevant disease",
        "value_type": "str",
    },
    {
        "code": "isolation_source",
        "description": "physical/environmental source of the sample",
        "value_type": "str",
    },
    {
        "code": "lat",
        "description": "geographical coordinates of location where sample was collected",
        "value_type": "float",
    },
    {
        "code": "lon",
        "description": "geographical coordinates of location where sample was collected",
        "value_type": "float",
    },
]


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    for row in specimen_detail_types_data:
        op.execute(
            f"""
            INSERT INTO specimen_detail_types (code, description, value_type)
            VALUES ('{row["code"]}', '{row["description"]}', '{row["value_type"]}')
            """
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    for row in specimen_detail_types_data:
        op.execute(
            f"""
            DELETE FROM sample_detail_types WHERE code = '{row["code"]}'
            """
        )
    # ### end Alembic commands ###
