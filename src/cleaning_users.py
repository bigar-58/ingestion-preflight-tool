from __future__ import annotations

from pathlib import Path
import duckdb

def clean_users_csv_to_parquet(src_csv: Path, dest_parquet: Path) -> None: 
    """
    Script to clean and standardize input csv

    Cleaning rules
    --------------
    - Trim whitespace for string fields
    - Convert empty strings -> NULL for email/country.
    - Parse signup_date using YYYY-MM-DD; invalid parses become NULL.
    - Coerce user_id to BIGINT when possible; invalid parses become NULL.

    Note: 
    - Cleaning does not prevent hard failures from existing, validation handles this
    """
    dest_parquet.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(database=":memory:")
    rel = con.read_csv(str(src_csv), header=True)
    con.register("rel", rel)

    q = """
    CREATE OR REPLACE TEMP VIEW cleaned AS SELECT
        try_cast(NULLIF(CAST(user_id AS VARCHAR), '') AS BIGINT) AS user_id,
        NULLIF(TRIM(CAST(email AS VARCHAR)), '') AS email, 
        CAST(try_strptime(NULLIF(TRIM(CAST(signup_date AS VARCHAR)), ''), '%Y-%m-%d') AS DATE) AS signup_date,
        NULLIF(TRIM(CAST(country AS VARCHAR)), '') AS country
    FROM rel
    """
    cleaned = con.execute(q)

    con.execute(
        "COPY (SELECT * FROM cleaned) TO ? (FORMAT PARQUET)",
        [str(dest_parquet)]
    )

    con.close()