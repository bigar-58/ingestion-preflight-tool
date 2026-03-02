from __future__ import annotations

from dataclasses import dataclass

@dataclass
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
    errors: list[str]