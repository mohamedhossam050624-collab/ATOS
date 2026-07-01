from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from kernel.exceptions import InvalidServiceStateError
from kernel.state import ServiceState


@dataclass(slots=True)
class ServiceMetadata:
    """
    Metadata describing a Kernel-managed service.

    This metadata is intentionally lightweight and infrastructure-neutral.
    It helps with logging, health reporting, debugging, and future service
    discovery without coupling the Kernel to external systems.
    """

    service_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class Service(ABC):
    """
    Base abstraction for every service managed by the ATOS Kernel.

    A service represents a lifecycle-controlled platform component.
    Examples include configuration loaders, event buses, plugin managers,
    schedulers, health monitors, brokers, and infrastructure adapters.

    Services must not perform responsibilities outside their assigned domain.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        version: str = "1.0.0",
    ) -> None:
        if not name or not name.strip():
            raise ValueError("Service name must not be empty.")

        self._metadata = ServiceMetadata(
            name=name.strip(),
            description=description.strip(),
            version=version.strip() or "1.0.0",
        )
        self._state = ServiceState.CREATED

    @property
    def metadata(self) -> ServiceMetadata:
        """
        Return immutable-style service metadata.

        The returned dataclass is used for introspection and future health
        reporting. Service identity should not change after creation.
        """
        return self._metadata

    @property
    def service_id(self) -> str:
        """
        Return the unique service identifier.
        """
        return self._metadata.service_id

    @property
    def name(self) -> str:
        """
        Return the service name.
        """
        return self._metadata.name

    @property
    def description(self) -> str:
        """
        Return the service description.
        """
        return self._metadata.description

    @property
    def version(self) -> str:
        """
        Return the service version.
        """
        return self._metadata.version

    @property
    def state(self) -> ServiceState:
        """
        Return the current lifecycle state of the service.
        """
        return self._state

    def set_state(self, state: ServiceState) -> None:
        """
        Update the service lifecycle state.

        State transitions are controlled by the Kernel lifecycle manager.
        This method validates that only ServiceState values are assigned.
        """
        if not isinstance(state, ServiceState):
            raise InvalidServiceStateError(
                f"Invalid service state for '{self.name}': {state!r}"
            )

        self._state = state

    @abstractmethod
    async def initialize(self) -> None:
        """
        Prepare the service before startup.

        This method should load local dependencies, validate configuration,
        and prepare internal resources. It must not start long-running work.
        """

    @abstractmethod
    async def start(self) -> None:
        """
        Start the service.

        This method should activate the service after initialization.
        """

    @abstractmethod
    async def stop(self) -> None:
        """
        Stop the service gracefully.

        This method should release resources and stop background work safely.
        """

    async def health_check(self) -> dict[str, Any]:
        """
        Return the current health status of the service.

        Default behavior is intentionally conservative and can be overridden
        by concrete services that need deeper checks.
        """
        return {
            "service_id": self.service_id,
            "name": self.name,
            "version": self.version,
            "state": self.state.value,
            "healthy": self.state != ServiceState.FAILED,
        }