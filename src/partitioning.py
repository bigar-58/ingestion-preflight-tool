from __future__ import annotations

import re
from dataclasses import dataclass

_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

@dataclass(frozen=True)
class Partition:
    """
    Represents a partition key/val pair used in output paths
    E.g.: key="dt", value="2026-02-28" -> dt=2026-02-28
    """
    key: str
    val: str

def partition_from_filename(filename: str) -> Partition | None:
    """
    Extract a dt partition from a filename if it contains YYYY-MM-DD

    Note: If file names are not following a formatting standard, runs may fail
    """
    m = _DATE_RE.search(filename)
    if not m:
        return None
    return Partition(key="dt", val=m.group(1))