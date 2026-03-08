from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import shutil

def quarantine_file(src: Path, quarantine_dir: Path) -> Path: 
    """
    Moves a file into the quarantine directory along with a timestamp suffix
    to avoid naming collisions.

    Returns: Destination path
    """
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = quarantine_dir / f"{src.stem}__quarantined__{ts}{src.suffix}"
    shutil.move(str(src), str(dest))
    return dest