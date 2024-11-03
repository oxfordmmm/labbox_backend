"""mutations and unique constraints

Revision ID: 5fb8a9b2fea7
Revises: f7e573c00e6b
Create Date: 2024-04-03 14:10:50.453176

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5fb8a9b2fea7"
down_revision: Union[str, None] = "f7e573c00e6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tables: Sequence[str] = [
    "mutations",
]


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "mutations_version",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("analysis_id", sa.Integer(), autoincrement=False, nullable=True),
        sa.Column("species", sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column("drug", sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column("gene", sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column("mutation", sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column("position", sa.Integer(), autoincrement=False, nullable=True),
        sa.Column("ref", sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column("alt", sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column("coverage", sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column(
            "prediction", sa.String(length=50), autoincrement=False, nullable=True
        ),
        sa.Column(
            "evidence", sa.String(length=255), autoincrement=False, nullable=True
        ),
        sa.Column("evidence_json", sa.Text(), autoincrement=False, nullable=True),
        sa.Column(
            "created_by",
            sa.String(length=50),
            server_default=sa.text("'system'"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            sa.String(length=50),
            server_default=sa.text("'system'"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "id", "transaction_id", name=op.f("pk_mutations_version")
        ),
    )
    with op.batch_alter_table("mutations_version", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_mutations_version_end_transaction_id"),
            ["end_transaction_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_mutations_version_operation_type"),
            ["operation_type"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_mutations_version_transaction_id"),
            ["transaction_id"],
            unique=False,
        )

    op.create_table(
        "mutations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("analysis_id", sa.Integer(), nullable=False),
        sa.Column("species", sa.String(length=100), nullable=False),
        sa.Column("drug", sa.String(length=50), nullable=False),
        sa.Column("gene", sa.String(length=50), nullable=False),
        sa.Column("mutation", sa.String(length=50), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("ref", sa.String(length=50), nullable=False),
        sa.Column("alt", sa.String(length=50), nullable=False),
        sa.Column("coverage", sa.String(length=50), nullable=False),
        sa.Column("prediction", sa.String(length=50), nullable=False),
        sa.Column("evidence", sa.String(length=255), nullable=False),
        sa.Column("evidence_json", sa.Text(), nullable=True),
        sa.Column(
            "created_by",
            sa.String(length=50),
            server_default=sa.text("'system'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_by",
            sa.String(length=50),
            server_default=sa.text("'system'"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["analysis_id"],
            ["analyses.id"],
            name=op.f("fk_mutations_analysis_id_analyses"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mutations")),
        sa.UniqueConstraint(
            "analysis_id",
            "species",
            "drug",
            "gene",
            "mutation",
            name=op.f("uq_mutations_analysis_id"),
        ),
    )
    with op.batch_alter_table("analyses", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            batch_op.f("uq_analyses_sample_id"), ["sample_id", "batch_name"]
        )

    with op.batch_alter_table("others", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            batch_op.f("uq_others_analysis_id"), ["analysis_id", "other_type_code"]
        )

    with op.batch_alter_table("sample_details", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            batch_op.f("uq_sample_details_sample_id"),
            ["sample_id", "sample_detail_type_code"],
        )

    with op.batch_alter_table("specimen_details", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            batch_op.f("uq_specimen_details_specimen_id"),
            ["specimen_id", "specimen_detail_type_code"],
        )

    with op.batch_alter_table("spikes", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            batch_op.f("uq_spikes_sample_id"), ["sample_id", "name"]
        )
    for table in tables:
        op.execute(
            f"""
        CREATE TRIGGER before_update_trigger_{table}
        BEFORE UPDATE ON {table}
        FOR EACH ROW EXECUTE PROCEDURE update_change_columns();
        """
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    for table in tables:
        op.execute(
            f"""
        DROP TRIGGER before_update_trigger_{table} on {table};
        """
        )
    with op.batch_alter_table("spikes", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_spikes_sample_id"), type_="unique")

    with op.batch_alter_table("specimen_details", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("uq_specimen_details_specimen_id"), type_="unique"
        )

    with op.batch_alter_table("sample_details", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("uq_sample_details_sample_id"), type_="unique"
        )

    with op.batch_alter_table("others", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_others_analysis_id"), type_="unique")

    with op.batch_alter_table("analyses", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_analyses_sample_id"), type_="unique")

    op.drop_table("mutations")
    with op.batch_alter_table("mutations_version", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_mutations_version_transaction_id"))
        batch_op.drop_index(batch_op.f("ix_mutations_version_operation_type"))
        batch_op.drop_index(batch_op.f("ix_mutations_version_end_transaction_id"))

    op.drop_table("mutations_version")
    # ### end Alembic commands ###
