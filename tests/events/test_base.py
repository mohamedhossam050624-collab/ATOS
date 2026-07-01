from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from types import MappingProxyType

import pytest

from events.base import DomainEvent
from events.exceptions import InvalidEventError


def test_domain_event_can_be_created_with_required_fields() -> None:
    """
    Ensure a valid domain event can be created with required fields.
    """
    event = DomainEvent(
        event_type="kernel.service.started",
        source="kernel",
    )

    assert event.event_id
    assert event.event_type == "kernel.service.started"
    assert event.source == "kernel"
    assert event.payload == {}
    assert event.metadata == {}
    assert event.occurred_at.tzinfo is not None


def test_domain_event_payload_and_metadata_are_frozen_mappings() -> None:
    """
    Ensure payload and metadata are frozen after event creation.
    """
    event = DomainEvent(
        event_type="test.event",
        source="test",
        payload={"value": 10},
        metadata={"trace_id": "trace-1"},
    )

    assert isinstance(event.payload, MappingProxyType)
    assert isinstance(event.metadata, MappingProxyType)

    with pytest.raises(TypeError):
        event.payload["value"] = 20  # type: ignore[index]

    with pytest.raises(TypeError):
        event.metadata["trace_id"] = "trace-2"  # type: ignore[index]


def test_domain_event_is_dataclass_frozen() -> None:
    """
    Ensure event fields cannot be reassigned after creation.
    """
    event = DomainEvent(
        event_type="test.event",
        source="test",
    )

    with pytest.raises(FrozenInstanceError):
        event.event_type = "changed.event"  # type: ignore[misc]


def test_domain_event_to_dict_returns_serializable_data() -> None:
    """
    Ensure event can be converted to a dictionary.
    """
    occurred_at = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)

    event = DomainEvent(
        event_id="event-1",
        event_type="test.event",
        source="test",
        payload={"number": 1},
        metadata={"trace_id": "abc"},
        occurred_at=occurred_at,
    )

    data = event.to_dict()

    assert data == {
        "event_id": "event-1",
        "event_type": "test.event",
        "source": "test",
        "payload": {"number": 1},
        "metadata": {"trace_id": "abc"},
        "occurred_at": "2026-01-01T12:00:00+00:00",
    }


def test_with_metadata_returns_new_event_with_merged_metadata() -> None:
    """
    Ensure with_metadata returns a new event and preserves the original.
    """
    event = DomainEvent(
        event_id="event-1",
        event_type="test.event",
        source="test",
        payload={"value": 1},
        metadata={"trace_id": "trace-1"},
    )

    updated_event = event.with_metadata(
        {
            "correlation_id": "correlation-1",
        }
    )

    assert updated_event is not event
    assert updated_event.event_id == event.event_id
    assert updated_event.event_type == event.event_type
    assert updated_event.source == event.source
    assert updated_event.payload == event.payload
    assert updated_event.occurred_at == event.occurred_at

    assert dict(event.metadata) == {"trace_id": "trace-1"}
    assert dict(updated_event.metadata) == {
        "trace_id": "trace-1",
        "correlation_id": "correlation-1",
    }


def test_with_metadata_overrides_existing_metadata_keys() -> None:
    """
    Ensure new metadata values override existing metadata keys.
    """
    event = DomainEvent(
        event_type="test.event",
        source="test",
        metadata={"trace_id": "old"},
    )

    updated_event = event.with_metadata({"trace_id": "new"})

    assert updated_event.metadata["trace_id"] == "new"
    assert event.metadata["trace_id"] == "old"


def test_domain_event_rejects_empty_event_id() -> None:
    """
    Ensure event_id must be non-empty.
    """
    with pytest.raises(InvalidEventError):
        DomainEvent(
            event_id="",
            event_type="test.event",
            source="test",
        )


def test_domain_event_rejects_empty_event_type() -> None:
    """
    Ensure event_type must be non-empty.
    """
    with pytest.raises(InvalidEventError):
        DomainEvent(
            event_type="",
            source="test",
        )


def test_domain_event_rejects_empty_source() -> None:
    """
    Ensure source must be non-empty.
    """
    with pytest.raises(InvalidEventError):
        DomainEvent(
            event_type="test.event",
            source="",
        )


def test_domain_event_rejects_non_mapping_payload() -> None:
    """
    Ensure payload must be a mapping.
    """
    with pytest.raises(InvalidEventError):
        DomainEvent(
            event_type="test.event",
            source="test",
            payload=["not", "a", "mapping"],  # type: ignore[arg-type]
        )


def test_domain_event_rejects_non_mapping_metadata() -> None:
    """
    Ensure metadata must be a mapping.
    """
    with pytest.raises(InvalidEventError):
        DomainEvent(
            event_type="test.event",
            source="test",
            metadata=["not", "a", "mapping"],  # type: ignore[arg-type]
        )


def test_domain_event_rejects_non_datetime_occurred_at() -> None:
    """
    Ensure occurred_at must be a datetime instance.
    """
    with pytest.raises(InvalidEventError):
        DomainEvent(
            event_type="test.event",
            source="test",
            occurred_at="2026-01-01",  # type: ignore[arg-type]
        )


def test_domain_event_rejects_naive_datetime() -> None:
    """
    Ensure occurred_at must be timezone-aware.
    """
    with pytest.raises(InvalidEventError):
        DomainEvent(
            event_type="test.event",
            source="test",
            occurred_at=datetime(2026, 1, 1, 12, 0),
        )