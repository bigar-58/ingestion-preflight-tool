from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from pathlib import Path
import fnmatch

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
    output_dirname: str

@dataclass(frozen=True)
class DatasetRoute:
    """
    DatasetRoute maps file naming conventions to a DatasetSpec
    """
    pattern: str
    spec: DatasetSpec

ROUTES: list[DatasetRoute] = [
    DatasetRoute(
        pattern="users*.csv",
        spec=DatasetSpec(
            dataset_name="users",
            validator=validate_users_csv,
            cleaner=clean_users_csv_to_parquet,
            output_parquet_name="users.parquet",
            output_dir_name="users"
        ) 
    )
]

def match_dataset(filename: str) -> DatasetSpec | None:
    """
    Return the first matching DatasetSpec for a filename, or None if unknown.

    Note: current pattern is greedy and first match will always win.
    """
    for route in ROUTES:
        if fnmatch.fnmatch(filename, route.pattern):
            return route.spec

    return None