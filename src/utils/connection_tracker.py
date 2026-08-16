import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime

from src.utils.timestamped_storage import TimestampedStorage

logger = logging.getLogger(__name__)


@dataclass
class NodeDowntime:
    timestamp: datetime
    provider: str
    country: str


class ConnectionLossTracker:
    def __init__(self, enabled: bool = False, window_hours: int = 24):
        self.enabled = enabled
        self.window_hours = window_hours
        self.storage = TimestampedStorage()
        self.down_times: dict[str, datetime] = {}
        logger.info(
            f"Connection loss tracker: {'enabled' if enabled else 'disabled'}"
            + (f" (window={window_hours}h)" if enabled else "")
        )

    def record_connection_loss(
        self, node_name: str, timestamp: str | None = None, provider: str | None = None, country_code: str | None = None
    ) -> None:
        if not self.enabled:
            return

        dt = None
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
            except Exception as e:
                logger.warning(f"Failed to parse timestamp '{timestamp}': {e}")

        if dt is None:
            dt = datetime.now(UTC)

        node_downtime = NodeDowntime(
            timestamp=dt,
            provider=provider or "Unknown",
            country=country_code or "Unknown",
        )
        self.storage.add(key=node_name, value=node_downtime, timestamp=dt)
        self.down_times[node_name] = dt

        logger.info(f"Recorded connection loss for node: {node_name}")

    def get_statistics(self) -> dict[str, int]:
        if not self.enabled:
            return {}

        stats = {}
        for node_name in self.storage.get_all_keys():
            if count := self.storage.count_recent(node_name, self.window_hours):
                stats[node_name] = count

        logger.debug(f"Retrieved statistics for {len(stats)} nodes")
        return stats

    def get_node_loss_count(self, node_name: str) -> int:
        return self.storage.count_recent(node_name, self.window_hours) if self.enabled else 0

    def get_statistics_lines(self) -> list[str]:
        if not self.enabled:
            return []

        stats = self.get_statistics()
        if not stats:
            return []

        sorted_stats = sorted(stats.items(), key=lambda x: (-x[1], x[0]))
        return [f"<code>{name}</code> - x{count}" for name, count in sorted_stats]

    def get_storage_stats(self) -> dict[str, int]:
        return self.storage.get_stats()

    def get_provider_statistics(self) -> dict[str, int]:
        if not self.enabled:
            return {}

        provider_counts = defaultdict(int)
        for node_name in self.storage.get_all_keys():
            recent_entries = self.storage.get_recent(node_name, self.window_hours)
            for _timestamp, node_downtime in recent_entries:
                if isinstance(node_downtime, NodeDowntime):
                    provider_counts[node_downtime.provider] += 1

        return dict(provider_counts)

    def get_country_statistics(self) -> dict[str, int]:
        if not self.enabled:
            return {}

        country_counts = defaultdict(int)
        for node_name in self.storage.get_all_keys():
            recent_entries = self.storage.get_recent(node_name, self.window_hours)
            for _timestamp, node_downtime in recent_entries:
                if isinstance(node_downtime, NodeDowntime):
                    country_counts[node_downtime.country] += 1

        return dict(country_counts)

    def get_downtime(self, node_name: str, restore_timestamp: str | None = None) -> str | None:
        if not self.enabled or node_name not in self.down_times:
            return None

        down_time = self.down_times[node_name]

        restore_time = None
        if restore_timestamp:
            try:
                restore_time = datetime.fromisoformat(restore_timestamp)
            except Exception as e:
                logger.warning(f"Failed to parse restore timestamp '{restore_timestamp}': {e}")

        if restore_time is None:
            restore_time = datetime.now(UTC)

        duration = restore_time - down_time
        total_seconds = int(duration.total_seconds())

        del self.down_times[node_name]

        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            return f"{days}d {hours}h"
