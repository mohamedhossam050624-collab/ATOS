from __future__ import annotations

from abc import ABC, abstractmethod

from kernel.state import ServiceState


class Service(ABC):
    """
    Base class for every service inside ATOS.

    Every service must inherit from this class.
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._state = ServiceState.CREATED

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> ServiceState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state == ServiceState.RUNNING

    def set_state(self, state: ServiceState) -> None:
        self._state = state

    @abstractmethod
    async def initialize(self) -> None:
        """Prepare the service before startup."""

    @abstractmethod
    async def start(self) -> None:
        """Start the service."""

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully stop the service."""