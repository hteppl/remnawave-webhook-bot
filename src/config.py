import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    TOPIC_USER = os.getenv("TOPIC_USER") or None
    TOPIC_NODE = os.getenv("TOPIC_NODE") or None
    TOPIC_CRM = os.getenv("TOPIC_CRM") or None
    TOPIC_SERVICE = os.getenv("TOPIC_SERVICE") or None
    TOPIC_STATUS = os.getenv("TOPIC_STATUS") or None

    @classmethod
    def get_topic_for_event(cls, event_type: str) -> int | None:
        prefix_map = {
            "user.": cls.TOPIC_USER,
            "node.": cls.TOPIC_NODE,
            "crm.": cls.TOPIC_CRM,
            "service.": cls.TOPIC_SERVICE,
        }
        for prefix, topic in prefix_map.items():
            if event_type.startswith(prefix):
                return int(topic) if topic else None
        return None

    WEBHOOK_SECRET_HEADER = os.getenv("WEBHOOK_SECRET_HEADER")
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8089))
    WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

    LANGUAGE = os.getenv("LANGUAGE", "en")
    LOCALES_DIR = os.getenv("LOCALES_DIR", "locales")
    TIMEZONE = os.getenv("TIMEZONE", "UTC")
    TIME_FORMAT = os.getenv("TIME_FORMAT", "%d.%m.%Y %H:%M:%S").strip('"\'')

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_DISABLED_EVENTS = os.getenv("LOG_DISABLED_EVENTS", "true").lower() in ("true", "yes", "on", "1")

    ENABLE_CONNECTION_LOSS_STATS = os.getenv("ENABLE_CONNECTION_LOSS_STATS", "false").lower() in (
        "true",
        "yes",
        "on",
        "1",
    )
    CONNECTION_LOSS_STATS_HOURS = int(os.getenv("CONNECTION_LOSS_STATS_HOURS", "24"))
    CONNECTION_LOSS_REPORT_INTERVAL_HOURS = int(os.getenv("CONNECTION_LOSS_REPORT_INTERVAL_HOURS", "24"))

    @classmethod
    def validate(cls):
        required = {
            "TELEGRAM_BOT_TOKEN": cls.TELEGRAM_BOT_TOKEN,
            "TELEGRAM_CHAT_ID": cls.TELEGRAM_CHAT_ID,
            "WEBHOOK_SECRET_HEADER": cls.WEBHOOK_SECRET_HEADER,
        }
        for name, value in required.items():
            if not value:
                raise ValueError(f"{name} is not set")


config = Config()
