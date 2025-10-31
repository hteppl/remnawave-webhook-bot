import logging
from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _
from src.services import IPGeolocationService
from src.utils.user_agent_parser import get_device_info

logger = logging.getLogger(__name__)


class ServiceEventFormatter(BaseEventFormatter):
    """Formatter for service-related events."""

    def __init__(self):
        self.geo_service = IPGeolocationService()

    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str, **kwargs) -> str:
        """Format service event data."""
        translations = self.get_common_translations()
        event_icon = self.get_event_icon(event_type)
        event_message = self.get_event_message(event_type)

        # Build message without category header for service events
        msg = f"{event_icon} <b>{translations['action_label']}:</b> {event_message}\n\n"

        # Only show data for specific service events
        show_data = event_type in ["service.login_attempt_failed", "service.login_attempt_success"]

        if show_data:
            # Get formatted fields with geolocation
            msg += await self._format_service_fields(data, translations["field_sep"])
            msg += "\n"

        msg += f"{translations['time_icon']} <b>{translations['time_label']}:</b> {timestamp}"

        return msg

    async def _format_service_fields(self, data: Dict[str, Any], field_sep: str) -> str:
        """Format service-specific fields with geolocation."""
        # Flatten nested objects (e.g., loginAttempt)
        flattened_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                flattened_data.update(value)
            else:
                flattened_data[key] = value

        # Format basic fields
        field_configs = [
            ("ip", "field-ip", True),
        ]

        msg = self._format_fields(flattened_data, field_sep, field_configs)

        # Add geolocation data if IP exists
        ip_address = flattened_data.get("ip")
        if ip_address:
            geo_data = await self.geo_service.get_location(ip_address)

            if geo_data:
                # Format country
                if geo_data.get("country"):
                    field_label = _("field-geo-country")
                    value = (
                        f"{geo_data['country']} ({geo_data['countryCode']})"
                        if geo_data.get("countryCode")
                        else geo_data["country"]
                    )
                    msg += self.format_field(field_sep, field_label, value)

                # Format region/city
                if geo_data.get("city") or geo_data.get("regionName"):
                    field_label = _("field-geo-city")
                    parts = []
                    if geo_data.get("city"):
                        parts.append(geo_data["city"])
                    if geo_data.get("regionName"):
                        parts.append(geo_data["regionName"])
                    value = ", ".join(parts)
                    msg += self.format_field(field_sep, field_label, value)

                # Format ISP
                if geo_data.get("isp"):
                    field_label = _("field-geo-isp")
                    msg += self.format_field(field_sep, field_label, geo_data["isp"])

        # Parse and format device info from user agent
        user_agent = flattened_data.get("userAgent")
        if user_agent:
            device_info = get_device_info(user_agent)
            if device_info:
                field_label = _("field-device")
                msg += self.format_field(field_sep, field_label, device_info)

        # Format remaining fields (User Agent, username, password)
        remaining_configs = [
            ("userAgent", "field-user-agent", False),
            ("username", "field-username", True),
            ("password", "field-password", True),
        ]

        msg += self._format_fields(flattened_data, field_sep, remaining_configs)

        return msg
