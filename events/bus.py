from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from events.base import DomainEvent
from events.exceptions import (
    EventHandlerError,
    EventHandlerNotFoundError,
    EventPublishError,
    EventSubscriptionError,
    InvalidEventError,
)
from events.handler import EventHandler, get_handler_name, validate_event_handler
from kernel.service import Service
from shared.logger import logger


class EventBus(Service):
    """
    In-memory asynchronous Event Bus for ATOS.

    The Event Bus enables loose coupling between system components by allowing
    services to publish immutable DomainEvents and subscribers to react without
    direct dependencies between domains.

    This implementation is intentionally in-memory for the foundation phase.
    Future versions may add durable persistence, message queues, retries,
    dead-letter queues, and distributed event processing.
    """

    def __init__(self) -> None:
        super().__init__(
            name="event_bus",
            description="In-memory asynchronous domain event bus.",
            version="1.0.0",
        )
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)
        self._published_events_count = 0
        self._handler_errors_count = 0
        self._is_started = False

    @property
    def published_events_count(self) -> int:
        """
        Return the total number of successfully published events.
        """
        return self._published_events_count

    @property
    def handler_errors_count(self) -> int:
        """
        Return the total number of handler failures.
        """
        return self._handler_errors_count

    @property
    def subscription_count(self) -> int:
        """
        Return the total number of registered event handlers.
        """
        return sum(len(handlers) for handlers in self._subscribers.values())

    def subscribe(self, event_type: str, handler: object) -> None:
        """
        Subscribe an async handler to a specific event type.

        Args:
            event_type:
                Event type to subscribe to.

            handler:
                Async callable that accepts a DomainEvent.

        Raises:
            EventSubscriptionError:
                If event_type is invalid.

            InvalidEventHandlerError:
                If handler is not a valid async callable.
        """
        normalized_event_type = self._normalize_event_type(event_type)
        validated_handler = validate_event_handler(handler)

        if validated_handler in self._subscribers[normalized_event_type]:
            logger.warning(
                "Event handler already subscribed: "
                f"{get_handler_name(validated_handler)} -> {normalized_event_type}"
            )
            return

        self._subscribers[normalized_event_type].append(validated_handler)

        logger.info(
            "Subscribed event handler: "
            f"{get_handler_name(validated_handler)} -> {normalized_event_type}"
        )

    def unsubscribe(self, event_type: str, handler: object) -> None:
        """
        Unsubscribe a handler from a specific event type.

        Raises:
            EventHandlerNotFoundError:
                If the handler is not registered for the event type.
        """
        normalized_event_type = self._normalize_event_type(event_type)
        validated_handler = validate_event_handler(handler)

        handlers = self._subscribers.get(normalized_event_type, [])

        if validated_handler not in handlers:
            raise EventHandlerNotFoundError(
                "Event handler is not subscribed to event type "
                f"'{normalized_event_type}'."
            )

        handlers.remove(validated_handler)

        if not handlers:
            self._subscribers.pop(normalized_event_type, None)

        logger.info(
            "Unsubscribed event handler: "
            f"{get_handler_name(validated_handler)} -> {normalized_event_type}"
        )

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event to all handlers subscribed to its event type.

        Handler failures are isolated and logged. If one or more handlers fail,
        EventPublishError is raised after all handlers have been attempted.
        """
        if not isinstance(event, DomainEvent):
            raise InvalidEventError(
                f"EventBus can only publish DomainEvent instances. Got: {type(event)!r}"
            )

        if not self._is_started:
            raise EventPublishError("EventBus cannot publish events before startup.")

        handlers = self._subscribers.get(event.event_type, [])

        if not handlers:
            logger.debug(f"No handlers subscribed for event type: {event.event_type}")
            self._published_events_count += 1
            return

        logger.info(
            f"Publishing event '{event.event_type}' to {len(handlers)} handler(s)."
        )

        errors = await self._dispatch_event(event, handlers)

        self._published_events_count += 1

        if errors:
            self._handler_errors_count += len(errors)
            raise EventPublishError(
                f"Event '{event.event_type}' published with {len(errors)} handler error(s)."
            )

    def subscribers_for(self, event_type: str) -> tuple[EventHandler, ...]:
        """
        Return subscribed handlers for an event type.

        A tuple is returned to prevent external mutation of subscriber state.
        """
        normalized_event_type = self._normalize_event_type(event_type)
        return tuple(self._subscribers.get(normalized_event_type, []))

    def event_types(self) -> tuple[str, ...]:
        """
        Return event types that currently have subscribers.
        """
        return tuple(self._subscribers.keys())

    async def initialize(self) -> None:
        """
        Initialize the Event Bus.

        No external resources are required for the in-memory foundation version.
        """
        logger.info("Event Bus initialized.")

    async def start(self) -> None:
        """
        Start the Event Bus.
        """
        self._is_started = True
        logger.info("Event Bus started.")

    async def stop(self) -> None:
        """
        Stop the Event Bus.

        Subscriptions are kept in memory for diagnostics and controlled tests.
        Future distributed versions may close network connections here.
        """
        self._is_started = False
        logger.info("Event Bus stopped.")

    async def health_check(self) -> dict[str, Any]:
        """
        Return Event Bus health information.
        """
        base_health = await super().health_check()

        base_health.update(
            {
                "started": self._is_started,
                "event_types": list(self.event_types()),
                "subscription_count": self.subscription_count,
                "published_events_count": self._published_events_count,
                "handler_errors_count": self._handler_errors_count,
            }
        )

        return base_health

    async def _dispatch_event(
        self,
        event: DomainEvent,
        handlers: Iterable[EventHandler],
    ) -> list[EventHandlerError]:
        """
        Dispatch an event to all handlers and isolate handler failures.
        """
        tasks = [
            self._safe_call_handler(handler, event)
            for handler in handlers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        errors: list[EventHandlerError] = []

        for result in results:
            if isinstance(result, EventHandlerError):
                errors.append(result)

        return errors

    async def _safe_call_handler(
        self,
        handler: EventHandler,
        event: DomainEvent,
    ) -> EventHandlerError | None:
        """
        Execute a handler safely and convert failures to EventHandlerError.
        """
        try:
            await handler(event)
            return None

        except Exception as exc:
            handler_name = get_handler_name(handler)

            logger.exception(
                f"Event handler failed: {handler_name} for event {event.event_type}"
            )

            return EventHandlerError(
                f"Handler '{handler_name}' failed for event '{event.event_type}'."
            )

    @staticmethod
    def _normalize_event_type(event_type: str) -> str:
        """
        Normalize and validate event type names.
        """
        if not isinstance(event_type, str) or not event_type.strip():
            raise EventSubscriptionError("Event type must be a non-empty string.")

        return event_type.strip()