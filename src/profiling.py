from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import duckdb

@dataclass
class CsvProfile:
    row_count: int
    column_count: int
    columns: list[str]
    null_counts: dict[str, int]

def profile_csv(path: Path) -> CsvProfile:
    """
    CSV profiling done by DuckDB

    Assumptions
        1) Header row exists
    """
    conn = duckdb.connect(database=":memory:")
    rel = conn.read_csv(str(path), header=True)

    columns = rel.columns
    column_count = len(columns)

    # Register relation as a view to query
    conn.register("rel", rel)

    row_count = conn.execute("SELECT COUNT(*) FROM rel").fetchone()[0]

    null_counts: dict[str, int] = {}
    for col in columns: 
        q = f'SELECT COUNT(*) FROM rel WHERE "{col}" IS NULL'
        null_counts[col] = conn.execute(q).fetchone()[0]

    conn.close()

    return CsvProfile(
        row_count=row_count,
        column_count=column_count,
        columns=columns,
        null_counts=null_counts
    )