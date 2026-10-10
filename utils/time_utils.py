"""Runtime date and time helpers."""

import os
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover - Python < 3.9 fallback
    ZoneInfo = None


def current_runtime_datetime() -> datetime:
    """Return the current timezone-aware runtime datetime."""
    _load_env_file()
    timezone_name = os.environ.get("APP_TIMEZONE", "").strip()
    if timezone_name:
        tz = _load_timezone(timezone_name)
        return datetime.now(tz)
    return datetime.now().astimezone()


def current_analysis_datetime() -> str:
    """Return the current analysis timestamp as an ISO-8601 string."""
    return current_runtime_datetime().isoformat(timespec="seconds")


def current_analysis_date() -> str:
    """Return the current local analysis date."""
    return current_runtime_datetime().date().isoformat()


def normalize_analysis_datetime(analysis_date: str = None, analysis_datetime: str = None) -> str:
    """Return a datetime string consistent with an optional analysis date."""
    if analysis_datetime:
        return str(analysis_datetime)
    now_text = current_analysis_datetime()
    if not analysis_date:
        return now_text
    analysis_date = str(analysis_date)
    if now_text.startswith(analysis_date):
        return now_text
    return f"{analysis_date}T00:00:00"


def _load_timezone(timezone_name: str):
    if ZoneInfo is not None:
        try:
            return ZoneInfo(timezone_name)
        except Exception:
            pass
    if timezone_name in {"Asia/Shanghai", "Asia/Chongqing", "Asia/Harbin"}:
        return timezone(timedelta(hours=8), name=timezone_name)
    return datetime.now().astimezone().tzinfo


def _load_env_file() -> None:
    try:
        from env_loader import load_env_file
    except Exception:
        return
    load_env_file()
