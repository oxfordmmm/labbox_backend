"""
This module contains the SQLAlchemy models for the LabBox database.

Please note for relationships such as

specimens: Mapped[List["Specimen"]] = relationship(
        "Specimen", back_populates="country_sample_taken"
    )

that do not have the lazy parameter set, when using async code you will need to
specify options in the parent query to load the related data. Either options
lazy='joined' for eager loading or lazy='selectin' for select-in loading. E.g.

specimen_record: Optional[Specimen] = await db_session.scalar(
        select(Specimen).options(joinedload(Specimen.details)).filter(Specimen.accession == "asdf1")
    )

"""

from datetime import date, datetime
from typing import Dict, List, Optional, get_args

from sqlalchemy import (
    JSON,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import (
    Mapped,
    configure_mappers,
    mapped_column,
    relationship,
    validates,
)
from sqlalchemy_continuum import make_versioned  # type: ignore

from app.constants import (
    NucleicAcidType,
    SampleCategory,
    ValueType,
    db_timestamp,
    db_user,
)
from app.db import Model
from app.upload_models import ImportModel

make_versioned(user_cls=None)  # type: ignore


class GpasLocalModel(Model):
    __abstract__ = True

    created_by: Mapped[db_user]
    created_at: Mapped[db_timestamp]
    updated_by: Mapped[db_user]
    updated_at: Mapped[db_timestamp]

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def update_from_importmodel(self, importmodel: ImportModel) -> None:
        for field in importmodel.model_fields:
            if hasattr(self, field):
                self[field] = importmodel[field]


class Owner(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(primary_key=True)
    site: Mapped[str] = mapped_column(String(50), nullable=False)
    user: Mapped[str] = mapped_column(String(50), nullable=False)

    specimens: Mapped[List["Specimen"]] = relationship(
        "Specimen", back_populates="owner"
    )

    UniqueConstraint(site, user)


class Specimen(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "specimens"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id"))
    accession: Mapped[str] = mapped_column(String(20), nullable=False)
    collection_date: Mapped[date] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    organism: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    country_sample_taken_code: Mapped[str] = mapped_column(ForeignKey("countries.code"))
    specimen_type: Mapped[str] = mapped_column(String(50), nullable=True)
    specimen_qr_code: Mapped[Text] = mapped_column(Text, nullable=True)
    bar_code: Mapped[Text] = mapped_column(Text, nullable=True)

    owner: Mapped[Owner] = relationship("Owner", back_populates="specimens")
    samples: Mapped[List["Sample"]] = relationship("Sample", back_populates="specimen")
    storages: Mapped[List["Storage"]] = relationship(
        "Storage", back_populates="specimen"
    )
    country_sample_taken: Mapped["Country"] = relationship(
        "Country", back_populates="specimens"
    )
    details: Mapped[List["SpecimenDetail"]] = relationship(
        "SpecimenDetail", back_populates="specimen"
    )

    __table_args__ = (
        UniqueConstraint(
            "accession",
            "collection_date",
            "organism",
            postgresql_nulls_not_distinct=True,
            name="ux_specimen",
        ),
    )


class SpecimenDetail(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "specimen_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    specimen_id: Mapped[int] = mapped_column(ForeignKey("specimens.id"))
    specimen_detail_type_code: Mapped[str] = mapped_column(
        ForeignKey("specimen_detail_types.code")
    )
    value_str: Mapped[str] = mapped_column(String(50), nullable=True)
    value_int: Mapped[int] = mapped_column(nullable=True)
    value_float: Mapped[float] = mapped_column(nullable=True)
    value_bool: Mapped[bool] = mapped_column(nullable=True)
    value_date: Mapped[date] = mapped_column(nullable=True)
    value_text: Mapped[Text] = mapped_column(Text, nullable=True)

    specimen: Mapped["Specimen"] = relationship("Specimen", back_populates="details")
    specimen_detail_type: Mapped["SpecimenDetailType"] = relationship(
        "SpecimenDetailType", back_populates="details"
    )

    UniqueConstraint(specimen_id, specimen_detail_type_code)


class SpecimenDetailType(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "specimen_detail_types"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[Text] = mapped_column(Text, nullable=True)
    value_type: Mapped[ValueType] = mapped_column(
        Enum(
            *get_args(ValueType),
            name="value_type",
            create_constraint=True,
            validate_strings=True,
        )
    )

    details: Mapped[List["SpecimenDetail"]] = relationship(
        "SpecimenDetail", back_populates="specimen_detail_type"
    )


class Country(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    code2: Mapped[str] = mapped_column(String(2), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    lat: Mapped[float] = mapped_column(nullable=False)
    lon: Mapped[float] = mapped_column(nullable=False)

    specimens: Mapped[List["Specimen"]] = relationship(
        "Specimen", back_populates="country_sample_taken"
    )


class Run(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    run_date: Mapped[date] = mapped_column(default=datetime.utcnow, nullable=False)
    site: Mapped[str] = mapped_column(String(20), nullable=False)
    sequencing_method: Mapped[str] = mapped_column(String(20), nullable=False)
    machine: Mapped[str] = mapped_column(String(20), nullable=False)
    user: Mapped[str] = mapped_column(String(5), nullable=True)
    number_samples: Mapped[int] = mapped_column(default=0, nullable=True)
    flowcell: Mapped[str] = mapped_column(String(20), nullable=True)
    passed_qc: Mapped[bool] = mapped_column(default=False, nullable=True)
    comment: Mapped[Text] = mapped_column(Text, nullable=True)

    samples: Mapped[List["Sample"]] = relationship("Sample", back_populates="run")


class Sample(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "samples"

    id: Mapped[int] = mapped_column(primary_key=True)
    specimen_id: Mapped[int] = mapped_column(ForeignKey("specimens.id"))
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    guid: Mapped[str] = mapped_column(String(64), unique=True)
    sample_category: Mapped[SampleCategory] = mapped_column(
        Enum(
            *get_args(SampleCategory),
            name="sample_category",
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=True,
    )
    _nucleic_acid_type: Mapped[List[NucleicAcidType]] = mapped_column(
        "nucleic_acid_type", MutableList.as_mutable(ARRAY(String)), nullable=True
    )

    @hybrid_property
    def nucleic_acid_type(self):  # type: ignore
        return self._nucleic_acid_type

    @nucleic_acid_type.setter  # type: ignore
    def nucleic_acid_type(self, value):
        self._nucleic_acid_type = (
            value if isinstance(value, list) else [] if value is None else list(value)
        )

    run: Mapped["Run"] = relationship("Run", back_populates="samples")
    specimen: Mapped["Specimen"] = relationship("Specimen", back_populates="samples")
    details: Mapped[List["SampleDetail"]] = relationship(
        "SampleDetail", back_populates="sample"
    )
    spikes: Mapped[List["Spike"]] = relationship("Spike", back_populates="sample")
    analyses: Mapped[List["Analysis"]] = relationship(
        "Analysis", back_populates="sample"
    )

    @validates("nucleic_acid_type")
    def validate_nucleic_acid_type(self, key, nucleic_acid_type):
        if not isinstance(nucleic_acid_type, list):
            raise ValueError("Nucleic acid type must be a list")
        # make sure only unique nucleic acid types are added
        return list(set(nucleic_acid_type))


class SampleDetail(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "sample_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey("samples.id"))
    sample_detail_type_code: Mapped[str] = mapped_column(
        ForeignKey("sample_detail_types.code")
    )
    value_str: Mapped[str] = mapped_column(String(50), nullable=True)
    value_int: Mapped[int] = mapped_column(nullable=True)
    value_float: Mapped[float] = mapped_column(nullable=True)
    value_bool: Mapped[bool] = mapped_column(nullable=True)
    value_date: Mapped[date] = mapped_column(nullable=True)
    value_text: Mapped[Text] = mapped_column(Text, nullable=True)

    sample: Mapped["Sample"] = relationship("Sample", back_populates="details")
    sample_detail_type: Mapped["SampleDetailType"] = relationship(
        "SampleDetailType", back_populates="details"
    )

    UniqueConstraint(sample_id, sample_detail_type_code)


class SampleDetailType(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "sample_detail_types"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[Text] = mapped_column(Text, nullable=True)
    value_type: Mapped[ValueType] = mapped_column(
        Enum(
            *get_args(ValueType),
            name="value_type",
            create_constraint=True,
            validate_strings=True,
        )
    )

    details: Mapped[list["SampleDetail"]] = relationship(
        "SampleDetail", back_populates="sample_detail_type"
    )


class Spike(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "spikes"

    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey("samples.id"))
    name: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[str] = mapped_column(String(20))

    sample: Mapped["Sample"] = relationship("Sample", back_populates="spikes")

    UniqueConstraint(sample_id, name)


class Analysis(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey("samples.id"))
    batch_name: Mapped[str] = mapped_column(String(20))
    assay_system: Mapped[str] = mapped_column(String(20))

    sample: Mapped["Sample"] = relationship("Sample", back_populates="analyses")
    speciations: Mapped[List["Speciation"]] = relationship(
        "Speciation", back_populates="analysis"
    )
    others: Mapped[List["Other"]] = relationship("Other", back_populates="analysis")
    drug_resistances: Mapped[List["DrugResistance"]] = relationship(
        "DrugResistance", back_populates="analysis"
    )
    mutations: Mapped[List["Mutations"]] = relationship(
        "Mutations", back_populates="analysis"
    )

    UniqueConstraint(sample_id, batch_name)


class Speciation(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "speciations"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"))
    species_number: Mapped[int] = mapped_column()
    species: Mapped[str] = mapped_column(String(100))
    sub_species: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    analysis_date: Mapped[Optional[date]] = mapped_column(
        default=datetime.utcnow, nullable=True
    )
    data: Mapped[Optional[Dict | List]] = mapped_column(type_=JSON, nullable=True)

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="speciations"
    )

    UniqueConstraint(analysis_id, species_number)


class Other(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "others"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"))
    other_type_code: Mapped[str] = mapped_column(ForeignKey("other_types.code"))
    value_str: Mapped[str] = mapped_column(String(50), nullable=True)
    value_int: Mapped[int] = mapped_column(nullable=True)
    value_float: Mapped[float] = mapped_column(nullable=True)
    value_bool: Mapped[bool] = mapped_column(nullable=True)
    value_date: Mapped[date] = mapped_column(nullable=True)
    value_text: Mapped[Text] = mapped_column(Text, nullable=True)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="others")
    other_type: Mapped["OtherType"] = relationship("OtherType", back_populates="others")

    UniqueConstraint(analysis_id, other_type_code)


class OtherType(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "other_types"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[Text] = mapped_column(Text, nullable=True)
    value_type: Mapped[ValueType] = mapped_column(
        Enum(
            *get_args(ValueType),
            name="value_type",
            create_constraint=True,
            validate_strings=True,
        )
    )

    others: Mapped[List["Other"]] = relationship("Other", back_populates="other_type")


class DrugResistance(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "drug_resistances"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"))
    antibiotic: Mapped[str] = mapped_column(String(20))
    drug_resistance_result_type_code: Mapped[str] = mapped_column(
        ForeignKey("drug_resistance_result_types.code")
    )

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="drug_resistances"
    )
    drug_resistance_result_type: Mapped["DrugResistanceResultType"] = relationship(
        "DrugResistanceResultType", back_populates="drug_resistances"
    )

    UniqueConstraint(analysis_id, antibiotic)


class DrugResistanceResultType(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "drug_resistance_result_types"

    code: Mapped[str] = mapped_column(String(1), primary_key=True)
    description: Mapped[Text] = mapped_column(Text, nullable=True)

    drug_resistances: Mapped[List["DrugResistance"]] = relationship(
        "DrugResistance", back_populates="drug_resistance_result_type"
    )


class Storage(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "storages"

    id: Mapped[int] = mapped_column(primary_key=True)
    specimen_id: Mapped[int] = mapped_column(ForeignKey("specimens.id"))
    freezer: Mapped[str] = mapped_column(String(50))
    shelf: Mapped[str] = mapped_column(String(50))
    rack: Mapped[str] = mapped_column(String(50))
    tray: Mapped[str] = mapped_column(String(50))
    box: Mapped[str] = mapped_column(String(50))
    box_location: Mapped[str] = mapped_column(String(50))
    storage_qr_code: Mapped[Text] = mapped_column(Text, nullable=False, unique=True)
    date_into_storage: Mapped[date] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    notes: Mapped[Text] = mapped_column(Text, nullable=True)

    specimen: Mapped["Specimen"] = relationship("Specimen", back_populates="storages")


class Mutations(GpasLocalModel):
    __versioned__: Dict = {}
    __tablename__ = "mutations"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"))
    species: Mapped[str] = mapped_column(String(100))
    drug: Mapped[str] = mapped_column(String(50))
    gene: Mapped[str] = mapped_column(String(50))
    mutation: Mapped[str] = mapped_column(String(50))
    position: Mapped[int] = mapped_column()
    ref: Mapped[str] = mapped_column(String(50))
    alt: Mapped[str] = mapped_column(String(50))
    coverage: Mapped[str] = mapped_column(String(50))
    prediction: Mapped[str] = mapped_column(String(50))
    evidence: Mapped[str] = mapped_column(String(255))
    evidence_json: Mapped[Text] = mapped_column(Text, nullable=True)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="mutations")

    UniqueConstraint(analysis_id, species, drug, gene, mutation)


configure_mappers()
