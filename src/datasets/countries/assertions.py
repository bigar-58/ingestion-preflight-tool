from __future__ import annotations
from pathlib import Path
import duckdb

from src.assertion_contracts import OutputAssertionError, OutputAssertionResult

def assert_countries_parquet(path: Path) -> OutputAssertionResult:
    """
    Assertions for cleaned countries parquet.

    Current checks:
    * output is not empty
    * country_code is unique
    * required columns are not NULL: country_code, country_name, region
    """
    errors: list[OutputAssertionError] = []

    con = duckdb.connect(database=":memory:")
    parquet_path = path.as_posix()

    row_count = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{parquet_path}')"
    ).fetchone()[0]
    if row_count == 0:
        errors.append(
            OutputAssertionError(
                code="empty_output",
                message="Output file has zero rows",
                count=0,
            )
        )

    dup_cnt = con.execute(
        f"""
        SELECT COUNT(*) FROM (
          SELECT country_code
          FROM read_parquet('{parquet_path}')
          WHERE country_code IS NOT NULL
          GROUP BY country_code
          HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]
    if dup_cnt > 0:
        errors.append(
            OutputAssertionError(
                code="non_unique_key",
                message="Output file contains duplicate country_code values",
                count=int(dup_cnt),
            )
        )

    for col in ["country_code", "country_name", "region"]:
        null_cnt = con.execute(
            f"SELECT COUNT(*) FROM read_parquet('{parquet_path}') WHERE {col} IS NULL"
        ).fetchone()[0]
        if null_cnt > 0:
            errors.append(
                OutputAssertionError(
                    code="null_required_output",
                    message=f"Output file has NULL values in required column {col}",
                    count=int(null_cnt),
                )
            )

    con.close()
    return OutputAssertionResult(ok=len(errors) == 0, errors=errors)