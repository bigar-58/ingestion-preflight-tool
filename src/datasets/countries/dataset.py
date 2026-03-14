from __future__ import annotations

from src.datasets.base import DatasetDefinition
from src.datasets.countries.validation import validate_countries_csv
from src.datasets.countries.cleaning import clean_countries_csv_to_parquet
from src.datasets.countries.assertions import assert_countries_parquet

COUNTRIES_DATASET = DatasetDefinition(
    dataset_name="countries",
    pattern="countries*.csv",
    output_dirname="countries",
    output_parquet_name="countries.parquet",
    validator=validate_countries_csv,
    cleaner=clean_countries_csv_to_parquet,
    asserter=assert_countries_parquet
)