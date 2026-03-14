from __future__ import annotations

import fnmatch

from src.datasets.base import DatasetDefinition
from src.datasets.users.dataset import USERS_DATASET
from src.datasets.countries.dataset import COUNTRIES_DATASET

DATASETS: list[DatasetDefinition] = [
    USERS_DATASET,
    COUNTRIES_DATASET
]

def match_dataset(filename: str) -> DatasetDefinition | None:
    """
    Return the first matching dataset definition for input filename
    """
    for dataset in DATASETS: 
        if fnmatch.fnmatch(filename, dataset.pattern):
            return dataset
    return None


    