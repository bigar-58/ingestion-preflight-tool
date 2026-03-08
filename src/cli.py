from __future__ import annotations

import argparse
from pathlib import Path

from src.pipeline import run_pipeline
from src.policy import UnknownDatasetPolicy

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="ingestion-preflight-toolkit")
    p.add_argument("--dropzone", type=Path, default=Path("dropzone"))
    p.add_argument("--staging", type=Path, default=Path("staging"))
    p.add_argument("--reports", type=Path, default=Path("reports"))
    p.add_argument("--glob", dest="file_glob", default="*.csv")
    p.add_argument(
        "--unknown-policy", 
        choices=[e.value for e in UnknownDatasetPolicy], 
        default=UnknownDatasetPolicy.PROFILE_ONLY.value
    )
    return p.parse_args()

def main() -> None:
    args = parse_args()
    report_path = run_pipeline(
        dropzone=args.dropzone,
        staging_dir=args.staging,
        reports_dir=args.reports,
        file_glob=args.file_glob,
        unknown_policy=UnknownDatasetPolicy(args.unknown_policy)
    )
    print(f"Wrote report: {report_path}")
    
if __name__ == "__main__":
    main()