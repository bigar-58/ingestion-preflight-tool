from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

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

def main() -> None: 
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    STAGING_CLEAN.mkdir(parents=True, exist_ok=True)
    STAGING_QUAR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    results: list[FileResult] = []

    files = sorted(DROPZONE.glob("*.csv"))
    for f in files: 
        # placeholder for the meantime everthing will be accepted
        results.append(FileResult(filename=f.name, status="accepted"))

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