from __future__ import annotations
from enum import Enum

class OutputWritePolicy(str, Enum):
    OVERWRITE = "OVERWRITE"
    FAIL_IF_EXISTS = "FAIL_IF_EXISTS"
    VERSIONED = "VERSIONED"