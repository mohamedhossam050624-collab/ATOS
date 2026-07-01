from __future__ import annotations

from kernel.lifecycle import LifecycleManager
from kernel.registry import ServiceRegistry
from shared.logger import logger


class Kernel:
    """
    The central coordinator of the ATOS platform.

    Responsibilities:
    - Hold all registered services.
    - Manage service lifecycle.
    - Coordinate platform startup.
    - Coordinate platform shutdown.
    """

    def __init__(self) -> None:
        self.registry = ServiceRegistry()
        self.lifecycle = LifecycleManager()

        logger.info("Kernel initialized.")

    def register(self, service) -> None:
        """
        Register a new service.
        """
        self.registry.register(service)

    async def start(self) -> None:
        """
        Start all registered services.
        """
        logger.info("Starting ATOS Kernel...")

        for service in self.registry.all():
            await self.lifecycle.initialize(service)
            await self.lifecycle.start(service)

        logger.info("ATOS Kernel started successfully.")

    async def stop(self) -> None:
        """
        Stop all registered services.
        """
        logger.info("Stopping ATOS Kernel...")

        services = list(reversed(self.registry.all()))

        for service in services:
            await self.lifecycle.stop(service)

        logger.info("ATOS Kernel stopped.")