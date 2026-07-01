from __future__ import annotations

from typing import Any

import pytest

from kernel.exceptions import (
    ServiceAlreadyRegisteredError,
    ServiceNotFoundError,
    ServiceRegistrationError,
)
from kernel.registry import ServiceRegistry
from kernel.service import Service


class RegistryTestService(Service):
    """
    Concrete service implementation used only for testing the ServiceRegistry.
    """

    def __init__(self, name: str = "test_service") -> None:
        super().__init__(
            name=name,
            description="Registry test service.",
            version="1.0.0",
        )

    async def initialize(self) -> None:
        pass

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def health_check(self) -> dict[str, Any]:
        return await super().health_check()


def test_registry_starts_empty() -> None:
    """
    Ensure a new registry starts without services.
    """
    registry = ServiceRegistry()

    assert registry.count() == 0
    assert registry.list_services() == []
    assert registry.service_names() == ()


def test_register_service() -> None:
    """
    Ensure a valid service can be registered.
    """
    registry = ServiceRegistry()
    service = RegistryTestService(name="market_data")

    registry.register(service)

    assert registry.count() == 1
    assert registry.has("market_data") is True
    assert registry.get("market_data") is service


def test_register_rejects_non_service_object() -> None:
    """
    Ensure only Service instances can be registered.
    """
    registry = ServiceRegistry()

    with pytest.raises(ServiceRegistrationError):
        registry.register(object())  # type: ignore[arg-type]


def test_register_rejects_duplicate_service_name() -> None:
    """
    Ensure duplicate service names are rejected.
    """
    registry = ServiceRegistry()
    first_service = RegistryTestService(name="event_bus")
    second_service = RegistryTestService(name="event_bus")

    registry.register(first_service)

    with pytest.raises(ServiceAlreadyRegisteredError):
        registry.register(second_service)


def test_service_names_are_case_insensitive() -> None:
    """
    Ensure service lookups are case-insensitive.
    """
    registry = ServiceRegistry()
    service = RegistryTestService(name="HealthManager")

    registry.register(service)

    assert registry.has("healthmanager") is True
    assert registry.has("HEALTHMANAGER") is True
    assert registry.get("healthmanager") is service
    assert registry.get("HEALTHMANAGER") is service


def test_get_missing_service_raises_error() -> None:
    """
    Ensure requesting a missing service raises ServiceNotFoundError.
    """
    registry = ServiceRegistry()

    with pytest.raises(ServiceNotFoundError):
        registry.get("missing_service")


def test_get_optional_returns_none_for_missing_service() -> None:
    """
    Ensure optional lookup returns None when service does not exist.
    """
    registry = ServiceRegistry()

    assert registry.get_optional("missing_service") is None


def test_unregister_service() -> None:
    """
    Ensure a registered service can be removed.
    """
    registry = ServiceRegistry()
    service = RegistryTestService(name="scheduler")

    registry.register(service)
    removed_service = registry.unregister("scheduler")

    assert removed_service is service
    assert registry.count() == 0
    assert registry.has("scheduler") is False


def test_unregister_missing_service_raises_error() -> None:
    """
    Ensure unregistering a missing service raises ServiceNotFoundError.
    """
    registry = ServiceRegistry()

    with pytest.raises(ServiceNotFoundError):
        registry.unregister("missing_service")


def test_list_services_returns_copy() -> None:
    """
    Ensure list_services does not expose internal registry storage.
    """
    registry = ServiceRegistry()
    service = RegistryTestService(name="config_manager")

    registry.register(service)

    services = registry.list_services()
    services.clear()

    assert registry.count() == 1
    assert registry.get("config_manager") is service


def test_service_names_returns_registered_names() -> None:
    """
    Ensure service_names returns the original registered service names.
    """
    registry = ServiceRegistry()
    first_service = RegistryTestService(name="config_manager")
    second_service = RegistryTestService(name="event_bus")

    registry.register(first_service)
    registry.register(second_service)

    assert registry.service_names() == ("config_manager", "event_bus")


def test_clear_removes_all_services() -> None:
    """
    Ensure clear removes all registered services.
    """
    registry = ServiceRegistry()

    registry.register(RegistryTestService(name="config_manager"))
    registry.register(RegistryTestService(name="event_bus"))

    registry.clear()

    assert registry.count() == 0
    assert registry.list_services() == []


def test_extend_registers_multiple_services() -> None:
    """
    Ensure multiple services can be registered through extend.
    """
    registry = ServiceRegistry()

    services = [
        RegistryTestService(name="config_manager"),
        RegistryTestService(name="event_bus"),
        RegistryTestService(name="health_manager"),
    ]

    registry.extend(services)

    assert registry.count() == 3
    assert registry.has("config_manager") is True
    assert registry.has("event_bus") is True
    assert registry.has("health_manager") is True


def test_empty_service_name_lookup_is_rejected() -> None:
    """
    Ensure empty service names are rejected during lookup.
    """
    registry = ServiceRegistry()

    with pytest.raises(ServiceRegistrationError):
        registry.get("")
