from __future__ import annotations

from src.contracts import ValidationError

def summarize_error_codes(errors: list[ValidationError]) -> str:
    """Compact summary string suitable for FileResult.reason."""
    return ", ".join(sorted({e.code for e in errors}))

def errors_to_dicts(errors: list[ValidationError]) -> list[dict]:
    """JSON-safe serialization for reports."""
    return [{"code": e.code, "message": e.message, "count": e.count} for e in errors]