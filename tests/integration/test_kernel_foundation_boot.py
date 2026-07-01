from __future__ import annotations

import pytest

from config.manager import ConfigurationManager
from events.bus import EventBus
from kernel import Kernel
from kernel.state import ServiceState
from services.dummy_service import DummyService


@pytest.mark.asyncio
async def test_kernel_boots_foundation_services() -> None:
    """
    Ensure the Kernel can boot the current foundation services together.

    This integration test validates the current foundation boot path:
    - ConfigurationManager loads settings.
    - EventBus starts successfully.
    - DummyService starts successfully.
    - Kernel health check reports all foundation services.
    - Kernel shutdown stops all services gracefully.
    """
    kernel = Kernel()

    configuration_manager = ConfigurationManager(
        environ={
            "ATOS_ENV": "testing",
            "ATOS_DEBUG": "true",
            "ATOS_LOG_LEVEL": "info",
        }
    )
    event_bus = EventBus()
    dummy_service = DummyService()

    kernel.register_service(configuration_manager)
    kernel.register_service(event_bus)
    kernel.register_service(dummy_service)

    try:
        await kernel.start()

        assert kernel.is_running is True
        assert kernel.service_count() == 3

        health = await kernel.health_check()

        assert health["kernel_running"] is True
        assert health["kernel_shutting_down"] is False
        assert health["service_count"] == 3

        services = {
            service_health["name"]: service_health
            for service_health in health["services"]
        }

        assert "configuration_manager" in services
        assert "event_bus" in services
        assert "dummy_service" in services

        configuration_health = services["configuration_manager"]

        assert configuration_health["state"] == ServiceState.RUNNING.value
        assert configuration_health["healthy"] is True
        assert configuration_health["settings_loaded"] is True
        assert configuration_health["environment"] == "testing"
        assert configuration_health["debug"] is True
        assert configuration_health["log_level"] == "INFO"

        event_bus_health = services["event_bus"]

        assert event_bus_health["state"] == ServiceState.RUNNING.value
        assert event_bus_health["healthy"] is True
        assert event_bus_health["started"] is True
        assert event_bus_health["event_types"] == []
        assert event_bus_health["subscription_count"] == 0
        assert event_bus_health["published_events_count"] == 0
        assert event_bus_health["handler_errors_count"] == 0

        dummy_health = services["dummy_service"]

        assert dummy_health["state"] == ServiceState.RUNNING.value
        assert dummy_health["healthy"] is True
        assert dummy_health["initialized"] is True
        assert dummy_health["started"] is True
        assert dummy_health["stopped"] is False

    finally:
        if kernel.is_running:
            await kernel.shutdown()

    assert kernel.is_running is False
    assert configuration_manager.state == ServiceState.STOPPED
    assert event_bus.state == ServiceState.STOPPED
    assert dummy_service.state == ServiceState.STOPPED