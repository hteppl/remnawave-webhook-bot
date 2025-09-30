from datetime import datetime
from typing import Callable, Optional


def parse_iso_date(date_string: str) -> Optional[datetime]:
    """Parse ISO 8601 date string to datetime object."""
    try:
        # Handle both with and without milliseconds
        if "." in date_string:
            # Has milliseconds
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        else:
            # No milliseconds
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def calculate_days_difference(date_string: str, from_now: bool = True) -> Optional[int]:
    """
    Calculate days difference between a date and now.

    Args:
        date_string: ISO 8601 date string
        from_now: If True, calculate from now to date (future). If False, from date to now (past).

    Returns:
        Number of days (positive for future, negative for past) or None if parsing fails
    """
    date = parse_iso_date(date_string)
    if not date:
        return None

    now = datetime.now(date.tzinfo)

    if from_now:
        delta = date - now
    else:
        delta = now - date

    return delta.days


def format_date_with_days(date_string: str, translator: Callable, show_days: bool = True) -> str:
    """
    Format date string with optional days difference.

    Args:
        date_string: ISO 8601 date string
        translator: Translation function (required)
        show_days: Whether to show days difference

    Returns:
        Formatted date string
    """
    date = parse_iso_date(date_string)
    if not date:
        return date_string

    # Format as readable date
    formatted = date.strftime("%Y-%m-%d %H:%M")

    if show_days:
        now = datetime.now(date.tzinfo)
        delta = date - now
        days = delta.days

        # Use localized strings
        if days > 0:
            days_text = translator("date-in-days", days=days)
            formatted += f" ({days_text})"
        elif days < 0:
            days_text = translator("date-days-ago", days=abs(days))
            formatted += f" ({days_text})"
        else:
            # Same day
            hours = delta.seconds // 3600
            if hours > 0:
                hours_text = translator("date-in-hours", hours=hours)
                formatted += f" ({hours_text})"
            else:
                today_text = translator("date-today")
                formatted += f" ({today_text})"

    return formatted
