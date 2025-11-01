from typing import Dict, Any

from src.formatters import UserEventFormatter, NodeEventFormatter, CRMEventFormatter, ServiceEventFormatter
from src.i18n import get_translation as _


class MessageFormatter:
    def __init__(self):
        self.formatters = {
            "user.": UserEventFormatter(),
            "node.": NodeEventFormatter(),
            "crm.": CRMEventFormatter(),
            "service.": ServiceEventFormatter(),
        }

    async def format_webhook_message(self, event_type: str, data: Dict[str, Any], timestamp: str) -> str:
        for prefix, formatter in self.formatters.items():
            if event_type.startswith(prefix):
                return await formatter.format(event_type, data, timestamp)

        return (
            f"{_('message-header-event-icon')} <b>{_('message-header-event-label')}:</b> <code>{event_type}</code>\n"
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
