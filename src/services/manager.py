import logging
from typing import Protocol, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Service(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...


class ServiceManager:
    def __init__(self):
        self._services: list[Service] = []

    def register(self, service: Service) -> None:
        self._services.append(service)

    def get(self, service_type: type[T]) -> T | None:
        for service in self._services:
            if isinstance(service, service_type):
                return service
        return None

    async def start_all(self) -> None:
        for service in self._services:
            try:
                await service.start()
            except Exception as e:
                logger.error(f"Failed to start {service.__class__.__name__}: {e}", exc_info=True)

    async def stop_all(self) -> None:
        for service in reversed(self._services):
            try:
                await service.stop()
            except Exception as e:
                logger.error(f"Failed to stop {service.__class__.__name__}: {e}", exc_info=True)
