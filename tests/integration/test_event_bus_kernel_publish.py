from __future__ import annotations

import pytest

from config.manager import ConfigurationManager
from events.base import DomainEvent
from events.bus import EventBus
from kernel import Kernel
from kernel.state import ServiceState
from services.dummy_service import DummyService


@pytest.mark.asyncio
async def test_event_bus_publishes_event_after_kernel_boot() -> None:
    """
    Ensure EventBus can publish events after being started by the Kernel.

    This integration test validates:
    - Kernel starts foundation services.
    - EventBus is started through Kernel lifecycle management.
    - A subscribed async handler receives a DomainEvent.
    - EventBus metrics update correctly.
    - Kernel shutdown remains graceful.
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

    received_events: list[DomainEvent] = []

    async def collect_event(event: DomainEvent) -> None:
        received_events.append(event)

    event_bus.subscribe("kernel.test.event", collect_event)

    kernel.register_service(configuration_manager)
    kernel.register_service(event_bus)
    kernel.register_service(dummy_service)

    event = DomainEvent(
        event_type="kernel.test.event",
        source="integration_test",
        payload={
            "message": "event bus is operational",
        },
        metadata={
            "test": "kernel_event_bus_publish",
        },
    )

    try:
        await kernel.start()

        assert kernel.is_running is True
        assert event_bus.state == ServiceState.RUNNING

        await event_bus.publish(event)

        assert received_events == [event]
        assert event_bus.published_events_count == 1
        assert event_bus.handler_errors_count == 0

        health = await kernel.health_check()

        services = {
            service_health["name"]: service_health
            for service_health in health["services"]
        }

        event_bus_health = services["event_bus"]

        assert event_bus_health["state"] == ServiceState.RUNNING.value
        assert event_bus_health["started"] is True
        assert event_bus_health["subscription_count"] == 1
        assert event_bus_health["published_events_count"] == 1
        assert event_bus_health["handler_errors_count"] == 0
        assert event_bus_health["event_types"] == ["kernel.test.event"]

    finally:
        if kernel.is_running:
            await kernel.shutdown()

    assert kernel.is_running is False
    assert configuration_manager.state == ServiceState.STOPPED
    assert event_bus.state == ServiceState.STOPPED
    assert dummy_service.state == ServiceState.STOPPED
    