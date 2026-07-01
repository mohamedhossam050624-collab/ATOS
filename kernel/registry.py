from __future__ import annotations

from collections.abc import Iterable

from kernel.exceptions import (
    ServiceAlreadyRegisteredError,
    ServiceNotFoundError,
    ServiceRegistrationError,
)
from kernel.service import Service


class ServiceRegistry:
    """
    Registry for Kernel-managed services.

    The registry is responsible for storing, retrieving, listing, and removing
    services controlled by the ATOS Kernel.

    It does not start or stop services.
    Lifecycle operations belong to the LifecycleManager.
    """

    def __init__(self) -> None:
        self._services: dict[str, Service] = {}

    def register(self, service: Service) -> None:
        """
        Register a service by its unique service name.

        Raises:
            ServiceRegistrationError: If the given object is not a Service.
            ServiceAlreadyRegisteredError: If a service with the same name exists.
        """
        if not isinstance(service, Service):
            raise ServiceRegistrationError(
                f"Only Service instances can be registered. Got: {type(service)!r}"
            )

        service_name = self._normalize_name(service.name)

        if service_name in self._services:
            raise ServiceAlreadyRegisteredError(
                f"Service '{service.name}' is already registered."
            )

        self._services[service_name] = service

    def unregister(self, service_name: str) -> Service:
        """
        Remove and return a registered service by name.

        Raises:
            ServiceNotFoundError: If the service is not registered.
        """
        normalized_name = self._normalize_name(service_name)

        if normalized_name not in self._services:
            raise ServiceNotFoundError(
                f"Service '{service_name}' is not registered."
            )

        return self._services.pop(normalized_name)

    def get(self, service_name: str) -> Service:
        """
        Return a registered service by name.

        Raises:
            ServiceNotFoundError: If the service is not registered.
        """
        normalized_name = self._normalize_name(service_name)

        if normalized_name not in self._services:
            raise ServiceNotFoundError(
                f"Service '{service_name}' is not registered."
            )

        return self._services[normalized_name]

    def get_optional(self, service_name: str) -> Service | None:
        """
        Return a registered service by name, or None if it does not exist.
        """
        normalized_name = self._normalize_name(service_name)
        return self._services.get(normalized_name)

    def has(self, service_name: str) -> bool:
        """
        Return True if a service is registered.
        """
        normalized_name = self._normalize_name(service_name)
        return normalized_name in self._services

    def list_services(self) -> list[Service]:
        """
        Return all registered services.

        A new list is returned to prevent external mutation of registry state.
        """
        return list(self._services.values())

    def service_names(self) -> tuple[str, ...]:
        """
        Return all registered service names.
        """
        return tuple(service.name for service in self._services.values())

    def count(self) -> int:
        """
        Return the number of registered services.
        """
        return len(self._services)

    def clear(self) -> None:
        """
        Clear all registered services.

        This should only be used during controlled shutdown, tests, or recovery.
        """
        self._services.clear()

    def extend(self, services: Iterable[Service]) -> None:
        """
        Register multiple services.

        Registration stops immediately if any service is invalid or duplicated.
        """
        for service in services:
            self.register(service)

    @staticmethod
    def _normalize_name(service_name: str) -> str:
        """
        Normalize service names before registry lookup.

        Service names are treated as case-insensitive to prevent accidental
        duplicates such as 'EventBus' and 'eventbus'.
        """
        if not isinstance(service_name, str) or not service_name.strip():
            raise ServiceRegistrationError("Service name must be a non-empty string.")

        return service_name.strip().lower()