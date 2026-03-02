from __future__ import annotations

from pathlib import Path
import duckdb

def clean_countries_csv_to_parquet(src_csv: Path, dest_parquet: Path) -> None:
    """
    Clean countries*.csv and write to Parquet

    Cleaning rules:
    - Trim strings
    - Empty strings -> NULL
    - Uppercase country_code
    """

    dest_parquet.parent.mkdir(parents=True)
    
    con = duckdb.connect(database=":memory:")
    rel = con.read_csv(str(src_csv, header=True))
    con.register("rel", rel)
    
    cleaning_q = """
        SELECT 
        NULLIF(UPPER(TRIM(CAST(country_code AS VARCHAR))), '') AS country_code,
        NULLIF(TRIM(CAST(country_name AS VARCHAR)), '') AS country_name,
        NULLIF(TRIM(CAST(region AS VARCHAR)), '') AS region
        FROM rel
        """
    con.execute(f"COPY ({cleaning_q}) TO ? (FORMAT_PARQUET)", [str(dest_parquet)])
    
    con.close()