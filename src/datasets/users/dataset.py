from __future__ import annotations

from src.datasets.base import DatasetDefinition
from src.datasets.users.validation import validate_users_csv
from src.datasets.users.cleaning import clean_users_csv_to_parquet
from src.datasets.users.assertions import assert_users_parquet

USERS_DATASET = DatasetDefinition(
    dataset_name="users",
    pattern="users*.csv",
    output_dirname="users",
    output_parquet_name="users.parquet",
    validator=validate_users_csv,
    cleaner=clean_users_csv_to_parquet,
    asserter=assert_users_parquet
)