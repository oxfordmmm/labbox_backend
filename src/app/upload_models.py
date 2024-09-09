import re
from datetime import date
from typing import List, Optional

from iso3166 import countries
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    field_validator,
    model_validator,
)
from typing_extensions import Self

from app.constants import ExcelStr, NucleicAcidType, SampleCategory, SequencingMethod


class ImportModel(BaseModel):
    def __getitem__(self, item):
        return self.__dict__[item] if item in self.__dict__ else None

    def __setitem__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value

    def get(self, key, default=None):
        return self.__dict__.get(key, default)


class RunImport(ImportModel):
    code: ExcelStr = Field(max_length=20)
    run_date: date
    site: ExcelStr = Field(max_length=20)
    sequencing_method: SequencingMethod
    machine: ExcelStr = Field(max_length=20)
    user: Optional[ExcelStr] = Field(None, max_length=5)
    number_samples: Optional[PositiveInt] = None
    flowcell: Optional[ExcelStr] = Field(None, max_length=20)
    passed_qc: Optional[bool] = None
    comment: Optional[ExcelStr] = None


class SpecimensImport(ImportModel):
    owner_site: ExcelStr = Field(max_length=50)
    owner_user: ExcelStr = Field(max_length=50)
    accession: ExcelStr = Field(max_length=20)
    collection_date: date
    country_sample_taken_code: ExcelStr = Field(max_length=3, min_length=3)
    specimen_type: Optional[ExcelStr] = Field(None, max_length=50)
    specimen_qr_code: Optional[ExcelStr] = None
    bar_code: Optional[ExcelStr] = None
    organism: Optional[ExcelStr] = Field(None, max_length=50)
    host: Optional[ExcelStr] = Field(None, max_length=50)
    host_diseases: Optional[ExcelStr] = Field(None, max_length=50)
    isolation_source: Optional[ExcelStr] = Field(None, max_length=50)
    lat: Optional[float] = None
    lon: Optional[float] = None

    model_config = ConfigDict(extra="allow")

    @field_validator("country_sample_taken_code")
    def validate_country_sample_taken_code(cls, v):
        if v not in countries:
            raise ValueError('Country code "{v}" not recognised')
        return v


class SamplesImport(ImportModel):
    run_code: ExcelStr = Field(max_length=20)
    accession: ExcelStr = Field(max_length=20)
    collection_date: date
    organism: Optional[ExcelStr] = Field(None, max_length=50)
    guid: ExcelStr = Field(max_length=64)
    sample_category: Optional[SampleCategory] = None
    nucleic_acid_type: Optional[List[NucleicAcidType]] = None
    dilution_post_initial_concentration: Optional[bool] = None
    extraction_date: Optional[date] = None
    extraction_method: Optional[ExcelStr] = Field(max_length=50)
    extraction_protocol: Optional[ExcelStr] = Field(max_length=50)
    extraction_user: Optional[ExcelStr] = Field(max_length=50)
    illumina_index: Optional[ExcelStr] = Field(None, max_length=50)
    input_volume: Optional[float] = None
    library_pool_concentration: Optional[float] = None
    ont_barcode: Optional[ExcelStr] = Field(None, max_length=50)
    dna_amplification: Optional[bool] = None
    pre_sequence_concentration: Optional[float] = None
    prep_kit: Optional[ExcelStr] = Field(None, max_length=50)
    comment: Optional[ExcelStr] = None

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def split_nucleic_acid_type(cls, values):
        v = values.get("nucleic_acid_type")
        if v:
            # Convert to set and back to list to remove duplicates
            unique_values = list({value.strip() for value in v.split(",")})
            # Validate that each value is a valid NucleicAcidType
            for value in unique_values:
                if value not in NucleicAcidType.__args__:  # type: ignore
                    raise ValueError(f"{value} is not a valid NucleicAcidType value")
            values["nucleic_acid_type"] = unique_values
        return values


class StoragesImport(ImportModel):
    accession: ExcelStr = Field(max_length=20)
    collection_date: date
    organism: Optional[ExcelStr] = Field(None, max_length=50)
    freezer: ExcelStr = Field(max_length=50)
    shelf: ExcelStr = Field(max_length=50)
    rack: ExcelStr = Field(max_length=50)
    tray: ExcelStr = Field(max_length=50)
    box: ExcelStr = Field(max_length=50)
    box_location: ExcelStr = Field(max_length=50, pattern=r"^[A-T](1[0-9]|20|[1-9])$")
    storage_qr_code: ExcelStr
    date_into_storage: date
    notes: Optional[ExcelStr] = None


class GpasSummary(ImportModel):
    sample_name: str = Field(max_length=20)
    batch: str = Field(max_length=20, alias="Batch")
    main_species: Optional[str] = Field(None, max_length=50, alias="Main Species")
    resistance_prediction: str = Field(max_length=50, alias="Resistance Prediction")
    run_date: Optional[date] = None
    species: Optional[str]
    sub_species: Optional[str]
    control: Optional[str] = Field(None, alias="Control", max_length=50)
    status: Optional[str] = Field(None, max_length=50, alias="Status")
    quality: Optional[str] = Field(None, max_length=50, alias="Quality")
    total_reads: Optional[float] = Field(None, alias="Total Reads (M)")
    tb_reads: Optional[float] = Field(None, alias="TB Reads (M)")
    coverage: Optional[float] = Field(None, alias="Coverage")
    null_calls: Optional[int] = Field(None, alias="Null calls")

    model_config = ConfigDict(extra="allow")

    @field_validator("resistance_prediction", mode="after")
    @classmethod
    def validate_resistance_prediction(cls, v):
        if v == "Complete":
            return None
        if not re.match(r"^[SRUF_]{4}\s[SRUF_]{2}\s[SRUF_]{2}$", v):
            raise ValueError(f"Invalid drug resistance prediction {v}")
        return v

    @field_validator("sample_name", mode="before")
    @classmethod
    def validate_sample_name(cls, v):
        if not v:
            raise ValueError("Sample name not found in mapping file")
        return v

    @model_validator(mode="before")
    def split_species(self) -> Self:
        if self["Main Species"]:
            if "_" in self["Main Species"]:
                split_species = self["Main Species"].split("_", 1)
                self["species"] = split_species[0]
                self["sub_species"] = (
                    split_species[1] if len(split_species) > 1 else None
                )
            else:
                match = re.search(r"(.*)\s(\(.*?\))", self["Main Species"])
                self["species"] = match.group(1) if match else self["Main Species"]
                self["sub_species"] = match.group(2) if match else None
        else:
            self["species"] = None
            self["sub_species"] = None
        return self

    @model_validator(mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        return {k: None if v == "" else v for k, v in v.items()}


class Mutations(ImportModel):
    sample_name: str = Field(max_length=20)
    batch: str = Field(max_length=20, alias="Batch")
    species: str = Field(max_length=100, alias="Species")
    drug: str = Field(max_length=50, alias="Drug")
    gene: str = Field(max_length=50, alias="Gene")
    mutation: str = Field(max_length=50, alias="Mutation")
    position: int = Field(alias="Position")
    ref: str = Field(max_length=50, alias="Ref")
    alt: str = Field(max_length=50, alias="Alt")
    coverage: str = Field(max_length=50, alias="Coverage")
    prediction: str = Field(max_length=50, alias="Prediction")
    evidence: str = Field(alias="Evidence")
    evidence_json: Optional[str] = Field(None, alias="Evidence JSON")
