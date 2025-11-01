from datetime import datetime
from zoneinfo import ZoneInfo

from src.config import config


def format_timestamp(timestamp_str: str) -> str:
    """
    Format timestamp string to configured timezone.

    Args:
        timestamp_str: ISO format timestamp string (e.g., "2025-11-01T23:04:10.677Z")

    Returns:
        Formatted timestamp string in configured timezone
    """
    try:
        # Parse ISO format timestamp
        # Handle both Z suffix and timezone offsets
        if timestamp_str.endswith("Z"):
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(timestamp_str)

        # Convert to configured timezone
        tz = ZoneInfo(config.TIMEZONE)
        dt_local = dt.astimezone(tz)

        # Format as: "2025-11-01 23:04:10 MSK"
        # Get timezone abbreviation
        tz_abbr = dt_local.strftime("%Z")
        formatted = dt_local.strftime(f"%Y-%m-%d %H:%M:%S {tz_abbr}")

        return formatted

    except Exception as e:
        # Fallback to original timestamp if parsing fails
        return timestamp_str


def get_current_timestamp() -> str:
    """
    Get current timestamp in configured timezone.

    Returns:
        Formatted current timestamp string
    """
    try:
        tz = ZoneInfo(config.TIMEZONE)
        dt_local = datetime.now(tz)
        tz_abbr = dt_local.strftime("%Z")
        return dt_local.strftime(f"%Y-%m-%d %H:%M:%S {tz_abbr}")
    except Exception:
        # Fallback to UTC
        from datetime import timezone

        dt_utc = datetime.now(timezone.utc)
        return dt_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
