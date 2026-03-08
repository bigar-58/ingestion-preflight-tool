from __future__ import annotations
from pathlib import Path
import duckdb

from src.assertion_contracts import OutputAssertionError, OutputAssertionResult

def assert_user_parquer(path: Path) -> OutputAssertionResult:
    """
    Assertions after clean up in parquet file
    
    Current assertions list:
    * Output is not empty
    * primary key user_id is unique
    * required columns are not null
    """
    errors: list[OutputAssertionResult] = []
    
    con = duckdb.connect(database=":memory:")
    parquet_path = path.as_posix()
    
    row_count = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{parquet_path})"
    ).fetchone()[0]
    if row_count == 0:
        errors.append(
            OutputAssertionError(
                code="empty_output",
                message="Output file has zero rows",
                count=0
            )
        )
    
    dup_cnt = con.execute(
        f"""
        SELECT user_id
        FROM read_parquet('{parquet_path}')
        WHERE user_id IS NOT NULL
        GROUP BY user_id
        HAVING COUNT(*) > 1
        """
    ).fetchone()[0]
    if dup_cnt > 0:
        errors.append(
            OutputAssertionError(
                code="non_unique_key",
                message="Output file contains duplicate user_id values",
                count=dup_cnt
            )
        )
        
    for col in ["user_id", "email", "signup_date"]:
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