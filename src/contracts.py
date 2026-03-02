from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ValidationError:
    """
    Structured validation error.
    
    code: unique identifier to error type
    message: Human-readable error msg
    count: Count of bad rows/rows failing data contract
    """
    code: str
    message: str
    count: int | None = None

@dataclass(frozen=True)
class ValidationResult:
    """
    Shared validator return type.

    ok:
      - True if the dataset passes all hard-fail checks
      - False if it must be quarantined / rejected

    errors:
      - Human-readable error codes/messages suitable for reports/logs.
      - Keep them stable so they can be searched and aggregated.
    """
    ok: bool
    errors: list[ValidationError]