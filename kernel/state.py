from __future__ import annotations

from enum import Enum


class ServiceState(str, Enum):
    """
    Represents the lifecycle state of a Kernel-managed service.

    These states are used by the Kernel lifecycle manager to control
    initialization, startup, shutdown, and failure handling.
    """

    CREATED = "created"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"

    @property
    def is_active(self) -> bool:
        """
        Return True if the service is currently active or transitioning
        into an active runtime state.
        """
        return self in {
            ServiceState.INITIALIZED,
            ServiceState.STARTING,
            ServiceState.RUNNING,
        }

    @property
    def is_terminal(self) -> bool:
        """
        Return True if the service is in a final or non-operational state.
        """
        return self in {
            ServiceState.STOPPED,
            ServiceState.FAILED,
        }