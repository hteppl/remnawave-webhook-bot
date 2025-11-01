import logging

from aiogram import Bot
from aiohttp import web

from src.config import config
from src.services.status_reporter import StatusReporter
from src.version import __version__
from src.webhook_handler import WebhookHandler

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] [%(name)s] - %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(app):
    """Application startup handler."""
    logger.info(f"Remnawave Webhook Bot v{__version__}")
    logger.info("Project sources: https://t.me/morkowniy_bot")
    logger.info(f"Listening on {config.WEBHOOK_HOST}:{config.WEBHOOK_PORT}{config.WEBHOOK_PATH}")
    logger.info(f"Language: {config.LANGUAGE}")

    # Start status reporter if enabled
    status_reporter = app.get("status_reporter")
    if status_reporter:
        await status_reporter.start()

    logger.info("Bot started successfully!")


async def on_cleanup(app):
    """Application cleanup handler."""
    # Stop status reporter
    status_reporter = app.get("status_reporter")
    if status_reporter:
        await status_reporter.stop()

    bot = app["bot"]
    await bot.session.close()
    logger.info("Bot stopped")


def main():
    """Run the webhook server."""
    # Validate configuration
    config.validate()

    # Initialize bot
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

    # Initialize webhook handler
    webhook_handler = WebhookHandler(bot)

    # Initialize status reporter
    status_reporter = StatusReporter(bot, webhook_handler.connection_tracker)

    # Create web application
    app = web.Application()
    app["bot"] = bot
    app["status_reporter"] = status_reporter
    app.router.add_post(config.WEBHOOK_PATH, webhook_handler.handle_webhook)
    app.router.add_get("/health", webhook_handler.health_check)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    # Run server
    web.run_app(app, host=config.WEBHOOK_HOST, port=config.WEBHOOK_PORT)


if __name__ == "__main__":
    main()
