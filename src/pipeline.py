from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from src.profiling import profile_csv
from src.datasets import match_dataset
from src.quarantine import quarantine_file
from src.processed import archive_processed_file
from src.unrouted import archive_unrouted_file
from src.policy import UnknownDatasetPolicy
from src.validation_utils import summarize_error_codes, errors_to_dicts
from src.partitioning import partition_from_filename

@dataclass
class FileResult:
    filename: str
    status: str  # "accepted" | "quarantined" | "unrouted"
    reason: str | None = None
    profile: dict | None = None
    outputs: dict | None = None
    validation_errors: list[dict] | None = None
    
def run_pipeline(
    dropzone: Path, 
    staging_dir: Path,
    reports_dir: Path, 
    unknown_policy: UnknownDatasetPolicy,
    file_glob: str = "*.csv"
) -> Path: 
    """
    Runs a single instance of an ingestion pass over the dropzone directory and
    outputs a JSON report into reports_dir
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    staging_clean = staging_dir / "clean"
    staging_quar = staging_quar / "quaratine"
    staging_processed = staging_dir / "processed"
    staging_unrouted = staging_dir / "unrouted"
    
    staging_clean.mkdir(parents=True, exist_ok=True)
    staging_quar.mkdir(parents=True, exist_ok=True)
    staging_processed.mkdir(parents=True, exist_ok=True)
    staging_unrouted.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    results = list[FileResult] = []
    files = sorted(dropzone.glob(file_glob))
    
    for f in files:
        #Profile dataset
        prof = profile_csv(f)
        prof_dict = {
            "row_count": prof.row_count,
            "column_count": prof.column_count,
            "columns": prof.columns,
            "null_counts": prof.null_counts
        }
        
        spec = match_dataset(f.name)
        if spec is None:
            if unknown_policy == UnknownDatasetPolicy.STRICT:
                quarantine_dest = quarantine_file(f, staging_quar)
                results.append(
                    FileResult(
                        filename=f.name,
                        status="quarantined",
                        reason="unknown_dataset",
                        validation_errors=[{
                            "code": "unknown_dataset",
                            "message": "No dataset route matched filename",
                            "count": None
                        }],
                        profile=prof_dict,
                        outputs={"quarantine_path": str(quarantine_dest)}
                    )
                )
            else: #POLICY_ONLY 
                unrouted_dest = archive_unrouted_file(f, staging_unrouted)
                results.append(
                    FileResult(
                        filename=f.name,
                        status="unrouted",
                        reason="unknown_dataset",
                        profile=prof_dict,
                        outputs={"unrouted_path": str(unrouted_dest)}
                    )
                )
        
        #Dataset validation
        v = spec.validator(f)
        if not v.ok:
            quarantine_dest = quarantine_file(f, staging_quar)
            results.append(
                FileResult(
                    filename=f.name,
                    status="quarantined",
                    reason=summarize_error_codes(v.errors),
                    validation_errors=errors_to_dicts(v.errors),
                    profile=prof_dict,
                    outputs={"quarantine_path": str(quarantine_dest)}
                )
            )
        else:
            part = partition_from_filename(f.name)
            
            base_dir = staging_clean / spec.output_dirname
            if part is not None:
                base_dir = base_dir / f"{part.key}={part.value}"
            parquet_path = base_dir / spec.output_parquet_name
            
            spec.cleaner(f, parquet_path)
            processed_dest = archive_processed_file(f, staging_processed)
            
            results.append(
                FileResult(
                    filename=f.name,
                    status="accepted",
                    profile=prof_dict,
                    outputs={
                        "parquet_path": str(parquet_path),
                        "processed_path": str(processed_dest)
                    }
                )
            )
        
        report = {
            "run_id": ts,
            "dropzone": str(dropzone),
            "file_seen": len(files),
            "unknown_policy": unknown_policy.value,
            "results": [asdict(r) for r in results]
        }
        
        report_path = reports_dir / f"run_{ts}.json"
        report_path.write_text(json.dumps(report, indent=2))
        return report_path    
        
    