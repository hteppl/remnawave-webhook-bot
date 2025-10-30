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
        def format_used_traffic(value):
            """Convert bytes to human-readable format (MB/GB)."""
            used_bytes = int(value)
            if used_bytes == 0:
                return "0 GB"
            elif used_bytes < 1024 ** 3:  # Less than 1 GB
                used_mb = used_bytes / (1024 ** 2)
                return f"{used_mb:.2f} MB"
            else:
                used_gb = used_bytes / (1024 ** 3)
                return f"{used_gb:.2f} GB"

        def format_traffic_limit(value):
            """Convert bytes to human-readable format (GB or Unlimited)."""
            limit_bytes = int(value)
            if limit_bytes == 0:
                return _("date-unlimited")
            else:
                limit_gb = limit_bytes / (1024 ** 3)
                return f"{limit_gb:.2f} GB"

        def format_date(value):
            """Format date with days."""
            return format_date_with_days(value, _)

        def format_squads(value):
            """Format squads list."""
            return ", ".join([squad["name"] for squad in value])

        field_configs = [
            ('username', 'field-username', True),
            ('email', 'field-email', False),
            ('status', 'field-status', False),
            {
                'data_key': 'usedTrafficBytes',
                'translation_key': 'field-used-traffic',
                'formatter': format_used_traffic,
            },
            {
                'data_key': 'trafficLimitBytes',
                'translation_key': 'field-data-limit',
                'formatter': format_traffic_limit,
            },
            {
                'data_key': 'expireAt',
                'translation_key': 'field-expire',
                'formatter': format_date,
                'condition': lambda d: d.get('expireAt'),
            },
            {
                'data_key': 'createdAt',
                'translation_key': 'field-created-at',
                'formatter': format_date,
                'condition': lambda d: d.get('createdAt'),
            },
            {
                'data_key': 'activeInternalSquads',
                'translation_key': 'field-squads',
                'use_code': True,
                'formatter': format_squads,
                'condition': lambda d: d.get('activeInternalSquads'),
            },
        ]

        return self._format_fields(data, field_sep, field_configs)
