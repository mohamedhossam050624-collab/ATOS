from __future__ import annotations

from typing import Awaitable

import pytest

from events.base import DomainEvent
from events.exceptions import InvalidEventHandlerError
from events.handler import EventHandler, get_handler_name, validate_event_handler


async def async_test_handler(event: DomainEvent) -> None:
    """
    Valid async event handler used for tests.
    """


def sync_test_handler(event: DomainEvent) -> None:
    """
    Invalid sync event handler used for tests.
    """


class AsyncCallableHandler:
    """
    Async callable object used for handler validation tests.
    """

    async def __call__(self, event: DomainEvent) -> None:
        pass


class SyncCallableHandler:
    """
    Sync callable object used for handler validation tests.
    """

    def __call__(self, event: DomainEvent) -> None:
        pass


def test_validate_event_handler_accepts_async_function() -> None:
    """
    Ensure async functions are accepted as event handlers.
    """
    handler = validate_event_handler(async_test_handler)

    assert handler is async_test_handler


def test_validate_event_handler_rejects_sync_function() -> None:
    """
    Ensure sync functions are rejected.
    """
    with pytest.raises(InvalidEventHandlerError):
        validate_event_handler(sync_test_handler)


def test_validate_event_handler_rejects_non_callable_object() -> None:
    """
    Ensure non-callable objects are rejected.
    """
    with pytest.raises(InvalidEventHandlerError):
        validate_event_handler("not-a-handler")


def test_validate_event_handler_rejects_sync_callable_object() -> None:
    """
    Ensure sync callable objects are rejected.
    """
    handler = SyncCallableHandler()

    with pytest.raises(InvalidEventHandlerError):
        validate_event_handler(handler)


def test_get_handler_name_for_function() -> None:
    """
    Ensure handler names are readable for functions.
    """
    assert get_handler_name(async_test_handler) == "async_test_handler"


@pytest.mark.asyncio
async def test_validated_async_handler_can_be_called() -> None:
    """
    Ensure a validated async handler can process an event.
    """
    called = False

    async def handler(event: DomainEvent) -> None:
        nonlocal called
        called = True

    validated_handler = validate_event_handler(handler)

    event = DomainEvent(
        event_type="test.event",
        source="test",
    )

    await validated_handler(event)

    assert called is True