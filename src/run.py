from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from src.profiling import profile_csv
from src.validation import validate_users_csv
from src.quarantine import quarantine_file

ROOT = Path(__file__).resolve().parents[1]
DROPZONE = ROOT / "dropzone"
STAGING_CLEAN = ROOT / "staging" / "clean" 
STAGING_QUAR = ROOT / "staging" / "quarantine" 
REPORTS = ROOT / "reports"


@dataclass
class FileResult:
    filename: str
    status: str # "accepted" | "quarantined"
    reason: str | None = None
    profile: dict | None = None

def main() -> None: 
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    STAGING_CLEAN.mkdir(parents=True, exist_ok=True)
    STAGING_QUAR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    results: list[FileResult] = []

    files = sorted(DROPZONE.glob("*.csv"))
    for f in files: 
        profile = profile_csv(f)

        if f.name == "users.csv":
            v = validate_users_csv(f)
            if not v.ok:
                quarantine_file(f, STAGING_QUAR)
                results.append(
                    FileResult(
                        filename=f.name, 
                        status="quarantined",
                        reason="; ".join(v.errors),
                        profile={
                            "row_count": profile.row_count,
                            "column_count": profile.column_count,
                            "columns": profile.columns,
                            "null_counts": profile.null_counts
                        }
                    )   
                )

        results.append(
            FileResult(
                filename=f.name, 
                status="accepted",
                profile={
                    "row_count": profile.row_count,
                    "column_count": profile.column_count,
                    "columns": profile.columns,
                    "null_counts": profile.null_counts
                }
            )   
        )

    report = {
        "run_id": ts,
        "dropzone": str(DROPZONE),
        "files_seen": len(files),
        "results": [asdict(r) for r in results]
    }

    report_path = REPORTS / f"run_{ts}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote report: {report_path}")

if __name__ =="__main__":
    main()