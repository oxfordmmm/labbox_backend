from typing import Any, Dict, List

run_data: List[Dict[str, Any]] = [
    {
        "code": "Run1",
        "run_date": "2024-01-01",
        "site": "SiteA",
        "sequencing_method": "illumina",
        "machine": "Machine1",
        "user": "User1",
        "number_samples": 10,
        "flowcell": "Flowcell1",
        "passed_qc": True,
        "comment": "First run",
    },
    {
        "code": "Run2",
        "run_date": "2024-01-01",
        "site": "SiteB",
        "sequencing_method": "ont",
        "machine": "Machine2",
        "user": "User2",
        "number_samples": 20,
        "flowcell": "Flowcell2",
        "passed_qc": False,
        "comment": "Second run",
    },
]

run_data2: List[Dict[str, Any]] = [
    {
        "code": "Run2",
        "run_date": "2024-01-02",
        "site": "SiteB",
        "sequencing_method": "pacbio",
        "machine": "Machine2",
        "user": "User2",
        "number_samples": 20,
        "flowcell": "Flowcell2",
        "passed_qc": False,
        "comment": "Second run",
    },
    {
        "code": "Run3",
        "run_date": "2024-01-01",
        "site": "SiteA",
        "sequencing_method": "illumina",
        "machine": "Machine3",
        "user": "User3",
        "number_samples": 11,
        "flowcell": "Flowcell3",
        "passed_qc": True,
        "comment": "Third run",
    },
]

# Combine the first entry of run_data with run_data2
run_combined_run_data = [run_data[0]] + run_data2

bad_run_data: List[Dict[str, Any]] = [
    {
        "code": "Run12345678901234567890",
        "run_date": "2024-13-13",
        "site": "Site12345678901234567890",
        "sequencing_method": "Nanaopore",
        "machine": "Machine12345678901234567890",
        "user": "User12345",
        "number_samples": -20,
        "flowcell": "Flowcell12345678901234567890",
        "passed_qc": False,
        "comment": "Second run",
    }
]

specimen_data: List[Dict[str, Any]] = [
    {
        "owner_site": "blah owner",
        "owner_user": "blah site",
        "accession": "adfs1",
        "collection_date": "2024-01-01",
        "organism": "sponge bob",
        "country_sample_taken_code": "GBR",
        "specimen_type": "test",
        "specimen_qr_code": "1234567890",
        "bar_code": "hjkl",
        "host": "Tyrannosaurus rex",
        "isolation_source": "London",
        "lat": 51.5074,
        "lon": -0.1278,
    },
    {
        "owner_site": "blah owner",
        "owner_user": "blah site",
        "accession": "adfs2",
        "collection_date": "2024-01-01",
        "organism": "square pants",
        "country_sample_taken_code": "DEU",
        "specimen_type": "test",
        "specimen_qr_code": "1234567890",
        "bar_code": "hjkl",
        "host": "Velociraptor mongoliensis",
        "host_diseases": "WMV",
        "isolation_source": "Berlin",
        "lat": 52.5200,
        "lon": 13.4050,
    },
]

specimen_data2: List[Dict[str, Any]] = [
    {
        "owner_site": "blah owner",
        "owner_user": "blah site",
        "accession": "adfs2",
        "collection_date": "2024-01-01",
        "organism": "square pants",
        "country_sample_taken_code": "DEU",
        "specimen_type": "test2",
        "specimen_qr_code": "blah2",
        "bar_code": "hjkl2",
        "host": "Velociraptor mongoliensis sub",
        "host_diseases": "WMV2",
        "isolation_source": "Berlin",
        "lat": 52.5200,
        "lon": 13.4050,
    },
    {
        "owner_site": "blah owner",
        "owner_user": "blah site",
        "accession": "adfs3",
        "collection_date": "2024-03-01",
        "organism": "krusty krab",
        "country_sample_taken_code": "GBR",
        "specimen_type": "test",
        "specimen_qr_code": "1234567890",
        "bar_code": "hjkl2",
        "host": "Tyrannosaurus rexis",
        "host_diseases": "TDS",
        "isolation_source": "London",
        "lat": 51.5074,
        "lon": -0.1278,
    },
]

# Combine the first entry of run_data with run_data2
combined_specimen_data = [specimen_data[0]] + specimen_data2

bad_specimen_data: List[Dict[str, Any]] = [
    {
        "owner_site": "",
        "owner_user": "",
        "accession": "adfs12345678901234567890",
        "collection_date": "2024-13-13",
        "organism": "square pants",
        "country_sample_taken_code": "DE",
    },
]


specimen_data_details: List[Dict[str, Any]] = [
    {
        "owner_site": "blah owner",
        "owner_user": "blah site",
        "accession": "adfs1",
        "collection_date": "2024-01-01",
        "organism": "sponge bob",
        "country_sample_taken_code": "GBR",
        "specimen_type": "test",
        "specimen_qr_code": "1234567890",
        "bar_code": "hjkl",
        "host": "Tyrannosaurus rex",
        "host_diseases": "TDS",
        "lat": 51.5074,
        "lon": -0.1278,
    },
]

sample_data: List[Dict[str, Any]] = [
    {
        "run_code": "Run1", 
        "accession": "adfs1",
        "collection_date": "2024-01-01",
        "organism": "sponge bob",
        "guid": "cf6f977e6e",
        "sample_category": "culture",
        "nucleic_acid_type": "DNA",
    },
    {
        "run_code": "Run2", 
        "accession": "adfs2",
        "collection_date": "2024-01-01",
        "organism": "square pants",
        "guid": "52ca5d5b8b",
        "sample_category": "culture",
        "nucleic_acid_type": "RNA",
    },
]
