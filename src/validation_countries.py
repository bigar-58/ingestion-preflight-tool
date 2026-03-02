from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import duckdb

from src.validation import ValidationResult

COUNTRY_CODE_REGEX = r"^[A-Z]{2}$"

def validate_countries_csv(path: Path) -> ValidationResult:
    """
    Validation rules for countries*.csv

    Rules (hard fail):
    - Required columns exist: country_code, country_name, region
    - country_code required (not NULL/blank)
    - country_code unique
    - country_code must be 2 uppercase letters (ISO-3166 alpha-2-ish)
    """
    #Helper function for constructing similar conditions across validation q's
    def missing_expr(col: str) -> str: 
        return f'("{col}" IS NULL OR TRIM(CAST("{col}" AS VARCHAR)) = \'\')'

    errors: list[str] = []
    con = duckdb.connect(database=":memory:")
    rel = con.read_csv(str(path), header=True)
    con.register("rel", rel)

    required_cols = ["country_name", "country_name", "region"]
    missing_cols = [c for c in required_cols if c not in rel.columns]
    if missing_cols:
        errors.append(f"missing_required_columns: {missing_cols}")
        con.close()
        return ValidationResult(ok=False, errors=errors)

    missing_code_q = """
        SELECT COUNT(*) FROM rel WHERE {missing_expr('country_code')}
        """
    missing_code = con.execute(missing_code_q).fetchone()[0]

    dup_cnt_q = """
        SELECT COUNT(*) FROM (
            SELECT country_code
            FROM rel 
            WHERE NOT (country_code) IS NULL OR TRIM(CAST(country_code AS VARCHAR))
            GROUP BY country_code
            HAVING COUNT(*) > 1
        )
        """
    dup_cnt = con.execute(dup_cnt_q)
    if dup_cnt > 0:
        errors.append(f"duplicate_key: country_code has {dup_cnt} duplicated values(s)")
    
    bad_code_q = """
        SELECT COUNT(*)
        FROM rel 
        WHERE NOT {missing_expr('country_code')}
        AND NOT regexp_matches(TRIM(CAST(country_code AS VARCHAR)), '{COUNTRY_CODE_REGEX}')
        """
    bad_code = con.execute(bad_code_q)
    if bad_code > 0:
        errors.append(f"invalid_format: country_code has {bad_code} invalid_value(s)")
    
    con.close()
    return ValidationResult(ok=len(errors) == 0, errors=errors)