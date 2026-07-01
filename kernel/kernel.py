from __future__ import annotations

from typing import Any

from kernel.exceptions import KernelShutdownError, KernelStartupError
from kernel.lifecycle import LifecycleManager
from kernel.registry import ServiceRegistry
from kernel.service import Service
from kernel.state import ServiceState
from shared.logger import logger


class Kernel:
    """
    Central operating core of ATOS.

    The Kernel is responsible for platform lifecycle management:
    - Service registration
    - Service startup
    - Service shutdown
    - Health checks
    - Runtime state visibility

    The Kernel must never contain trading, analysis, reasoning, risk,
    portfolio, or execution business logic.
    """

    def __init__(self) -> None:
        self._registry = ServiceRegistry()
        self._lifecycle = LifecycleManager()
        self._is_running = False
        self._is_shutting_down = False

    @property
    def is_running(self) -> bool:
        """
        Return True if the Kernel is currently running.
        """
        return self._is_running

    @property
    def is_shutting_down(self) -> bool:
        """
        Return True if the Kernel is currently shutting down.
        """
        return self._is_shutting_down

    def register_service(self, service: Service) -> None:
        """
        Register a service with the Kernel.

        Services should be registered before Kernel startup.
        Runtime plugin loading will be handled later by the Plugin Manager,
        not by direct Kernel mutation.
        """
        if self._is_running:
            raise KernelStartupError(
                "Cannot register services after the Kernel has started."
            )

        self._registry.register(service)
        logger.info(f"Registered service: {service.name}")

    def unregister_service(self, service_name: str) -> Service:
        """
        Unregister a service from the Kernel.

        This is only allowed before startup or after shutdown.
        """
        if self._is_running:
            raise KernelShutdownError(
                "Cannot unregister services while the Kernel is running."
            )

        service = self._registry.unregister(service_name)
        logger.info(f"Unregistered service: {service.name}")
        return service

    def get_service(self, service_name: str) -> Service:
        """
        Return a registered service by name.
        """
        return self._registry.get(service_name)

    def list_services(self) -> list[Service]:
        """
        Return all registered services.
        """
        return self._registry.list_services()

    def service_names(self) -> tuple[str, ...]:
        """
        Return all registered service names.
        """
        return self._registry.service_names()

    def service_count(self) -> int:
        """
        Return the number of registered services.
        """
        return self._registry.count()

    async def start(self) -> None:
        """
        Start all registered services.

        Services are started in registration order.

        If any service fails to start, the Kernel attempts a safe rollback by
        stopping already-started services in reverse order.
        """
        if self._is_running:
            logger.warning("Kernel start requested while already running.")
            return

        logger.info("Starting ATOS Kernel.")

        started_services: list[Service] = []

        try:
            for service in self._registry.list_services():
                await self._lifecycle.start(service)
                started_services.append(service)

            self._is_running = True
            logger.info("ATOS Kernel started successfully.")

        except Exception as exc:
            logger.exception("ATOS Kernel startup failed. Rolling back services.")

            for service in reversed(started_services):
                try:
                    await self._lifecycle.stop(service)
                except Exception:
                    logger.exception(
                        f"Rollback failed while stopping service: {service.name}"
                    )

            self._is_running = False

            raise KernelStartupError("ATOS Kernel failed to start.") from exc

    async def shutdown(self) -> None:
        """
        Gracefully shut down all registered services.

        Services are stopped in reverse registration order.
        """
        if not self._is_running:
            logger.warning("Kernel shutdown requested while not running.")
            return

        logger.info("Shutting down ATOS Kernel.")
        self._is_shutting_down = True

        shutdown_errors: list[Exception] = []

        for service in reversed(self._registry.list_services()):
            try:
                await self._lifecycle.stop(service)
            except Exception as exc:
                shutdown_errors.append(exc)
                logger.exception(f"Failed to stop service during shutdown: {service.name}")

        self._is_running = False
        self._is_shutting_down = False

        if shutdown_errors:
            raise KernelShutdownError(
                f"ATOS Kernel shutdown completed with {len(shutdown_errors)} error(s)."
            )

        logger.info("ATOS Kernel shut down successfully.")

    async def health_check(self) -> dict[str, Any]:
        """
        Return Kernel and service health information.

        This method intentionally returns plain serializable data so it can be
        exposed later through APIs, dashboards, logs, or monitoring tools.
        """
        services_health: list[dict[str, Any]] = []

        for service in self._registry.list_services():
            try:
                services_health.append(await service.health_check())
            except Exception as exc:
                logger.exception(f"Health check failed for service: {service.name}")
                services_health.append(
                    {
                        "service_id": service.service_id,
                        "name": service.name,
                        "version": service.version,
                        "state": ServiceState.FAILED.value,
                        "healthy": False,
                        "error": str(exc),
                    }
                )

        return {
            "kernel_running": self._is_running,
            "kernel_shutting_down": self._is_shutting_down,
            "service_count": self._registry.count(),
            "services": services_health,
        }