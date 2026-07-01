from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4

from events.exceptions import InvalidEventError


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """
    Immutable base event used across ATOS.

    Domain events represent facts that already happened inside the system.
    They are used to decouple components and allow services to communicate
    through the Event Bus instead of direct dependencies.

    Events must be immutable so subscribers cannot accidentally mutate shared
    event data while processing it.
    """

    event_type: str
    source: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """
        Validate and freeze event mappings after initialization.
        """
        self._validate_event_id()
        self._validate_event_type()
        self._validate_source()
        self._validate_occurred_at()
        self._validate_mapping("payload", self.payload)
        self._validate_mapping("metadata", self.metadata)

        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the event to a serializable dictionary.

        Datetime is converted to ISO 8601 format so events can later be logged,
        persisted, exposed through APIs, or sent through message queues.
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "payload": dict(self.payload),
            "metadata": dict(self.metadata),
            "occurred_at": self.occurred_at.isoformat(),
        }

    def with_metadata(self, metadata: Mapping[str, Any]) -> "DomainEvent":
        """
        Return a new event with merged metadata.

        The original event remains unchanged.
        """
        self._validate_mapping("metadata", metadata)

        merged_metadata = {
            **dict(self.metadata),
            **dict(metadata),
        }

        return DomainEvent(
            event_id=self.event_id,
            event_type=self.event_type,
            source=self.source,
            payload=dict(self.payload),
            metadata=merged_metadata,
            occurred_at=self.occurred_at,
        )

    def _validate_event_id(self) -> None:
        """
        Validate event_id.
        """
        if not isinstance(self.event_id, str) or not self.event_id.strip():
            raise InvalidEventError("Event ID must be a non-empty string.")

    def _validate_event_type(self) -> None:
        """
        Validate event_type.
        """
        if not isinstance(self.event_type, str) or not self.event_type.strip():
            raise InvalidEventError("Event type must be a non-empty string.")

    def _validate_source(self) -> None:
        """
        Validate event source.
        """
        if not isinstance(self.source, str) or not self.source.strip():
            raise InvalidEventError("Event source must be a non-empty string.")

    def _validate_occurred_at(self) -> None:
        """
        Validate occurred_at.
        """
        if not isinstance(self.occurred_at, datetime):
            raise InvalidEventError("Event occurred_at must be a datetime instance.")

        if self.occurred_at.tzinfo is None:
            raise InvalidEventError("Event occurred_at must be timezone-aware.")

    @staticmethod
    def _validate_mapping(name: str, value: Mapping[str, Any]) -> None:
        """
        Validate event payload and metadata mappings.
        """
        if not isinstance(value, Mapping):
            raise InvalidEventError(f"Event {name} must be a mapping.")