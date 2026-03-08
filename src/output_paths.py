from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from src.output_policy import OutputWritePolicy
from src.partitioning import Partition

@dataclass(frozen=True)
class OutputTarget:
    parquet_path: Path
    already_exists: bool

def resolve_output_target(
    staging_clean: Path,
    output_dirname: str,
    output_filename: str,
    partition: Partition | None,
    run_id: str,
    policy: OutputWritePolicy
) ->  OutputTarget:
    """
    Resolve output parquer path based on partitioning/write policies
    """
    base_dir = staging_clean / output_dirname
    if partition is not None:
        base_dir = base_dir / f"{partition.key}={partition.val}"
    
    if policy == OutputWritePolicy.VERSIONED:
        parquet_path = base_dir / f"{Path(output_filename).stem}_{run_id}.parquet"
    else:
        parquet_path = base_dir / output_filename
        
    return OutputTarget(
        parquet_path=parquet_path,
        already_exists=parquet_path.exists()
    )
    
    