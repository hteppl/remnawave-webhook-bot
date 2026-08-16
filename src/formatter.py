from typing import Dict, Any

from src.formatters import (
    CRMEventFormatter,
    ErrorsEventFormatter,
    NodeEventFormatter,
    ServiceEventFormatter,
    TorrentBlockerEventFormatter,
    UserEventFormatter,
    UserHwidDevicesEventFormatter,
)
from src.l10n import get_translation as _


class MessageFormatter:
    def __init__(self):
        # `user_hwid_devices.` must be matched before `user.`
        self.formatters = {
            "user_hwid_devices.": UserHwidDevicesEventFormatter(),
            "user.": UserEventFormatter(),
            "node.": NodeEventFormatter(),
            "crm.": CRMEventFormatter(),
            "service.": ServiceEventFormatter(),
            "torrent_blocker.": TorrentBlockerEventFormatter(),
            "errors.": ErrorsEventFormatter(),
        }

    async def format_webhook_message(self, event_type: str, data: Dict[str, Any], timestamp: str, **kwargs) -> str:
        for prefix, formatter in self.formatters.items():
            if event_type.startswith(prefix):
                return await formatter.format(event_type, data, timestamp, **kwargs)

        return (
            f"<b>{_('message-header-event')}:</b> <code>{event_type}</code>\n"
            f"<b>{_('message-header-data-label')}:</b>\n<pre>{self._format_dict(data)}</pre>"
        )

    @staticmethod
    def _format_dict(d: Dict[str, Any], indent: int = 0) -> str:
        lines = []
        indent_str = "  " * indent
        for key, value in d.items():
            if isinstance(value, dict):
                lines.extend([f"{indent_str}{key}:", MessageFormatter._format_dict(value, indent + 1)])
            else:
                lines.append(f"{indent_str}{key}: {value}")
        return "\n".join(lines)
