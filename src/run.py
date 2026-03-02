from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from src.profiling import profile_csv
from src.quarantine import quarantine_file
from src.processed import archive_processed_file
from src.datasets import match_dataset
from src.partitioning import partition_from_filename

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
    validation_errors: list[dict] | None = None

def main() -> None: 
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    STAGING_CLEAN.mkdir(parents=True, exist_ok=True)
    STAGING_QUAR.mkdir(parents=True, exist_ok=True)
    STAGING_PROCESSED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    

    results: list[FileResult] = []

    files = sorted(DROPZONE.glob("*.csv"))
    for f in files: 
        #Profile
        profile = profile_csv(f)
        profile_dict = {
            "row_count": profile.row_count,
            "column_count": profile.column_count,
            "columns": profile.columns,
            "null_counts": profile.null_counts
        }

        #Get ingestion helpers
        spec = match_dataset(f.name)
        if spec is None:
            results.append(
                FileResult(
                    filename=f.name, 
                    status="accepted",
                    profile=profile_dict
                )   
            )
            continue

        #Validate 
        v = spec.validator(f)
        if not v.ok:
            quarantine_dest = quarantine_file(f, STAGING_QUAR)
            error_dicts = [
                {"code": e.code, "message": e.message, "count": e.count}
                for e in v.errors
            ]
            reason = ", ".join(sorted({e.code for e in v.errors}))
            results.append(
                FileResult(
                    filename=f.name, 
                    status="quarantined",
                    reason=reason,
                    profile= profile_dict,
                    outputs={"quarantine_path": str(quarantine_dest)},
                    error_dicts=error_dicts
                )   
            )
            continue
        
        #Cleaning
        part = partition_from_filename(f.name)
        base_dir = STAGING_CLEAN / spec.output_dirname
        if part is not None:
            base_dir = base_dir / f"{part.key}={part.val}"

        parquet_path = base_dir / spec.output_parquet_name
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