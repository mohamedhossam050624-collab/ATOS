from __future__ import annotations

from kernel.state import ServiceState


def test_service_state_values_are_stable() -> None:
    """
    Ensure service state values remain stable.

    These values may be used later in logs, health checks, dashboards,
    monitoring systems, and persisted lifecycle records.
    """
    assert ServiceState.CREATED.value == "created"
    assert ServiceState.INITIALIZED.value == "initialized"
    assert ServiceState.STARTING.value == "starting"
    assert ServiceState.RUNNING.value == "running"
    assert ServiceState.STOPPING.value == "stopping"
    assert ServiceState.STOPPED.value == "stopped"
    assert ServiceState.FAILED.value == "failed"


def test_service_state_values_are_unique() -> None:
    """
    Ensure no two service states share the same value.
    """
    values = [state.value for state in ServiceState]

    assert len(values) == len(set(values))


def test_active_service_states() -> None:
    """
    Ensure active states correctly represent services that are initialized,
    starting, or running.
    """
    assert ServiceState.CREATED.is_active is False
    assert ServiceState.INITIALIZED.is_active is True
    assert ServiceState.STARTING.is_active is True
    assert ServiceState.RUNNING.is_active is True
    assert ServiceState.STOPPING.is_active is False
    assert ServiceState.STOPPED.is_active is False
    assert ServiceState.FAILED.is_active is False


def test_terminal_service_states() -> None:
    """
    Ensure terminal states correctly represent stopped or failed services.
    """
    assert ServiceState.CREATED.is_terminal is False
    assert ServiceState.INITIALIZED.is_terminal is False
    assert ServiceState.STARTING.is_terminal is False
    assert ServiceState.RUNNING.is_terminal is False
    assert ServiceState.STOPPING.is_terminal is False
    assert ServiceState.STOPPED.is_terminal is True
    assert ServiceState.FAILED.is_terminal is True