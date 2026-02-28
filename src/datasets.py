from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from pathlib import Path

from src.validation import ValidationResult, validate_users_csv
from src.cleaning import clean_users_csv_to_parquet

@dataclass(frozen=True)
class DatasetSpec:
    """
    DatasetSpec will tie together the entire data contract by defining:
    - how to validate
    - how to clean
    - how to name outputs for a dataset
    """
    dataset_name: str
    validator: Callable[[Path], ValidationResult]
    cleaner: Callable[[Path, Path], None]
    output_parquet_name: str

DATASETS: dict[str, DatasetSpec] = {
    "users.csv": DatasetSpec(
        dataset_name="users",
        validator=validate_users_csv,
        cleaner=clean_users_csv_to_parquet,
        output_parquet_name="users.parquet"
    )
}