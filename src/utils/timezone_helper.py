from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from src.config import config


def format_timestamp(timestamp_str: str) -> str:
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        tz = ZoneInfo(config.TIMEZONE)
        dt_local = dt.astimezone(tz)
        return dt_local.strftime(f"%Y-%m-%d %H:%M:%S {dt_local.strftime('%Z')}")
    except Exception:
        return timestamp_str


def get_current_timestamp() -> str:
    try:
        tz = ZoneInfo(config.TIMEZONE)
        dt = datetime.now(tz)
        return dt.strftime(f"%Y-%m-%d %H:%M:%S {dt.strftime('%Z')}")
    except Exception:
        dt = datetime.now(timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
