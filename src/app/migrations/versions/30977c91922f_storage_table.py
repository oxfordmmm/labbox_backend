"""storage table

Revision ID: 30977c91922f
Revises: 8a13068d82dc
Create Date: 2024-02-14 09:52:07.579841

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "30977c91922f"
down_revision: Union[str, None] = "8a13068d82dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "storages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("specimen_id", sa.Integer(), nullable=False),
        sa.Column("freezer_id", sa.String(length=20), nullable=False),
        sa.Column("freezer_compartment", sa.String(length=20), nullable=False),
        sa.Column("freezer_sub_compartment", sa.String(length=20), nullable=False),
        sa.Column("storage_qr_code", sa.Text(), nullable=False),
        sa.Column("date_into_storage", sa.Date(), nullable=False),
        sa.Column(
            "created_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
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
            server_default=sa.text("CURRENT_USER"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["specimen_id"],
            ["specimens.id"],
            name=op.f("fk_storages_specimen_id_specimens"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_storages")),
        sa.UniqueConstraint(
            "storage_qr_code", name=op.f("uq_storages_storage_qr_code")
        ),
    )
    op.execute(
        f"""
        CREATE TRIGGER before_update_trigger_storages
        BEFORE UPDATE ON storages
        FOR EACH ROW EXECUTE PROCEDURE update_change_columns();
        """
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        f"""
        DROP TRIGGER before_update_trigger_storages;
        """
    )
    op.drop_table("storages")
    # ### end Alembic commands ###
