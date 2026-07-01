from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from config.exceptions import ConfigurationError, ConfigurationLoadError
from config.settings import AppSettings, load_settings
from kernel.service import Service
from shared.logger import logger


class ConfigurationManager(Service):
    """
    Kernel-managed service responsible for loading and exposing ATOS settings.

    The Configuration Manager is the single access point for application-level
    configuration. Other components should depend on this service instead of
    reading environment variables directly.

    This manager currently handles safe non-secret AppSettings only.

    Secrets, broker credentials, API keys, database credentials, and model keys
    must be introduced later through dedicated secret-management mechanisms.
    """

    def __init__(
        self,
        environ: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            name="configuration_manager",
            description="Loads and provides validated ATOS configuration.",
            version="1.0.0",
        )
        self._environ = environ
        self._settings: AppSettings | None = None

    @property
    def is_loaded(self) -> bool:
        """
        Return True when settings have been loaded successfully.
        """
        return self._settings is not None

    @property
    def settings(self) -> AppSettings:
        """
        Return loaded application settings.

        Raises:
            ConfigurationLoadError:
                If settings have not been loaded yet.
        """
        if self._settings is None:
            raise ConfigurationLoadError(
                "Configuration settings have not been loaded yet."
            )

        return self._settings

    async def initialize(self) -> None:
        """
        Load and validate application settings.

        This method is intentionally side-effect-light. It validates and stores
        settings but does not start background tasks or connect to external
        systems.
        """
        try:
            logger.info("Loading ATOS configuration settings.")
            self._settings = load_settings(self._environ)
            logger.info(
                "ATOS configuration loaded successfully "
                f"for environment: {self._settings.environment.value}"
            )

        except ConfigurationError:
            logger.exception("ATOS configuration failed validation.")
            raise

        except Exception as exc:
            logger.exception("Unexpected error while loading ATOS configuration.")
            raise ConfigurationLoadError(
                "Unexpected error while loading ATOS configuration."
            ) from exc

    async def start(self) -> None:
        """
        Start the Configuration Manager.

        Configuration must be loaded before the service is considered started.
        """
        if self._settings is None:
            raise ConfigurationLoadError(
                "Configuration Manager cannot start before settings are loaded."
            )

        logger.info("Configuration Manager started.")

    async def stop(self) -> None:
        """
        Stop the Configuration Manager.

        Loaded settings are kept in memory for post-shutdown diagnostics. They
        do not contain secrets.
        """
        logger.info("Configuration Manager stopped.")

    async def health_check(self) -> dict[str, Any]:
        """
        Return Configuration Manager health data.

        The response intentionally excludes sensitive values and only exposes
        safe metadata.
        """
        base_health = await super().health_check()

        base_health.update(
            {
                "settings_loaded": self.is_loaded,
                "environment": (
                    self._settings.environment.value if self._settings else None
                ),
                "debug": self._settings.debug if self._settings else None,
                "log_level": self._settings.log_level if self._settings else None,
            }
        )

        return base_health