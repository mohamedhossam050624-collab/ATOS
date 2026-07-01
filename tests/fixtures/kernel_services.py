from __future__ import annotations

from typing import Any

from kernel.service import Service


class KernelTestService(Service):
    """
    Reusable test service for Kernel-related tests.

    This service is intentionally simple and deterministic. It is used to
    verify Kernel lifecycle, registry, service abstraction, and health-check
    behavior without introducing real business logic.
    """

    def __init__(
        self,
        name: str = "test_service",
        description: str = "Reusable Kernel test service.",
        version: str = "1.0.0",
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            version=version,
        )
        self.initialized = False
        self.started = False
        self.stopped = False

    async def initialize(self) -> None:
        """
        Mark the service as initialized.
        """
        self.initialized = True

    async def start(self) -> None:
        """
        Mark the service as started.
        """
        self.started = True
        self.stopped = False

    async def stop(self) -> None:
        """
        Mark the service as stopped.
        """
        self.started = False
        self.stopped = True

    async def health_check(self) -> dict[str, Any]:
        """
        Return service health information for tests.
        """
        health = await super().health_check()
        health.update(
            {
                "initialized": self.initialized,
                "started": self.started,
                "stopped": self.stopped,
            }
        )
        return health


class FailingInitializeService(KernelTestService):
    """
    Test service that fails during initialization.
    """

    async def initialize(self) -> None:
        raise RuntimeError("Initialization failed.")


class FailingStartService(KernelTestService):
    """
    Test service that fails during startup.
    """

    async def start(self) -> None:
        raise RuntimeError("Startup failed.")


class FailingStopService(KernelTestService):
    """
    Test service that fails during shutdown.
    """

    async def stop(self) -> None:
        raise RuntimeError("Shutdown failed.")