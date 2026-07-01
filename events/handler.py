from __future__ import annotations

import inspect
from collections.abc import Awaitable
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

    Supported handlers:
    - async functions
    - objects with async __call__

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

    if _is_async_callable(handler):
        return handler  # type: ignore[return-value]

    raise InvalidEventHandlerError("Event handler must be an async callable.")


def get_handler_name(handler: EventHandler) -> str:
    """
    Return a stable readable name for an event handler.

    This is used for logging, debugging, monitoring, and future diagnostics.
    """
    return getattr(handler, "__qualname__", getattr(handler, "__name__", repr(handler)))


def _is_async_callable(handler: object) -> bool:
    """
    Return True if the handler is an async function or an object with async __call__.
    """
    if inspect.iscoroutinefunction(handler):
        return True

    call_method = getattr(handler, "__call__", None)

    return inspect.iscoroutinefunction(call_method)