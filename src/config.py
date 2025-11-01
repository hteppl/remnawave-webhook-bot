import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # Telegram Topics Configuration (Forum Topics)
    # Set to None or empty string to disable topic routing
    TOPIC_USER = os.getenv("TOPIC_USER") or None
    TOPIC_NODE = os.getenv("TOPIC_NODE") or None
    TOPIC_CRM = os.getenv("TOPIC_CRM") or None
    TOPIC_SERVICE = os.getenv("TOPIC_SERVICE") or None
    TOPIC_STATUS = os.getenv("TOPIC_STATUS") or None

    @classmethod
    def get_topic_for_event(cls, event_type: str) -> int | None:
        """
        Get message thread ID for event type.

        Args:
            event_type: Event type (e.g., user.created, node.disabled)

        Returns:
            Thread ID or None if no topic configured
        """
        if event_type.startswith("user."):
            return int(cls.TOPIC_USER) if cls.TOPIC_USER else None
        elif event_type.startswith("node."):
            return int(cls.TOPIC_NODE) if cls.TOPIC_NODE else None
        elif event_type.startswith("crm."):
            return int(cls.TOPIC_CRM) if cls.TOPIC_CRM else None
        elif event_type.startswith("service."):
            return int(cls.TOPIC_SERVICE) if cls.TOPIC_SERVICE else None
        return None

    # Webhook Configuration
    WEBHOOK_SECRET_HEADER = os.getenv("WEBHOOK_SECRET_HEADER")
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8089))
    WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

    # Internationalization
    LANGUAGE = os.getenv("LANGUAGE", "en")
    LOCALES_DIR = os.getenv("LOCALES_DIR", "locales")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    # Connection Loss Tracking
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
        """Validate required configuration."""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set")
        if not cls.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_CHAT_ID is not set")
        if not cls.WEBHOOK_SECRET_HEADER:
            raise ValueError("WEBHOOK_SECRET_HEADER is not set")


config = Config()
