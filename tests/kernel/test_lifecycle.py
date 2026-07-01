from __future__ import annotations

from typing import Any

import pytest

from kernel.exceptions import ServiceShutdownError, ServiceStartupError
from kernel.lifecycle import LifecycleManager
from kernel.service import Service
from kernel.state import ServiceState


class LifecycleTestService(Service):
    """
    Concrete service implementation used only for testing LifecycleManager.
    """

    def __init__(self, name: str = "lifecycle_test_service") -> None:
        super().__init__(
            name=name,
            description="Lifecycle test service.",
            version="1.0.0",
        )
        self.initialized = False
        self.started = False
        self.stopped = False

    async def initialize(self) -> None:
        self.initialized = True

    async def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.stopped = True
        self.started = False

    async def health_check(self) -> dict[str, Any]:
        return await super().health_check()


class FailingInitializeService(LifecycleTestService):
    """
    Service that fails during initialization.
    """

    async def initialize(self) -> None:
        raise RuntimeError("Initialization failed.")


class FailingStartService(LifecycleTestService):
    """
    Service that fails during startup.
    """

    async def start(self) -> None:
        raise RuntimeError("Startup failed.")


class FailingStopService(LifecycleTestService):
    """
    Service that fails during shutdown.
    """

    async def stop(self) -> None:
        raise RuntimeError("Shutdown failed.")


@pytest.mark.asyncio
async def test_initialize_service_successfully() -> None:
    """
    Ensure LifecycleManager initializes a service and updates its state.
    """
    manager = LifecycleManager()
    service = LifecycleTestService()

    await manager.initialize(service)

    assert service.initialized is True
    assert service.state == ServiceState.INITIALIZED


@pytest.mark.asyncio
async def test_initialize_is_idempotent_for_initialized_service() -> None:
    """
    Ensure initializing an already initialized service does not fail.
    """
    manager = LifecycleManager()
    service = LifecycleTestService()

    await manager.initialize(service)
    await manager.initialize(service)

    assert service.initialized is True
    assert service.state == ServiceState.INITIALIZED


@pytest.mark.asyncio
async def test_start_service_from_created_state() -> None:
    """
    Ensure starting a CREATED service initializes it first, then starts it.
    """
    manager = LifecycleManager()
    service = LifecycleTestService()

    await manager.start(service)

    assert service.initialized is True
    assert service.started is True
    assert service.state == ServiceState.RUNNING


@pytest.mark.asyncio
async def test_start_is_idempotent_for_running_service() -> None:
    """
    Ensure starting an already running service does not fail.
    """
    manager = LifecycleManager()
    service = LifecycleTestService()

    await manager.start(service)
    await manager.start(service)

    assert service.started is True
    assert service.state == ServiceState.RUNNING


@pytest.mark.asyncio
async def test_stop_running_service_successfully() -> None:
    """
    Ensure stopping a running service calls stop and updates state.
    """
    manager = LifecycleManager()
    service = LifecycleTestService()

    await manager.start(service)
    await manager.stop(service)

    assert service.stopped is True
    assert service.started is False
    assert service.state == ServiceState.STOPPED


@pytest.mark.asyncio
async def test_stop_created_service_marks_it_as_stopped() -> None:
    """
    Ensure stopping a never-started service safely marks it as stopped.
    """
    manager = LifecycleManager()
    service = LifecycleTestService()

    await manager.stop(service)

    assert service.stopped is False
    assert service.state == ServiceState.STOPPED


@pytest.mark.asyncio
async def test_stop_is_idempotent_for_stopped_service() -> None:
    """
    Ensure stopping an already stopped service does not fail.
    """
    manager = LifecycleManager()
    service = LifecycleTestService()

    await manager.stop(service)
    await manager.stop(service)

    assert service.state == ServiceState.STOPPED


@pytest.mark.asyncio
async def test_initialize_failure_sets_failed_state() -> None:
    """
    Ensure initialization failure is wrapped and service state becomes FAILED.
    """
    manager = LifecycleManager()
    service = FailingInitializeService()

    with pytest.raises(ServiceStartupError):
        await manager.initialize(service)

    assert service.state == ServiceState.FAILED


@pytest.mark.asyncio
async def test_start_failure_sets_failed_state() -> None:
    """
    Ensure startup failure is wrapped and service state becomes FAILED.
    """
    manager = LifecycleManager()
    service = FailingStartService()

    with pytest.raises(ServiceStartupError):
        await manager.start(service)

    assert service.state == ServiceState.FAILED


@pytest.mark.asyncio
async def test_stop_failure_sets_failed_state() -> None:
    """
    Ensure shutdown failure is wrapped and service state becomes FAILED.
    """
    manager = LifecycleManager()
    service = FailingStopService()

    await manager.start(service)

    with pytest.raises(ServiceShutdownError):
        await manager.stop(service)

    assert service.state == ServiceState.FAILED