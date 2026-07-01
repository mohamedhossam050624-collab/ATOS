from __future__ import annotations

from typing import Any

from kernel.service import Service


class DummyService(Service):
    """
    Temporary smoke-test service for validating Kernel lifecycle behavior.

    This service exists only to prove that the Kernel can register, initialize,
    start, stop, and health-check a managed service.

    It must not contain business logic.
    It should be moved to test fixtures later.
    """

    def __init__(self) -> None:
        super().__init__(
            name="dummy_service",
            description="Temporary service used for Kernel smoke testing.",
            version="1.0.0",
        )
        self._initialized = False
        self._started = False
        self._stopped = False

    async def initialize(self) -> None:
        """
        Prepare the dummy service for startup.
        """
        self._initialized = True

    async def start(self) -> None:
        """
        Start the dummy service.
        """
        if not self._initialized:
            raise RuntimeError("DummyService cannot start before initialization.")

        self._started = True
        self._stopped = False

    async def stop(self) -> None:
        """
        Stop the dummy service.
        """
        self._started = False
        self._stopped = True

    async def health_check(self) -> dict[str, Any]:
        """
        Return dummy service health information.
        """
        base_health = await super().health_check()
        base_health.update(
            {
                "initialized": self._initialized,
                "started": self._started,
                "stopped": self._stopped,
            }
        )
        return base_health