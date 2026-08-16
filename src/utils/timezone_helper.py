import logging
from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.config import config

logger = logging.getLogger(__name__)


def format_timestamp(timestamp_str: str) -> str:
    try:
        dt = datetime.fromisoformat(timestamp_str)
        dt_local = dt.astimezone(ZoneInfo(config.TIMEZONE))
        tz_abbr = dt_local.strftime("%Z")
        return dt_local.strftime(f"{config.TIME_FORMAT} {tz_abbr}")
    except ZoneInfoNotFoundError as e:
        logger.error(f"Timezone '{config.TIMEZONE}' not found. Install tzdata package. Error: {e}")
        return timestamp_str
    except Exception as e:
        logger.error(f"Failed to format timestamp with timezone {config.TIMEZONE}: {e}")
        return timestamp_str


def get_current_timestamp() -> str:
    try:
        dt = datetime.now(ZoneInfo(config.TIMEZONE))
        tz_abbr = dt.strftime("%Z")
        return dt.strftime(f"{config.TIME_FORMAT} {tz_abbr}")
    except ZoneInfoNotFoundError as e:
        logger.error(f"Timezone '{config.TIMEZONE}' not found. Install tzdata package. Error: {e}")
        dt = datetime.now(UTC)
        return dt.strftime(f"{config.TIME_FORMAT} UTC")
    except Exception as e:
        logger.error(f"Failed to get current timestamp with timezone {config.TIMEZONE}: {e}")
        dt = datetime.now(UTC)
        return dt.strftime(f"{config.TIME_FORMAT} UTC")
