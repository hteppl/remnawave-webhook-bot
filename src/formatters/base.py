import inspect
from abc import ABC, abstractmethod
from html import escape
from typing import Dict, Any

from src.i18n import get_translation as _
from src.utils.timezone_helper import format_timestamp


class BaseEventFormatter(ABC):
    @abstractmethod
    async def format(self, event_type: str, data: Dict[str, Any], timestamp: str, **kwargs) -> str:
        pass

    @staticmethod
    def get_event_name(event_type: str) -> str:
        return "-".join(event_type.split(".")[1:]).replace("_", "-")

    @staticmethod
    def get_event_category(event_type: str) -> str:
        return event_type.split(".")[0]

    @staticmethod
    def escape_value(value: Any) -> str:
        if value is None or str(value).strip().lower() == "none":
            return "-"
        return escape(str(value))

    def format_field(self, field_sep: str, field_label: str, value: Any, use_code: bool = False) -> str:
        escaped = self.escape_value(value)
        return (
            f"{field_sep}{field_label}: <code>{escaped}</code>\n"
            if use_code
            else f"{field_sep}{field_label}: {escaped}\n"
        )

    def _format_fields(self, data: Dict[str, Any], field_sep: str, field_configs: list) -> str:
        msg = ""
        for config in field_configs:
            if isinstance(config, tuple):
                data_key, translation_key, use_code = config
                if data_key in data:
                    msg += self.format_field(field_sep, _(translation_key), data[data_key], use_code)
                continue

            data_key = config["data_key"]
            translation_key = config["translation_key"]
            use_code = config.get("use_code", False)
            formatter = config.get("formatter")
            nested = config.get("nested")
            condition = config.get("condition")

            if condition and not condition(data):
                continue

            value = None
            value_found = False

            if nested:
                obj = data
                for key in nested.split("."):
                    if isinstance(obj, dict) and key in obj:
                        obj = obj[key]
                    else:
                        obj = None
                        break
                value = obj
                value_found = True
            elif data_key in data:
                value = data[data_key]
                value_found = True

            if not value_found:
                continue

            if formatter:
                sig = inspect.signature(formatter)
                value = formatter(value) if len(sig.parameters) == 1 else formatter(value, data)

            msg += self.format_field(field_sep, _(translation_key), value, use_code)

        return msg

    @staticmethod
    def get_common_translations() -> Dict[str, str]:
        return {
            "action": _("message-header-action"),
            "time": _("message-header-time"),
            "field_sep": _("message-separator-field"),
        }

    def get_event_icon(self, event_type: str) -> str:
        category = self.get_event_category(event_type)
        event_name = self.get_event_name(event_type)
        icon_key = f"event-{category}-{event_name}-icon"
        icon = _(icon_key)
        return icon if icon != icon_key else ""

    def get_event_message(self, event_type: str, **kwargs) -> str:
        category = self.get_event_category(event_type)
        event_name = self.get_event_name(event_type)
        msg_key = f"event-{category}-{event_name}-message"
        return _(msg_key, **kwargs) if kwargs else _(msg_key)

    def get_category_header(self, event_type: str) -> str:
        category = self.get_event_category(event_type)
        return _(f"event-{category}-header")

    def build_standard_message(
        self,
        event_type: str,
        timestamp: str,
        fields_content: str,
        additional_content: str = None,
        event_message_kwargs: Dict[str, Any] = None,
    ) -> str:
        t = self.get_common_translations()
        header = self.get_category_header(event_type)
        icon = self.get_event_icon(event_type)
        event_message = self.get_event_message(event_type, **(event_message_kwargs or {}))

        if icon:
            msg = f"{icon} <b>{t['action']}:</b> {event_message}\n\n"
        else:
            msg = f"<b>{t['action']}:</b> {event_message}\n\n"

        msg += f"<b>{header}</b>\n\n"
        msg += fields_content

        if additional_content:
            msg += f"\n{additional_content}\n"

        msg += f"\n<b>{t['time']}:</b> {format_timestamp(timestamp)}"
        return msg
