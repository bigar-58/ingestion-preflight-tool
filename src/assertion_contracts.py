from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class OutputAssertionError:
    """
    code -> stable identifier for alerting
    message -> explanation of failure/error
    count -> (optional) additional numerical context
    """
    code: str 
    message: str
    count: int | None = None
    
@dataclass(frozen=True)
class OutputAssertionResult:
    """
    Result of post-clean assertions
    """
    ok: bool
    errors: list[OutputAssertionError]