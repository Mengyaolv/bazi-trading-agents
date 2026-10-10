"""Small .env loader used by the local test scripts and graph setup."""

from pathlib import Path
import os
from typing import Optional, Union


def load_env_file(path: Optional[Union[str, Path]] = None) -> None:
    """Load KEY=VALUE pairs from a .env file without overriding real env vars."""
    env_path = Path(path) if path is not None else Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value
