from __future__ import annotations

import pytest

from events.base import DomainEvent
from events.bus import EventBus
from events.exceptions import (
    EventHandlerNotFoundError,
    EventPublishError,
    EventSubscriptionError,
    InvalidEventError,
    InvalidEventHandlerError,
)
from kernel.lifecycle import LifecycleManager
from kernel.state import ServiceState


async def working_handler(event: DomainEvent) -> None:
    """
    Valid event handler used in EventBus tests.
    """


async def failing_handler(event: DomainEvent) -> None:
    """
    Event handler that always fails.
    """
    raise RuntimeError("Handler failed.")


def sync_handler(event: DomainEvent) -> None:
    """
    Invalid synchronous handler.
    """


def test_event_bus_starts_empty() -> None:
    """
    Ensure EventBus starts with no subscriptions or published events.
    """
    bus = EventBus()

    assert bus.name == "event_bus"
    assert bus.subscription_count == 0
    assert bus.published_events_count == 0
    assert bus.handler_errors_count == 0
    assert bus.event_types() == ()


def test_subscribe_registers_handler() -> None:
    """
    Ensure a valid handler can be subscribed.
    """
    bus = EventBus()

    bus.subscribe("test.event", working_handler)

    assert bus.subscription_count == 1
    assert bus.event_types() == ("test.event",)
    assert bus.subscribers_for("test.event") == (working_handler,)


def test_subscribe_ignores_duplicate_handler() -> None:
    """
    Ensure subscribing the same handler twice does not duplicate it.
    """
    bus = EventBus()

    bus.subscribe("test.event", working_handler)
    bus.subscribe("test.event", working_handler)

    assert bus.subscription_count == 1
    assert bus.subscribers_for("test.event") == (working_handler,)


def test_subscribe_rejects_empty_event_type() -> None:
    """
    Ensure empty event types are rejected.
    """
    bus = EventBus()

    with pytest.raises(EventSubscriptionError):
        bus.subscribe("", working_handler)


def test_subscribe_rejects_invalid_handler() -> None:
    """
    Ensure synchronous handlers are rejected.
    """
    bus = EventBus()

    with pytest.raises(InvalidEventHandlerError):
        bus.subscribe("test.event", sync_handler)


def test_unsubscribe_removes_handler() -> None:
    """
    Ensure a subscribed handler can be removed.
    """
    bus = EventBus()

    bus.subscribe("test.event", working_handler)
    bus.unsubscribe("test.event", working_handler)

    assert bus.subscription_count == 0
    assert bus.event_types() == ()


def test_unsubscribe_missing_handler_raises_error() -> None:
    """
    Ensure unsubscribing a missing handler raises an error.
    """
    bus = EventBus()

    with pytest.raises(EventHandlerNotFoundError):
        bus.unsubscribe("test.event", working_handler)


@pytest.mark.asyncio
async def test_publish_requires_started_bus() -> None:
    """
    Ensure events cannot be published before EventBus startup.
    """
    bus = EventBus()
    event = DomainEvent(event_type="test.event", source="test")

    with pytest.raises(EventPublishError):
        await bus.publish(event)


@pytest.mark.asyncio
async def test_publish_rejects_invalid_event() -> None:
    """
    Ensure only DomainEvent instances can be published.
    """
    bus = EventBus()
    await bus.initialize()
    await bus.start()

    with pytest.raises(InvalidEventError):
        await bus.publish(object())  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_publish_without_subscribers_succeeds() -> None:
    """
    Ensure publishing an event without subscribers succeeds.
    """
    bus = EventBus()
    event = DomainEvent(event_type="test.event", source="test")

    await bus.initialize()
    await bus.start()

    await bus.publish(event)

    assert bus.published_events_count == 1
    assert bus.handler_errors_count == 0


@pytest.mark.asyncio
async def test_publish_dispatches_event_to_handler() -> None:
    """
    Ensure published events are dispatched to subscribed handlers.
    """
    bus = EventBus()
    received_events: list[DomainEvent] = []

    async def handler(event: DomainEvent) -> None:
        received_events.append(event)

    event = DomainEvent(event_type="test.event", source="test")

    bus.subscribe("test.event", handler)

    await bus.initialize()
    await bus.start()
    await bus.publish(event)

    assert received_events == [event]
    assert bus.published_events_count == 1
    assert bus.handler_errors_count == 0


@pytest.mark.asyncio
async def test_publish_isolates_handler_failures() -> None:
    """
    Ensure failing handlers do not prevent other handlers from running.
    """
    bus = EventBus()
    received_events: list[DomainEvent] = []

    async def successful_handler(event: DomainEvent) -> None:
        received_events.append(event)

    event = DomainEvent(event_type="test.event", source="test")

    bus.subscribe("test.event", failing_handler)
    bus.subscribe("test.event", successful_handler)

    await bus.initialize()
    await bus.start()

    with pytest.raises(EventPublishError):
        await bus.publish(event)

    assert received_events == [event]
    assert bus.published_events_count == 1
    assert bus.handler_errors_count == 1


@pytest.mark.asyncio
async def test_event_bus_lifecycle_manager_integration() -> None:
    """
    Ensure EventBus works through LifecycleManager.
    """
    lifecycle = LifecycleManager()
    bus = EventBus()

    await lifecycle.start(bus)

    assert bus.state == ServiceState.RUNNING

    await lifecycle.stop(bus)

    assert bus.state == ServiceState.STOPPED


@pytest.mark.asyncio
async def test_event_bus_health_check() -> None:
    """
    Ensure EventBus health check exposes safe runtime metadata.
    """
    bus = EventBus()

    bus.subscribe("test.event", working_handler)

    await bus.initialize()
    await bus.start()

    health = await bus.health_check()

    assert health["name"] == "event_bus"
    assert health["state"] == ServiceState.CREATED.value
    assert health["healthy"] is True
    assert health["started"] is True
    assert health["event_types"] == ["test.event"]
    assert health["subscription_count"] == 1
    assert health["published_events_count"] == 0
    assert health["handler_errors_count"] == 0