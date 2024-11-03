"""lookup data

Revision ID: 8a13068d82dc
Revises: 9914ba1a02f5
Create Date: 2024-01-26 11:39:23.759016

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8a13068d82dc"
down_revision: Union[str, None] = "9914ba1a02f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

sample_detail_types_data = [
    {
        "code": "extraction_method",
        "description": "Extraction method",
        "value_type": "str",
    },
    {
        "code": "extraction_protocol",
        "description": "Extraction protocol",
        "value_type": "str",
    },
    {
        "code": "extraction_date",
        "description": "Extraction date",
        "value_type": "date",
    },
    {
        "code": "extraction_user",
        "description": "Extraction user",
        "value_type": "str",
    },
    {
        "code": "dna_amplification",
        "description": "DNA amplification",
        "value_type": "bool",
    },
    {
        "code": "pre_sequence_concentration",
        "description": "Pre sequence concentration",
        "value_type": "float",
    },
    {
        "code": "dilution_post_initial_concentration",
        "description": "Dilution post initial concentration",
        "value_type": "bool",
    },
    {
        "code": "input_volume",
        "description": "Input volume",
        "value_type": "float",
    },
    {
        "code": "prep_kit",
        "description": "Prep kit",
        "value_type": "str",
    },
    {
        "code": "illumina_index",
        "description": "Illumina index",
        "value_type": "str",
    },
    {
        "code": "ont_barcode",
        "description": "ONT barcode",
        "value_type": "str",
    },
    {
        "code": "library_pool_concentration",
        "description": "Library pool concentration",
        "value_type": "float",
    },
    {
        "code": "comment",
        "description": "Comment",
        "value_type": "text",
    },
]
drug_resistance_result_types_data = [
    {
        "code": "S",
        "description": "Susceptible",
    },
    {
        "code": "R",
        "description": "Resistant",
    },
    {
        "code": "U",
        "description": "Unclassified",
    },
    {
        "code": "F",
        "description": "Failed",
    },
    {
        "code": "-",
        "description": "Not tested",
    },
]


def upgrade() -> None:
    for row in sample_detail_types_data:
        op.execute(
            f"""
            INSERT INTO sample_detail_types (code, description, value_type)
            VALUES ('{row["code"]}', '{row["description"]}', '{row["value_type"]}')
            """
        )
    for row in drug_resistance_result_types_data:
        op.execute(
            f"""
            INSERT INTO drug_resistance_result_types (code, description)
            VALUES ('{row["code"]}', '{row["description"]}')
            """
        )


def downgrade() -> None:
    # don't delete the data as it may be referenced in other tables
    # for row in sample_detail_types_data:
    #     op.execute(
    #         f"""
    #         DELETE FROM sample_detail_types WHERE code = '{row["code"]}'
    #         """
    #     )
    # for row in drug_resistance_result_types_data:
    #     op.execute(
    #         f"""
    #         DELETE FROM drug_resistance_result_types WHERE code = '{row["code"]}'
    #         """
    #     )
    pass
