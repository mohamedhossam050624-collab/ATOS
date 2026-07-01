from __future__ import annotations

from typing import Dict

from kernel.exceptions import (
    ServiceAlreadyRegisteredError,
    ServiceNotFoundError,
)
from kernel.service import Service


class ServiceRegistry:
    """
    Stores and manages all registered services.
    """

    def __init__(self) -> None:
        self._services: Dict[str, Service] = {}

    def register(self, service: Service) -> None:
        """
        Register a new service.
        """
        if service.name in self._services:
            raise ServiceAlreadyRegisteredError(
                f"Service '{service.name}' is already registered."
            )

        self._services[service.name] = service

    def get(self, name: str) -> Service:
        """
        Retrieve a service by name.
        """
        try:
            return self._services[name]
        except KeyError as exc:
            raise ServiceNotFoundError(
                f"Service '{name}' not found."
            ) from exc

    def exists(self, name: str) -> bool:
        """
        Check whether a service is registered.
        """
        return name in self._services

    def all(self) -> list[Service]:
        """
        Return all registered services.
        """
        return list(self._services.values())

    def remove(self, name: str) -> None:
        """
        Remove a registered service.
        """
        self._services.pop(name, None)

    def clear(self) -> None:
        """
        Remove all registered services.
        """
        self._services.clear()

    def count(self) -> int:
        """
        Return the number of registered services.
        """
        return len(self._services)