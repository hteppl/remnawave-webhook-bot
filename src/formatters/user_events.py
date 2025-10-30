from typing import Dict, Any

from src.formatters.base import BaseEventFormatter
from src.i18n import get_translation as _
from src.utils import format_date_with_days


class UserEventFormatter(BaseEventFormatter):
    """Formatter for user-related events."""

    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str, **kwargs) -> str:
        """Format user event data."""
        translations = self.get_common_translations()
        fields_content = self._format_user_fields(data, translations["field_sep"])

        # Pass usage_percentage for bandwidth events
        event_message_kwargs = {"usage_percentage": data.get("usage_percentage", 0)}

        return self.build_standard_message(
            event_type=event_type,
            timestamp=timestamp,
            fields_content=fields_content,
            event_message_kwargs=event_message_kwargs,
        )

    def _format_user_fields(self, data: Dict[str, Any], field_sep: str) -> str:
        """Format user-specific fields."""
        msg = ""

        # Username
        if "username" in data:
            field_label = _("field-username")
            msg += self.format_field(field_sep, field_label, data["username"], use_code=True)

        # Email
        if "email" in data:
            field_label = _("field-email")
            msg += self.format_field(field_sep, field_label, data["email"])

        # Status
        if "status" in data:
            field_label = _("field-status")
            msg += self.format_field(field_sep, field_label, data["status"])

        # Used traffic
        if "usedTrafficBytes" in data:
            field_label = _("field-used-traffic")
            # Convert bytes to human-readable format
            used_bytes = int(data.get("usedTrafficBytes", 0))
            if used_bytes == 0:
                used_str = "0 GB"
            elif used_bytes < 1024 ** 3:  # Less than 1 GB
                used_mb = used_bytes / (1024 ** 2)
                used_str = f"{used_mb:.2f} MB"
            else:
                used_gb = used_bytes / (1024 ** 3)
                used_str = f"{used_gb:.2f} GB"
            msg += self.format_field(field_sep, field_label, used_str)

        # Data limit (using trafficLimitBytes from the webhook data)
        if "trafficLimitBytes" in data:
            field_label = _("field-data-limit")
            # Convert bytes to human-readable format
            limit_bytes = int(data.get("trafficLimitBytes", 0))
            if limit_bytes == 0:
                limit_str = _("date-unlimited")
            else:
                # Convert to GB
                limit_gb = limit_bytes / (1024 ** 3)
                limit_str = f"{limit_gb:.2f} GB"
            msg += self.format_field(field_sep, field_label, limit_str)

        # Expire (using expireAt from webhook data)
        if "expireAt" in data and data["expireAt"]:
            field_label = _("field-expire")
            formatted_date = format_date_with_days(data["expireAt"], _)
            msg += self.format_field(field_sep, field_label, formatted_date)

        # Created date
        if "createdAt" in data and data["createdAt"]:
            field_label = _("field-created-at")
            formatted_date = format_date_with_days(data["createdAt"], _)
            msg += self.format_field(field_sep, field_label, formatted_date)

        # Active squads
        if "activeInternalSquads" in data and data["activeInternalSquads"]:
            squads = ", ".join([squad["name"] for squad in data["activeInternalSquads"]])
            field_label = _("field-squads")
            msg += self.format_field(field_sep, field_label, squads, use_code=True)

        return msg
