from __future__ import annotations

import pytest

from config.environment import RuntimeEnvironment
from config.exceptions import (
    ConfigurationLoadError,
    InvalidConfigurationValueError,
    UnsupportedEnvironmentError,
)
from config.manager import ConfigurationManager
from kernel.lifecycle import LifecycleManager
from kernel.service import Service
from kernel.state import ServiceState


def test_configuration_manager_is_kernel_service() -> None:
    """
    Ensure ConfigurationManager is a Kernel-managed service.
    """
    manager = ConfigurationManager()

    assert isinstance(manager, Service)
    assert manager.name == "configuration_manager"
    assert manager.state == ServiceState.CREATED


def test_settings_access_before_loading_raises_error() -> None:
    """
    Ensure settings cannot be accessed before initialization.
    """
    manager = ConfigurationManager()

    with pytest.raises(ConfigurationLoadError):
        _ = manager.settings


def test_configuration_manager_starts_unloaded() -> None:
    """
    Ensure a new ConfigurationManager starts without loaded settings.
    """
    manager = ConfigurationManager()

    assert manager.is_loaded is False


@pytest.mark.asyncio
async def test_initialize_loads_default_settings() -> None:
    """
    Ensure initialize loads safe default settings.
    """
    manager = ConfigurationManager(environ={})

    await manager.initialize()

    assert manager.is_loaded is True
    assert manager.settings.app_name == "ATOS"
    assert manager.settings.environment == RuntimeEnvironment.DEVELOPMENT
    assert manager.settings.debug is False
    assert manager.settings.log_level == "INFO"


@pytest.mark.asyncio
async def test_initialize_loads_custom_settings() -> None:
    """
    Ensure initialize loads custom environment-backed settings.
    """
    manager = ConfigurationManager(
        environ={
            "ATOS_APP_NAME": "ATOS Test",
            "ATOS_ENV": "testing",
            "ATOS_DEBUG": "true",
            "ATOS_LOG_LEVEL": "debug",
        }
    )

    await manager.initialize()

    assert manager.is_loaded is True
    assert manager.settings.app_name == "ATOS Test"
    assert manager.settings.environment == RuntimeEnvironment.TESTING
    assert manager.settings.debug is True
    assert manager.settings.log_level == "DEBUG"


@pytest.mark.asyncio
async def test_initialize_rejects_invalid_environment() -> None:
    """
    Ensure invalid runtime environments are rejected.
    """
    manager = ConfigurationManager(
        environ={
            "ATOS_ENV": "local",
        }
    )

    with pytest.raises(UnsupportedEnvironmentError):
        await manager.initialize()

    assert manager.is_loaded is False


@pytest.mark.asyncio
async def test_initialize_rejects_debug_in_production() -> None:
    """
    Ensure debug mode cannot be enabled in production.
    """
    manager = ConfigurationManager(
        environ={
            "ATOS_ENV": "production",
            "ATOS_DEBUG": "true",
        }
    )

    with pytest.raises(InvalidConfigurationValueError):
        await manager.initialize()

    assert manager.is_loaded is False


@pytest.mark.asyncio
async def test_start_before_initialize_raises_error() -> None:
    """
    Ensure ConfigurationManager cannot start before settings are loaded.
    """
    manager = ConfigurationManager()

    with pytest.raises(ConfigurationLoadError):
        await manager.start()


@pytest.mark.asyncio
async def test_start_after_initialize_succeeds() -> None:
    """
    Ensure ConfigurationManager can start after initialization.
    """
    manager = ConfigurationManager(environ={})

    await manager.initialize()
    await manager.start()

    assert manager.is_loaded is True


@pytest.mark.asyncio
async def test_health_check_before_initialize() -> None:
    """
    Ensure health check reports unloaded settings before initialization.
    """
    manager = ConfigurationManager()

    health = await manager.health_check()

    assert health["name"] == "configuration_manager"
    assert health["state"] == ServiceState.CREATED.value
    assert health["healthy"] is True
    assert health["settings_loaded"] is False
    assert health["environment"] is None
    assert health["debug"] is None
    assert health["log_level"] is None


@pytest.mark.asyncio
async def test_health_check_after_initialize() -> None:
    """
    Ensure health check reports loaded safe configuration metadata.
    """
    manager = ConfigurationManager(
        environ={
            "ATOS_ENV": "testing",
            "ATOS_DEBUG": "true",
            "ATOS_LOG_LEVEL": "warning",
        }
    )

    await manager.initialize()

    health = await manager.health_check()

    assert health["name"] == "configuration_manager"
    assert health["settings_loaded"] is True
    assert health["environment"] == "testing"
    assert health["debug"] is True
    assert health["log_level"] == "WARNING"


@pytest.mark.asyncio
async def test_configuration_manager_lifecycle() -> None:
    """
    Ensure ConfigurationManager works through the Kernel lifecycle manager.
    """
    lifecycle = LifecycleManager()
    manager = ConfigurationManager(environ={})

    await lifecycle.start(manager)

    assert manager.is_loaded is True
    assert manager.state == ServiceState.RUNNING

    await lifecycle.stop(manager)

    assert manager.state == ServiceState.STOPPED