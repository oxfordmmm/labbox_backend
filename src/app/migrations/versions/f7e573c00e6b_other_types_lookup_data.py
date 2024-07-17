"""other-types-lookup-data

Revision ID: f7e573c00e6b
Revises: f01fce5ded1d
Create Date: 2024-03-21 14:11:59.217541

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f7e573c00e6b"
down_revision: Union[str, None] = "f01fce5ded1d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

other_types_data = [
    {
        "code": "control",
        "description": "control",
        "value_type": "str",
    },
    {
        "code": "status",
        "description": "Status",
        "value_type": "str",
    },
    {
        "code": "quality",
        "description": "quality",
        "value_type": "str",
    },
    {
        "code": "total_reads",
        "description": "total reads",
        "value_type": "float",
    },
    {
        "code": "tb_reads",
        "description": "TB reads",
        "value_type": "float",
    },
    {
        "code": "coverage",
        "description": "coverage",
        "value_type": "float",
    },
    {
        "code": "null_calls",
        "description": "null calls",
        "value_type": "int",
    },
]


def upgrade() -> None:
    for row in other_types_data:
        op.execute(
            sa.text(
                "INSERT INTO other_types (code, description, value_type) VALUES (:code, :description, :value_type)"
            ).bindparams(
                code=row["code"],
                description=row["description"],
                value_type=row["value_type"],
            )
        )


def downgrade() -> None:
    for row in other_types_data:
        op.execute(
            sa.text("DELETE FROM other_types WHERE code = :code").bindparams(
                code=row["code"],
            )
        )
