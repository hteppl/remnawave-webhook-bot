from typing import Optional

from user_agents import parse


def get_device_info(user_agent_string: str) -> Optional[str]:
    """
    Parse user-agent string and return formatted device information.

    Args:
        user_agent_string: The user-agent string to parse

    Returns:
        Formatted device information string or None if parsing fails

    Example:
        "Chrome 141.0.0 Windows 10" or "Safari 17.0 iOS 17.1"
    """
    if not user_agent_string:
        return None

    try:
        ua = parse(user_agent_string)
        parts = []

        # Browser
        if ua.browser.family and ua.browser.family != "Other":
            browser = ua.browser.family
            if ua.browser.version_string and ua.browser.version_string != "0":
                browser += f" {ua.browser.version_string}"
            parts.append(browser)

        # OS
        if ua.os.family and ua.os.family != "Other":
            os = ua.os.family
            if ua.os.version_string and ua.os.version_string != "0":
                os += f" {ua.os.version_string}"
            parts.append(os)

        return " ".join(parts) if parts else None

    except Exception:
        return None
