from __future__ import annotations

import pytest

from config.manager import ConfigurationManager
from kernel import Kernel
from kernel.state import ServiceState
from services.dummy_service import DummyService


@pytest.mark.asyncio
async def test_kernel_boots_configuration_manager_and_dummy_service() -> None:
    """
    Ensure the Kernel can boot multiple managed services together.

    This integration test validates the current foundation boot path:
    - ConfigurationManager loads settings.
    - DummyService starts successfully.
    - Kernel health check reports both services.
    - Kernel shutdown stops both services gracefully.
    """
    kernel = Kernel()

    configuration_manager = ConfigurationManager(
        environ={
            "ATOS_ENV": "testing",
            "ATOS_DEBUG": "true",
            "ATOS_LOG_LEVEL": "info",
        }
    )
    dummy_service = DummyService()

    kernel.register_service(configuration_manager)
    kernel.register_service(dummy_service)

    try:
        await kernel.start()

        assert kernel.is_running is True
        assert kernel.service_count() == 2

        health = await kernel.health_check()

        assert health["kernel_running"] is True
        assert health["kernel_shutting_down"] is False
        assert health["service_count"] == 2

        services = {
            service_health["name"]: service_health
            for service_health in health["services"]
        }

        assert "configuration_manager" in services
        assert "dummy_service" in services

        configuration_health = services["configuration_manager"]

        assert configuration_health["state"] == ServiceState.RUNNING.value
        assert configuration_health["healthy"] is True
        assert configuration_health["settings_loaded"] is True
        assert configuration_health["environment"] == "testing"
        assert configuration_health["debug"] is True
        assert configuration_health["log_level"] == "INFO"

        dummy_health = services["dummy_service"]

        assert dummy_health["state"] == ServiceState.RUNNING.value
        assert dummy_health["healthy"] is True
        assert dummy_health["initialized"] is True
        assert dummy_health["started"] is True
        assert dummy_health["stopped"] is False

    finally:
        if kernel.is_running:
            await kernel.shutdown()

    assert kernel.is_running is False
    assert configuration_manager.state == ServiceState.STOPPED
    assert dummy_service.state == ServiceState.STOPPED