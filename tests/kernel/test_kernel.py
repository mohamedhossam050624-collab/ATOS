from __future__ import annotations

from typing import Any

import pytest

from kernel import Kernel
from kernel.exceptions import KernelShutdownError, KernelStartupError
from kernel.service import Service
from kernel.state import ServiceState


class KernelManagedService(Service):
    """
    Concrete service implementation used only for testing Kernel behavior.
    """

    def __init__(self, name: str = "kernel_managed_service") -> None:
        super().__init__(
            name=name,
            description="Kernel managed test service.",
            version="1.0.0",
        )
        self.initialized = False
        self.started = False
        self.stopped = False

    async def initialize(self) -> None:
        self.initialized = True

    async def start(self) -> None:
        self.started = True
        self.stopped = False

    async def stop(self) -> None:
        self.started = False
        self.stopped = True

    async def health_check(self) -> dict[str, Any]:
        health = await super().health_check()
        health.update(
            {
                "initialized": self.initialized,
                "started": self.started,
                "stopped": self.stopped,
            }
        )
        return health


class FailingStartKernelService(KernelManagedService):
    """
    Service that fails during startup.
    """

    async def start(self) -> None:
        raise RuntimeError("Kernel startup test failure.")


class FailingStopKernelService(KernelManagedService):
    """
    Service that fails during shutdown.
    """

    async def stop(self) -> None:
        raise RuntimeError("Kernel shutdown test failure.")


def test_kernel_starts_empty() -> None:
    """
    Ensure a new Kernel starts with no registered services.
    """
    kernel = Kernel()

    assert kernel.is_running is False
    assert kernel.is_shutting_down is False
    assert kernel.service_count() == 0
    assert kernel.list_services() == []
    assert kernel.service_names() == ()


def test_kernel_registers_service() -> None:
    """
    Ensure the Kernel can register and expose a service.
    """
    kernel = Kernel()
    service = KernelManagedService(name="config_manager")

    kernel.register_service(service)

    assert kernel.service_count() == 1
    assert kernel.get_service("config_manager") is service
    assert kernel.list_services() == [service]
    assert kernel.service_names() == ("config_manager",)


def test_kernel_unregisters_service_before_startup() -> None:
    """
    Ensure services can be unregistered before Kernel startup.
    """
    kernel = Kernel()
    service = KernelManagedService(name="event_bus")

    kernel.register_service(service)
    removed_service = kernel.unregister_service("event_bus")

    assert removed_service is service
    assert kernel.service_count() == 0


@pytest.mark.asyncio
async def test_kernel_starts_registered_services() -> None:
    """
    Ensure Kernel startup initializes and starts registered services.
    """
    kernel = Kernel()
    service = KernelManagedService(name="health_manager")

    kernel.register_service(service)

    await kernel.start()

    assert kernel.is_running is True
    assert service.initialized is True
    assert service.started is True
    assert service.state == ServiceState.RUNNING

    await kernel.shutdown()


@pytest.mark.asyncio
async def test_kernel_shutdown_stops_registered_services() -> None:
    """
    Ensure Kernel shutdown stops registered services.
    """
    kernel = Kernel()
    service = KernelManagedService(name="scheduler")

    kernel.register_service(service)

    await kernel.start()
    await kernel.shutdown()

    assert kernel.is_running is False
    assert kernel.is_shutting_down is False
    assert service.started is False
    assert service.stopped is True
    assert service.state == ServiceState.STOPPED


@pytest.mark.asyncio
async def test_kernel_start_is_idempotent() -> None:
    """
    Ensure starting an already running Kernel does not fail.
    """
    kernel = Kernel()
    service = KernelManagedService(name="event_bus")

    kernel.register_service(service)

    await kernel.start()
    await kernel.start()

    assert kernel.is_running is True
    assert service.state == ServiceState.RUNNING

    await kernel.shutdown()


@pytest.mark.asyncio
async def test_kernel_shutdown_when_not_running_is_safe() -> None:
    """
    Ensure shutting down a non-running Kernel does not fail.
    """
    kernel = Kernel()

    await kernel.shutdown()

    assert kernel.is_running is False
    assert kernel.is_shutting_down is False


@pytest.mark.asyncio
async def test_kernel_rejects_service_registration_after_startup() -> None:
    """
    Ensure services cannot be directly registered after Kernel startup.
    """
    kernel = Kernel()
    first_service = KernelManagedService(name="config_manager")
    second_service = KernelManagedService(name="event_bus")

    kernel.register_service(first_service)
    await kernel.start()

    with pytest.raises(KernelStartupError):
        kernel.register_service(second_service)

    await kernel.shutdown()


@pytest.mark.asyncio
async def test_kernel_rejects_service_unregistration_while_running() -> None:
    """
    Ensure services cannot be unregistered while Kernel is running.
    """
    kernel = Kernel()
    service = KernelManagedService(name="config_manager")

    kernel.register_service(service)
    await kernel.start()

    with pytest.raises(KernelShutdownError):
        kernel.unregister_service("config_manager")

    await kernel.shutdown()


@pytest.mark.asyncio
async def test_kernel_health_check_reports_services() -> None:
    """
    Ensure Kernel health check returns Kernel and service health data.
    """
    kernel = Kernel()
    service = KernelManagedService(name="monitoring")

    kernel.register_service(service)

    await kernel.start()
    health = await kernel.health_check()

    assert health["kernel_running"] is True
    assert health["kernel_shutting_down"] is False
    assert health["service_count"] == 1
    assert len(health["services"]) == 1

    service_health = health["services"][0]

    assert service_health["name"] == "monitoring"
    assert service_health["state"] == ServiceState.RUNNING.value
    assert service_health["healthy"] is True
    assert service_health["initialized"] is True
    assert service_health["started"] is True

    await kernel.shutdown()


@pytest.mark.asyncio
async def test_kernel_rolls_back_started_services_when_startup_fails() -> None:
    """
    Ensure Kernel startup failure rolls back already-started services.
    """
    kernel = Kernel()
    healthy_service = KernelManagedService(name="healthy_service")
    failing_service = FailingStartKernelService(name="failing_service")

    kernel.register_service(healthy_service)
    kernel.register_service(failing_service)

    with pytest.raises(KernelStartupError):
        await kernel.start()

    assert kernel.is_running is False
    assert healthy_service.stopped is True
    assert healthy_service.state == ServiceState.STOPPED
    assert failing_service.state == ServiceState.FAILED


@pytest.mark.asyncio
async def test_kernel_shutdown_reports_failure() -> None:
    """
    Ensure Kernel shutdown raises KernelShutdownError if a service fails to stop.
    """
    kernel = Kernel()
    service = FailingStopKernelService(name="failing_stop_service")

    kernel.register_service(service)

    await kernel.start()

    with pytest.raises(KernelShutdownError):
        await kernel.shutdown()

    assert kernel.is_running is False
    assert kernel.is_shutting_down is False
    assert service.state == ServiceState.FAILED