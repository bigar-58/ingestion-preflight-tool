from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from src.profiling import profile_csv
from src.quarantine import quarantine_file
from src.processed import archive_processed_file
from src.datasets import match_dataset

ROOT = Path(__file__).resolve().parents[1]
DROPZONE = ROOT / "dropzone"
STAGING_CLEAN = ROOT / "staging" / "clean" 
STAGING_QUAR = ROOT / "staging" / "quarantine" 
STAGING_PROCESSED = ROOT / "staging" / "processed"
REPORTS = ROOT / "reports"


@dataclass
class FileResult:
    filename: str
    status: str # "accepted" | "quarantined"
    reason: str | None = None
    profile: dict | None = None
    outputs: dict | None = None

def main() -> None: 
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    STAGING_CLEAN.mkdir(parents=True, exist_ok=True)
    STAGING_QUAR.mkdir(parents=True, exist_ok=True)
    STAGING_PROCESSED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    

    results: list[FileResult] = []

    files = sorted(DROPZONE.glob("*.csv"))
    for f in files: 
        #Get ingestion helpers
        spec = match_dataset(f.name)

        #Profile
        profile = profile_csv(f)
        profile_dict = {
            "row_count": profile.row_count,
            "column_count": profile.column_count,
            "columns": profile.columns,
            "null_counts": profile.null_counts
        }

        #Validate 
        if f.name == "users.csv":
            v = spec.validator(f)
            if not v.ok:
                quarantine_dest = quarantine_file(f, STAGING_QUAR)
                results.append(
                    FileResult(
                        filename=f.name, 
                        status="quarantined",
                        reason="; ".join(v.errors),
                        profile= profile_dict,
                        outputs={"quarantine_path": str(quarantine_dest)}
                    )   
                )
                continue
            
            #Cleaning
            parquet_path = STAGING_CLEAN / "users.parquet"
            spec.cleaner(f,parquet_path)

            processed_dest = archive_processed_file(f, STAGING_PROCESSED)

            #Log file result
            results.append(
                FileResult(
                    filename=f.name,
                    status="accepted",
                    profile=profile_dict,
                    outputs={
                        "parquet_path": str(parquet_path),
                        "processed_path": str(processed_dest)
                    },
                )
            )

            continue
        
        #Fail safe for unknown files
        results.append(
            FileResult(
                filename=f.name, 
                status="accepted",
                profile=profile_dict
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