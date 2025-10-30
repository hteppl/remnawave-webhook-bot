import logging
from datetime import datetime
from typing import Dict

from src.utils.timestamped_storage import TimestampedStorage

logger = logging.getLogger(__name__)


class ConnectionLossTracker:
    """Track node connection losses over time."""

    def __init__(self, enabled: bool = False, window_hours: int = 24):
        """
        Initialize the connection loss tracker.

        Args:
            enabled: Whether tracking is enabled
            window_hours: Time window in hours for statistics
        """
        self.enabled = enabled
        self.window_hours = window_hours
        self.storage = TimestampedStorage()

        if self.enabled:
            logger.info(f"Connection loss tracker initialized: window={window_hours}h")
        else:
            logger.info("Connection loss tracker disabled")

    def record_connection_loss(self, node_name: str, timestamp: str = None) -> None:
        """
        Record a connection loss event.

        Args:
            node_name: Name of the node
            timestamp: Optional ISO timestamp string (defaults to now)
        """
        if not self.enabled:
            return

        # Parse timestamp if provided
        dt = None
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except Exception as e:
                logger.warning(f"Failed to parse timestamp '{timestamp}': {e}")

        self.storage.add(key=node_name, value=1, timestamp=dt)
        logger.info(f"Recorded connection loss for node: {node_name}")

    def get_statistics(self) -> Dict[str, int]:
        """
        Get connection loss statistics for all nodes within the time window.

        Returns:
            Dictionary mapping node names to loss counts
        """
        if not self.enabled:
            return {}

        stats = {}
        for node_name in self.storage.get_all_keys():
            count = self.storage.count_recent(node_name, self.window_hours)
            if count > 0:
                stats[node_name] = count

        logger.debug(f"Retrieved statistics for {len(stats)} nodes")
        return stats

    def get_node_loss_count(self, node_name: str) -> int:
        """
        Get connection loss count for a specific node.

        Args:
            node_name: Name of the node

        Returns:
            Number of losses within the time window
        """
        if not self.enabled:
            return 0

        return self.storage.count_recent(node_name, self.window_hours)

    def format_statistics_summary(self) -> str:
        """
        Format statistics as a summary string.

        Returns:
            Formatted string with node names and counts (e.g., "node1 x2\nnode2 x3")
        """
        if not self.enabled:
            return ""

        stats = self.get_statistics()
        if not stats:
            return ""

        # Sort by count (descending), then by name
        sorted_stats = sorted(stats.items(), key=lambda x: (-x[1], x[0]))

        lines = [f"{name} x{count}" for name, count in sorted_stats]
        return "\n".join(lines)

    def get_storage_stats(self) -> Dict[str, int]:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage statistics
        """
        return self.storage.get_stats()
