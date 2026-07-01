from __future__ import annotations

import pytest

from kernel.exceptions import ServiceShutdownError, ServiceStartupError
from kernel.lifecycle import LifecycleManager
from kernel.state import ServiceState
from tests.fixtures.kernel_services import (
    FailingInitializeService,
    FailingStartService,
    FailingStopService,
    KernelTestService,
)


@pytest.mark.asyncio
async def test_initialize_service_successfully() -> None:
    """
    Ensure LifecycleManager initializes a service and updates its state.
    """
    manager = LifecycleManager()
    service = KernelTestService(name="lifecycle_test_service")

    await manager.initialize(service)

    assert service.initialized is True
    assert service.state == ServiceState.INITIALIZED


@pytest.mark.asyncio
async def test_initialize_is_idempotent_for_initialized_service() -> None:
    """
    Ensure initializing an already initialized service does not fail.
    """
    manager = LifecycleManager()
    service = KernelTestService(name="lifecycle_test_service")

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
    service = KernelTestService(name="lifecycle_test_service")

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
    service = KernelTestService(name="lifecycle_test_service")

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
    service = KernelTestService(name="lifecycle_test_service")

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
    service = KernelTestService(name="lifecycle_test_service")

    await manager.stop(service)

    assert service.stopped is False
    assert service.state == ServiceState.STOPPED


@pytest.mark.asyncio
async def test_stop_is_idempotent_for_stopped_service() -> None:
    """
    Ensure stopping an already stopped service does not fail.
    """
    manager = LifecycleManager()
    service = KernelTestService(name="lifecycle_test_service")

    await manager.stop(service)
    await manager.stop(service)

    assert service.state == ServiceState.STOPPED


@pytest.mark.asyncio
async def test_initialize_failure_sets_failed_state() -> None:
    """
    Ensure initialization failure is wrapped and service state becomes FAILED.
    """
    manager = LifecycleManager()
    service = FailingInitializeService(name="failing_initialize_service")

    with pytest.raises(ServiceStartupError):
        await manager.initialize(service)

    assert service.state == ServiceState.FAILED


@pytest.mark.asyncio
async def test_start_failure_sets_failed_state() -> None:
    """
    Ensure startup failure is wrapped and service state becomes FAILED.
    """
    manager = LifecycleManager()
    service = FailingStartService(name="failing_start_service")

    with pytest.raises(ServiceStartupError):
        await manager.start(service)

    assert service.state == ServiceState.FAILED


@pytest.mark.asyncio
async def test_stop_failure_sets_failed_state() -> None:
    """
    Ensure shutdown failure is wrapped and service state becomes FAILED.
    """
    manager = LifecycleManager()
    service = FailingStopService(name="failing_stop_service")

    await manager.start(service)

    with pytest.raises(ServiceShutdownError):
        await manager.stop(service)

    assert service.state == ServiceState.FAILED