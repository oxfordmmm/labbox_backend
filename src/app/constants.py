from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BeforeValidator
from sqlalchemy import String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import mapped_column

db_timestamp = Annotated[
    datetime,
    mapped_column(TIMESTAMP(precision=3), server_default=text("NOW()"), nullable=False),
]

db_user = Annotated[
    str,
    mapped_column(String(50), server_default=text("CURRENT_USER"), nullable=False),
]

ValueType = Literal["str", "int", "float", "bool", "date", "text"]
SampleCategory = Literal["culture", "unclutured"]
NucleicAcidType = Literal["DNA", "RNA", "cDNA"]
SequencingMethod = Literal["illumina", "ont", "pacbio"]


def coerce_to_str(x: Any) -> str:
    return str(x).strip()


ExcelStr = Annotated[str, BeforeValidator(coerce_to_str)]

# Drugs in the order they appear in the summary csv. Key is the location in the string
tb_drugs = {
    0: "Isoniazid (INH)",
    1: "Rifampicin (RIF)",
    2: "Pyrazinamide (PZA)",
    3: "Ethambutol (EMB)",
    5: "Moxifloxacin (MXF)",
    6: "Levofloxacin (LEV)",
    8: "Linezolid (LZD)",
    9: "Bedaquiline (BDQ)",
}
