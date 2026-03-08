from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import duckdb

from src.contracts import ValidationResult, ValidationError

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

def validate_users_csv(path: Path) -> ValidationResult:
    """
    Hard-fail validation ruels for users.csv
    """
    # Helper functions
    def missing_expr(col: str) -> str:
        return f'("{col}" IS NULL OR TRIM(CAST("{col}" AS VARCHAR)) = \'\')'

    errors: list[ValidationError] = []
    con = duckdb.connect(database=":memory:")
    rel = con.read_csv(str(path), header=True)
    con.register("rel", rel)

    # 1) Required columns (TODO: Have user inputted column names for validation)
    required_cols = ["user_id", "email", "signup_date", "country"]
    cols = rel.columns
    missing_cols = [c for c in required_cols if c not in cols]
    if missing_cols:
        errors.append(
            ValidationError(
                code="missing_required_columns",
                message=f"Missing columns: {missing_cols}",
                count=len(missing_cols)
            )
        )
        con.close()
        return ValidationResult(ok=False, errors=errors)
    
    # 2) Required fields not missing
    for col in ["user_id", "email", "signup_date"]:
        cnt = con.execute(f"SELECT COUNT(*) FROM rel WHERE {missing_expr(col)}").fetchone()[0]
        if cnt > 0:
            errors.append(
                ValidationError(
                code="missing_required_values",
                message=f"{col} has NULL/blank values",
                count=int(cnt)
            )
        )
    
    # 3) Unique user_id
    q = """
        SELECT COUNT(*)
        FROM (
            SELECT user_id
            FROM rel
            WHERE NOT (user_id IS NULL OR TRIM(CAST(user_id AS VARCHAR)) = '')
            GROUP BY user_id
            HAVING COUNT(*) > 1
        )
    """
    dup_cnt = con.execute(q).fetchone()[0]
    if dup_cnt > 0:
        errors.append(
            ValidationError(
                code="duplicate_key",
                message="user_id has duplicate values",
                count=dup_cnt
            )
        )

    # 4) Email format
    q = f"""
        SELECT COUNT(*)
        FROM rel
        WHERE NOT ({missing_expr("email")})
            AND NOT regexp_matches(CAST(email AS VARCHAR), '{EMAIL_REGEX}')
    """
    bad_email_cnt = con.execute(q).fetchone()[0]
    if bad_email_cnt > 0:
        errors.append(
            ValidationError(
                code="invalid_format",
                message=f"Email has invalid format",
                count=bad_email_cnt
            )
        )

    # 5) Date parse (DuckDB: try_strptime returns NULL on failure)
    q = f"""
        SELECT COUNT(*)
        FROM rel
        WHERE NOT ({missing_expr("signup_date")})
        AND try_strptime(CAST(signup_date AS VARCHAR), '%Y-%m-%d') IS NULL
    """
    bad_date_cnt = con.execute(q).fetchone()[0]
    if bad_date_cnt > 0:
        errors.append(
            ValidationError(
                code="invalid_date",
                message=f"signup_date has unparsable data as YYYY-MM-DD",
                count=bad_date_cnt
            )
        )

    con.close()
    return ValidationResult(ok=len(errors) == 0, errors=errors)