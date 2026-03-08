from __future__ import annotations

from pathlib import Path

from src.pipeline import run_pipeline
from src.policy import UnknownDatasetPolicy

ROOT = Path(__file__).resolve().parents[1]

def main() -> None: 
    report_path = run_pipeline(
        dropzone=ROOT / "dropzone",
        staging_dir=ROOT / "staging",
        reports_dir=ROOT / "reports",
        unknown_policy=UnknownDatasetPolicy.PROFILE_ONLY,
        file_glob="*.csv"
    )
    print(f"Wrote report: {report_path}")

if __name__ =="__main__":
    main()