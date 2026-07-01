from __future__ import annotations

from kernel.exceptions import ServiceShutdownError, ServiceStartupError
from kernel.service import Service
from kernel.state import ServiceState
from shared.logger import logger


class LifecycleManager:
    """
    Manages the lifecycle of a single ATOS service.

    Responsibilities:
    - Initialize services safely.
    - Start services safely.
    - Stop services gracefully.
    - Update service state.
    - Convert unexpected exceptions into Kernel-level errors.
    """

    async def initialize(self, service: Service) -> None:
        """
        Initialize a service before startup.

        If the service is already initialized or running, this method does nothing.
        """
        if service.state in {ServiceState.INITIALIZED, ServiceState.RUNNING}:
            logger.debug(f"Service '{service.name}' is already initialized.")
            return

        try:
            logger.info(f"Initializing service: {service.name}")
            await service.initialize()
            service.set_state(ServiceState.INITIALIZED)
            logger.info(f"Service initialized successfully: {service.name}")

        except Exception as exc:
            service.set_state(ServiceState.FAILED)
            logger.exception(f"Failed to initialize service: {service.name}")
            raise ServiceStartupError(
                f"Failed to initialize service '{service.name}'."
            ) from exc

    async def start(self, service: Service) -> None:
        """
        Start a service.

        If the service is still in CREATED state, it will be initialized first.
        """
        if service.state == ServiceState.RUNNING:
            logger.debug(f"Service '{service.name}' is already running.")
            return

        if service.state == ServiceState.CREATED:
            await self.initialize(service)

        try:
            logger.info(f"Starting service: {service.name}")
            service.set_state(ServiceState.STARTING)
            await service.start()
            service.set_state(ServiceState.RUNNING)
            logger.info(f"Service started successfully: {service.name}")

        except Exception as exc:
            service.set_state(ServiceState.FAILED)
            logger.exception(f"Failed to start service: {service.name}")
            raise ServiceStartupError(
                f"Failed to start service '{service.name}'."
            ) from exc

    async def stop(self, service: Service) -> None:
        """
        Stop a service gracefully.

        Services that were never started are marked as stopped safely.
        """
        if service.state == ServiceState.STOPPED:
            logger.debug(f"Service '{service.name}' is already stopped.")
            return

        if service.state == ServiceState.CREATED:
            service.set_state(ServiceState.STOPPED)
            logger.debug(f"Service '{service.name}' was never started. Marked as stopped.")
            return

        try:
            logger.info(f"Stopping service: {service.name}")
            service.set_state(ServiceState.STOPPING)
            await service.stop()
            service.set_state(ServiceState.STOPPED)
            logger.info(f"Service stopped successfully: {service.name}")

        except Exception as exc:
            service.set_state(ServiceState.FAILED)
            logger.exception(f"Failed to stop service: {service.name}")
            raise ServiceShutdownError(
                f"Failed to stop service '{service.name}'."
            ) from exc