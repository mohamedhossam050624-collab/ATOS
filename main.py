from __future__ import annotations

import asyncio
import sys
from typing import Any

from config.manager import ConfigurationManager
from events.bus import EventBus
from kernel import Kernel
from kernel.exceptions import KernelError
from services.dummy_service import DummyService
from shared.logger import logger


async def run_kernel_smoke_test() -> dict[str, Any]:
    """
    Run a minimal ATOS Kernel smoke test.

    This entrypoint validates that the Kernel can:
    - Register multiple foundation services.
    - Start all registered services.
    - Load configuration through the Configuration Manager.
    - Start the in-memory Event Bus.
    - Run health checks.
    - Shut down gracefully.

    This file is temporary for the foundation phase and must not contain
    trading logic, AI logic, broker logic, strategy logic, or business workflows.
    """
    kernel = Kernel()

    configuration_manager = ConfigurationManager(environ={})
    event_bus = EventBus()
    dummy_service = DummyService()

    kernel.register_service(configuration_manager)
    kernel.register_service(event_bus)
    kernel.register_service(dummy_service)

    try:
        await kernel.start()

        health = await kernel.health_check()
        logger.info(f"Kernel health check result: {health}")

        return health

    finally:
        if kernel.is_running:
            await kernel.shutdown()


def main() -> int:
    """
    Application entrypoint for the current foundation smoke test.

    Returns:
        0 when the Kernel smoke test succeeds.
        1 when a controlled Kernel error occurs.
        2 when an unexpected error occurs.
    """
    try:
        health = asyncio.run(run_kernel_smoke_test())

        print("ATOS Kernel smoke test completed successfully.")
        print(health)

        return 0

    except KernelError as exc:
        logger.exception("ATOS Kernel failed during smoke test.")
        print(f"ATOS Kernel error: {exc}", file=sys.stderr)
        return 1

    except Exception as exc:
        logger.exception("Unexpected ATOS startup error.")
        print(f"Unexpected ATOS error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())