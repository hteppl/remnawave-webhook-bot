import logging
from datetime import datetime
from typing import Dict, List

from src.utils.timestamped_storage import TimestampedStorage

logger = logging.getLogger(__name__)


class ConnectionLossTracker:
    def __init__(self, enabled: bool = False, window_hours: int = 24):
        self.enabled = enabled
        self.window_hours = window_hours
        self.storage = TimestampedStorage()
        logger.info(f"Connection loss tracker: {'enabled' if enabled else 'disabled'}" + (f" (window={window_hours}h)" if enabled else ""))

    def record_connection_loss(self, node_name: str, timestamp: str = None) -> None:
        if not self.enabled:
            return

        dt = None
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except Exception as e:
                logger.warning(f"Failed to parse timestamp '{timestamp}': {e}")

        self.storage.add(key=node_name, value=1, timestamp=dt)
        logger.info(f"Recorded connection loss for node: {node_name}")

    def get_statistics(self) -> Dict[str, int]:
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

    def get_statistics_lines(self) -> List[str]:
        if not self.enabled:
            return []

        stats = self.get_statistics()
        if not stats:
            return []

        sorted_stats = sorted(stats.items(), key=lambda x: (-x[1], x[0]))
        return [f"<code>{name}</code> - x{count}" for name, count in sorted_stats]

    def get_storage_stats(self) -> Dict[str, int]:
        return self.storage.get_stats()
