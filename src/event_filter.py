import logging
import os

logger = logging.getLogger(__name__)


class EventFilter:
    USER_EVENTS = [
        "user.created",
        "user.modified",
        "user.deleted",
        "user.revoked",
        "user.disabled",
        "user.enabled",
        "user.limited",
        "user.expired",
        "user.traffic_reset",
        "user.expires_in_72_hours",
        "user.expires_in_48_hours",
        "user.expires_in_24_hours",
        "user.expired_24_hours_ago",
        "user.first_connected",
        "user.bandwidth_usage_threshold_reached",
    ]

    NODE_EVENTS = [
        "node.created",
        "node.modified",
        "node.disabled",
        "node.enabled",
        "node.deleted",
        "node.connection_lost",
        "node.connection_restored",
        "node.traffic_notify",
    ]

    BILLING_EVENTS = [
        "crm.infra_billing_node_payment_in_7_days",
        "crm.infra_billing_node_payment_in_48hrs",
        "crm.infra_billing_node_payment_in_24hrs",
        "crm.infra_billing_node_payment_due_today",
        "crm.infra_billing_node_payment_overdue_24hrs",
        "crm.infra_billing_node_payment_overdue_48hrs",
        "crm.infra_billing_node_payment_overdue_7_days",
    ]

    SERVICE_EVENTS = [
        "service.panel_started",
        "service.login_attempt_failed",
        "service.login_attempt_success",
    ]

    ALL_EVENTS = USER_EVENTS + NODE_EVENTS + BILLING_EVENTS + SERVICE_EVENTS

    def __init__(self):
        self.enabled_events = self._load_enabled_events()
        logger.info(f"Event filter initialized ({len(self.enabled_events)} events enabled)")

    def _load_enabled_events(self) -> set:
        enabled = set()
        for event in self.ALL_EVENTS:
            env_var = f"NOTIFY_{event.upper().replace('.', '_')}"
            if os.getenv(env_var, "true").lower() in ("true", "yes", "on", "1"):
                enabled.add(event)
        return enabled

    def is_enabled(self, event_type: str) -> bool:
        return event_type in self.enabled_events

    def get_disabled_events(self) -> list:
        return [event for event in self.ALL_EVENTS if event not in self.enabled_events]

    def get_enabled_events(self) -> list:
        return list(self.enabled_events)


event_filter = EventFilter()
