import asyncio
import logging

from aiogram import Bot

from src.config import config
from src.i18n import get_translation as _
from src.utils.connection_tracker import ConnectionLossTracker
from src.utils.timezone_helper import get_current_timestamp

logger = logging.getLogger(__name__)


class StatusReporter:
    def __init__(self, bot: Bot, connection_tracker: ConnectionLossTracker):
        self.bot = bot
        self.connection_tracker = connection_tracker
        self.task = None

    async def start(self):
        if not config.ENABLE_CONNECTION_LOSS_STATS or not config.TOPIC_STATUS:
            logger.info("Status reports disabled")
            return

        logger.info(f"Starting status reporter ({config.CONNECTION_LOSS_REPORT_INTERVAL_HOURS}h interval)")
        self.task = asyncio.create_task(self._periodic_report())

    async def stop(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                logger.info("Status reporter stopped")

    async def _periodic_report(self):
        interval = config.CONNECTION_LOSS_REPORT_INTERVAL_HOURS * 3600
        while True:
            try:
                await asyncio.sleep(interval)
                await self._send_status_report()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in status report: {e}", exc_info=True)

    async def _send_status_report(self):
        stats_lines = self.connection_tracker.get_statistics_lines()
        if not stats_lines:
            logger.debug("No statistics to report")
            return

        provider_stats = self.connection_tracker.get_provider_statistics()
        country_stats = self.connection_tracker.get_country_statistics()
        stats_formatted = "\n".join([line for line in stats_lines])

        message_parts = [
            f"{_('connection-stats-icon')} <b>{_('connection-stats-title', hours=config.CONNECTION_LOSS_STATS_HOURS)}</b>",
            stats_formatted,
        ]

        if provider_stats:
            provider_lines = [
                f"<code>{provider}</code> - x{count}" for provider, count in sorted(provider_stats.items(), key=lambda x: (-x[1], x[0]))
            ]
            message_parts.append(f"\n{_('provider-stats-icon')} <b>{_('provider-stats-title')}:</b>")
            message_parts.append("\n".join(provider_lines))

        if country_stats:
            country_lines = [
                f"<code>{country}</code> - x{count}" for country, count in sorted(country_stats.items(), key=lambda x: (-x[1], x[0]))
            ]
            message_parts.append(f"\n{_('country-stats-icon')} <b>{_('country-stats-title')}:</b>")
            message_parts.append("\n".join(country_lines))

        message_parts.append(f"\n{_('message-header-time-icon')} <b>{_('message-header-time-label')}:</b> {get_current_timestamp()}")
        message = "\n".join(message_parts)

        try:
            await self.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode="HTML",
                message_thread_id=int(config.TOPIC_STATUS),
            )
            logger.info("Status report sent")
        except Exception as e:
            logger.error(f"Failed to send status report: {e}", exc_info=True)
