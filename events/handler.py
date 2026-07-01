from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Protocol, runtime_checkable

from events.base import DomainEvent
from events.exceptions import InvalidEventHandlerError


@runtime_checkable
class EventHandler(Protocol):
    """
    Protocol for asynchronous event handlers.

    Every Event Bus handler must accept a DomainEvent and return an awaitable
    result. Handlers must not mutate events.
    """

    def __call__(self, event: DomainEvent) -> Awaitable[None]:
        """
        Handle a domain event asynchronously.
        """


def validate_event_handler(handler: object) -> EventHandler:
    """
    Validate that an object is a supported asynchronous event handler.

    Args:
        handler:
            Object expected to be an async callable accepting a DomainEvent.

    Returns:
        EventHandler:
            The validated handler.

    Raises:
        InvalidEventHandlerError:
            If the handler is not callable or is not asynchronous.
    """
    if not callable(handler):
        raise InvalidEventHandlerError("Event handler must be callable.")

    if not inspect.iscoroutinefunction(handler):
        raise InvalidEventHandlerError(
            "Event handler must be an async callable."
        )

    return handler  # type: ignore[return-value]


def get_handler_name(handler: EventHandler) -> str:
    """
    Return a stable readable name for an event handler.

    This is used for logging, debugging, monitoring, and future diagnostics.
    """
    return getattr(handler, "__qualname__", getattr(handler, "__name__", repr(handler)))