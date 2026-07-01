from __future__ import annotations

import pytest

from kernel.exceptions import InvalidServiceStateError
from kernel.state import ServiceState
from tests.fixtures.kernel_services import KernelTestService


def test_service_requires_non_empty_name() -> None:
    """
    Ensure services cannot be created without a valid name.
    """
    with pytest.raises(ValueError, match="Service name must not be empty"):
        KernelTestService(name="")


def test_service_metadata_is_initialized() -> None:
    """
    Ensure service metadata is created correctly.
    """
    service = KernelTestService(
        name="market_data",
        description="Collects market data.",
        version="2.1.0",
    )

    assert service.name == "market_data"
    assert service.description == "Collects market data."
    assert service.version == "2.1.0"
    assert service.service_id
    assert service.metadata.name == "market_data"
    assert service.metadata.description == "Collects market data."
    assert service.metadata.version == "2.1.0"


def test_service_initial_state_is_created() -> None:
    """
    Ensure newly created services start in CREATED state.
    """
    service = KernelTestService()

    assert service.state == ServiceState.CREATED


def test_service_state_can_be_updated() -> None:
    """
    Ensure a service state can be updated using a valid ServiceState.
    """
    service = KernelTestService()

    service.set_state(ServiceState.INITIALIZED)

    assert service.state == ServiceState.INITIALIZED


def test_service_rejects_invalid_state() -> None:
    """
    Ensure invalid state values are rejected.
    """
    service = KernelTestService()

    with pytest.raises(InvalidServiceStateError):
        service.set_state("running")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_service_lifecycle_methods_can_be_called() -> None:
    """
    Ensure concrete service lifecycle methods can be called.
    """
    service = KernelTestService()

    await service.initialize()
    await service.start()
    await service.stop()

    assert service.initialized is True
    assert service.started is False
    assert service.stopped is True


@pytest.mark.asyncio
async def test_default_health_check_output() -> None:
    """
    Ensure health_check returns stable service health data.
    """
    service = KernelTestService()

    health = await service.health_check()

    assert health["service_id"] == service.service_id
    assert health["name"] == "test_service"
    assert health["version"] == "1.0.0"
    assert health["state"] == ServiceState.CREATED.value
    assert health["healthy"] is True
    assert health["initialized"] is False
    assert health["started"] is False
    assert health["stopped"] is False


@pytest.mark.asyncio
async def test_failed_service_health_is_unhealthy() -> None:
    """
    Ensure failed services are reported as unhealthy.
    """
    service = KernelTestService()
    service.set_state(ServiceState.FAILED)

    health = await service.health_check()

    assert health["state"] == ServiceState.FAILED.value
    assert health["healthy"] is False