from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import shutil

def archive_unrouted_file(src: Path, unrouted_dir: Path):
    """
    Move an unrouted/unknown dataset file into staging/unrouted directory with a
    timestamp
    """
    unrouted_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = unrouted_dir / f"{src.stem}__unrouted__{ts}{src.suffix}"
    shutil.move(str(src), str(dest))
    return dest