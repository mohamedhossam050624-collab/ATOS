from kernel.service import Service
from kernel.state import ServiceState
from shared.logger import logger


class DummyService(Service):
    def __init__(self) -> None:
        super().__init__("DummyService")

    async def initialize(self) -> None:
        self.set_state(ServiceState.INITIALIZED)
        logger.info(f"{self.name} initialized.")

    async def start(self) -> None:
        self.set_state(ServiceState.RUNNING)
        logger.info(f"{self.name} started.")

    async def stop(self) -> None:
        self.set_state(ServiceState.STOPPED)
        logger.info(f"{self.name} stopped.")