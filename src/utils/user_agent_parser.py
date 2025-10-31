from typing import Optional
from user_agents import parse


def get_device_info(user_agent_string: str) -> Optional[str]:
    """
    Parse user-agent string and return formatted device information.

    Args:
        user_agent_string: The user-agent string to parse

    Returns:
        Formatted device information string or None if parsing fails
    """
    if not user_agent_string:
        return None

    try:
        ua = parse(user_agent_string)

        # Build device parts
        parts = []

        # Browser info
        if ua.browser.family and ua.browser.family != "Other":
            browser_part = ua.browser.family
            if ua.browser.version_string and ua.browser.version_string != "0":
                browser_part += f" {ua.browser.version_string}"
            parts.append(browser_part)

        # OS info
        if ua.os.family and ua.os.family != "Other":
            os_part = ua.os.family
            if ua.os.version_string and ua.os.version_string != "0":
                os_part += f" {ua.os.version_string}"
            parts.append(f"on {os_part}")

        # Device type (Mobile, Tablet, Desktop, Bot, etc.)
        device_type = None
        if ua.is_mobile:
            device_type = "Mobile"
        elif ua.is_tablet:
            device_type = "Tablet"
        elif ua.is_pc:
            device_type = "Desktop"
        elif ua.is_bot:
            device_type = "Bot"

        if device_type:
            parts.append(f"({device_type})")

        return " ".join(parts) if parts else None

    except Exception:
        return None


print(get_device_info("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."))
