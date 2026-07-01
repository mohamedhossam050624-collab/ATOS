import asyncio

from kernel import Kernel
from services.dummy_service import DummyService


async def main() -> None:
    kernel = Kernel()

    kernel.register(DummyService())

    await kernel.start()

    input("\nPress ENTER to shutdown...\n")

    await kernel.stop()


if __name__ == "__main__":
    asyncio.run(main())