from __future__ import annotations

import json
from pathlib import Path
from typing import Any

def write_latest_report(report: dict[str, Any], reports_dir: Path) -> Path:
    """
    Write/overwrite reports/latest.json with the details of the most recent run report
    """
    reports_dir.mkdir(parents=True, exist_ok=True)
    latest_path = reports_dir / "latest.json"
    latest_path.write_text(json.dumps(report, indent=2))
    return latest_path

def append_report_index(report: dict[str, Any], reports_dir: Path) -> Path:
    """
    Appends one line JSON summary to the reports/index.jsonl for fast data exploration
    following a run
    """
    reports_dir.mkdir(parents=True, exist_ok=True)
    index_path = reports_dir / "index.jsonl"
    
    summary = {
        "run_id":report["run_id"],
        "dropzone":report["dropzone"],
        "files_seen":report["files_seen"],
        "unknown_policy":report.get("unknown_policy"),
        "result_counts": {
            "accepted": sum(1 for r in report["results"] if r["status"] == "accepted"),
            "quarantined": sum(1 for r in report["results"] if r["status"] == "quarantined"),
            "unrouted": sum(1 for r in report["results"] if r["status"] == "unrouted")
        },
        "report_path":str(reports_dir / f"run_{report['run_id']}.json")
    }
    
    #Write summary to output
    with index_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(summary) + "\n")
        
    return index_path
    
    
    