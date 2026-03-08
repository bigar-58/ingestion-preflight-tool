from __future__ import annotations

import argparse
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX_PATH = ROOT / "reports" / "index.jsonl"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="query-run-index",
        description="Query and print JSONL run index data with DuckDB"
    )
    parser.add_argument(
        "--index-path",
        type=Path,
        default=DEFAULT_INDEX_PATH,
        help=f"Path to a JSONL index file (default: {DEFAULT_INDEX_PATH})"
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    index_path = args.index_path
    
    if not index_path.exists():
        print(f"Run index not found: {index_path}")
        return
    
    con = duckdb.connect(database=":memory:")
    
    # NOTE read_json_auto infers schema based on JSONL input
    q = f"""
        SELECT
            run_id,
            dropzone,
            files_seen,
            unknown_policy,
            result_counts.accepted AS accepted,
            result_counts.quarantined AS quarantined,
            result_counts.unrouted AS unrouted,
            report_path
        FROM read_json_auto('{index_path.as_posix()}')
        ORDER BY run_id DESC
        """
    
    rows = con.execute(q).fetchall()
    columns = [desc[0] for desc in con.description]
    
    if not rows:
        print(f"Run index is empty: {index_path}")
        con.close()
        return
    
    #Formatting for print output for dynamic table widths
    widths = []
    for i, col in enumerate(columns):
        max_data_width = max(len(str(row[i])) for row in rows)
        widths.append(max(len(col), max_data_width))
    
    header = " | ".join(col.ljust(widths[i]) for i, col in enumerate(columns))
    separator = "-+-".join("-" * widths[i] for i in range(len(columns)))
    
    print(f"Index path: {index_path}")
    print(header)
    print(separator)
    for row in rows:
        print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(columns))))    
        
    con.close()
    
if __name__ == "__main__":
    main()
    