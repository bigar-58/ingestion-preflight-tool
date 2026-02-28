from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import shutil

def archive_processed_file(src: Path, processed_dir: Path) -> Path:
    """
    Moves a successfully processed file into processed/ with a timestamp
    """
    processed_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = processed_dir / f"{src.stem}__processed__{ts}{src.suffix}"
    shutil.move(str(src), str(dest))
    return dest