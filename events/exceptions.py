from __future__ import annotations


class EventBusError(Exception):
    """
    Base exception for all Event Bus related errors.

    All Event Bus errors must inherit from this class so they can be handled
    consistently by the Kernel, monitoring tools, tests, and future recovery
    mechanisms.
    """


class EventPublishError(EventBusError):
    """
    Raised when an event cannot be published successfully.
    """


class EventSubscriptionError(EventBusError):
    """
    Raised when an event handler cannot be subscribed or unsubscribed.
    """


class EventHandlerError(EventBusError):
    """
    Raised when an event handler fails while processing an event.
    """


class InvalidEventError(EventBusError):
    """
    Raised when an invalid event object is used.
    """


class InvalidEventHandlerError(EventSubscriptionError):
    """
    Raised when an invalid event handler is registered.
    """


class EventHandlerNotFoundError(EventSubscriptionError):
    """
    Raised when attempting to unsubscribe an event handler that is not registered.
    """