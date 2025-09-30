import logging

from aiogram import Bot
from aiohttp import web

from src.config import config
from src.webhook_handler import WebhookHandler

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def on_startup(app):
    """Application startup handler."""
    logger.info("Bot started successfully")
    logger.info(f"Listening on {config.WEBHOOK_HOST}:{config.WEBHOOK_PORT}{config.WEBHOOK_PATH}")
    logger.info(f"Language: {config.LANGUAGE}")


async def on_cleanup(app):
    """Application cleanup handler."""
    bot = app['bot']
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

    # Create web application
    app = web.Application()
    app["bot"] = bot
    app.router.add_post(config.WEBHOOK_PATH, webhook_handler.handle_webhook)
    app.router.add_get('/health', webhook_handler.health_check)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    # Run server
    web.run_app(app, host=config.WEBHOOK_HOST, port=config.WEBHOOK_PORT)


if __name__ == '__main__':
    main()
