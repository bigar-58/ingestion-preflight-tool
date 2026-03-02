from __future__ import annotations
from enum import Enum

class UnknownDatasetPolicy(str, Enum):
    STRICT = "STRICT"
    PROFILE_ONLY = "PROFILE_ONLY"