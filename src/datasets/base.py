from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from src.contracts import ValidationResult
from src.assertion_contracts import OutputAssertionResult

@dataclass(frozen=True)
class DatasetDefinition:
    """
    Generic interface to define dataset-specific behavior.
    
    Each dataset provides:
    1. File name for routing results
    2. Validator function for input files
    3. Dataset cleaner for writing to output parquet file
    4. optional output assertion for tests. 
    """
    dataset_name: str
    pattern: str 
    output_dirname: str
    output_parquet_name: str
    validator: Callable[[Path], ValidationResult]
    cleaner: Callable[[Path, Path], None]
    asserter: Callable[[Path], OutputAssertionResult] | None = None

