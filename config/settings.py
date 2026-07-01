from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from config.environment import RuntimeEnvironment
from config.exceptions import InvalidConfigurationValueError


DEFAULT_APP_NAME: Final[str] = "ATOS"
DEFAULT_ENVIRONMENT: Final[RuntimeEnvironment] = RuntimeEnvironment.DEVELOPMENT
DEFAULT_DEBUG: Final[bool] = False
DEFAULT_LOG_LEVEL: Final[str] = "INFO"

VALID_LOG_LEVELS: Final[set[str]] = {
    "TRACE",
    "DEBUG",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
}

TRUE_VALUES: Final[set[str]] = {"1", "true", "yes", "y", "on"}
FALSE_VALUES: Final[set[str]] = {"0", "false", "no", "n", "off"}


@dataclass(frozen=True, slots=True)
class AppSettings:
    """
    Immutable application-level settings for ATOS.

    This settings object contains only safe, non-secret platform configuration.

    Secrets such as broker keys, API tokens, database passwords, and model keys
    must never be stored directly in this object unless they are loaded through
    a dedicated secret-management mechanism in a future configuration layer.
    """

    app_name: str
    environment: RuntimeEnvironment
    debug: bool
    log_level: str

    @property
    def is_development(self) -> bool:
        """
        Return True when ATOS is running in development mode.
        """
        return self.environment == RuntimeEnvironment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """
        Return True when ATOS is running in testing mode.
        """
        return self.environment == RuntimeEnvironment.TESTING

    @property
    def is_production(self) -> bool:
        """
        Return True when ATOS is running in production mode.
        """
        return self.environment == RuntimeEnvironment.PRODUCTION


def load_settings(environ: Mapping[str, str] | None = None) -> AppSettings:
    """
    Load ATOS application settings from environment variables.

    Args:
        environ:
            Optional environment mapping used for tests. If omitted, os.environ
            is used.

    Supported variables:
        ATOS_APP_NAME:
            Human-readable application name. Defaults to 'ATOS'.

        ATOS_ENV:
            Runtime environment. Defaults to 'development'.

        ATOS_DEBUG:
            Boolean debug flag. Defaults to false.

        ATOS_LOG_LEVEL:
            Log level. Defaults to 'INFO'.

    Returns:
        AppSettings:
            Immutable validated application settings.

    Raises:
        InvalidConfigurationValueError:
            If a setting is present but invalid.
    """
    source = environ if environ is not None else os.environ

    app_name = _read_app_name(source)
    environment = _read_environment(source)
    debug = _read_debug(source)
    log_level = _read_log_level(source)

    if environment == RuntimeEnvironment.PRODUCTION and debug:
        raise InvalidConfigurationValueError(
            "ATOS_DEBUG must not be enabled in production."
        )

    return AppSettings(
        app_name=app_name,
        environment=environment,
        debug=debug,
        log_level=log_level,
    )


def _read_app_name(environ: Mapping[str, str]) -> str:
    """
    Read and validate the ATOS application name.
    """
    raw_value = environ.get("ATOS_APP_NAME", DEFAULT_APP_NAME)

    if not isinstance(raw_value, str) or not raw_value.strip():
        raise InvalidConfigurationValueError(
            "ATOS_APP_NAME must be a non-empty string."
        )

    return raw_value.strip()


def _read_environment(environ: Mapping[str, str]) -> RuntimeEnvironment:
    """
    Read and validate the ATOS runtime environment.
    """
    raw_value = environ.get("ATOS_ENV", DEFAULT_ENVIRONMENT.value)

    return RuntimeEnvironment.from_value(raw_value)


def _read_debug(environ: Mapping[str, str]) -> bool:
    """
    Read and validate the ATOS debug flag.
    """
    raw_value = environ.get("ATOS_DEBUG")

    if raw_value is None:
        return DEFAULT_DEBUG

    if not isinstance(raw_value, str) or not raw_value.strip():
        raise InvalidConfigurationValueError(
            "ATOS_DEBUG must be a valid boolean string."
        )

    normalized_value = raw_value.strip().lower()

    if normalized_value in TRUE_VALUES:
        return True

    if normalized_value in FALSE_VALUES:
        return False

    raise InvalidConfigurationValueError(
        "ATOS_DEBUG must be one of: "
        f"{', '.join(sorted(TRUE_VALUES | FALSE_VALUES))}."
    )


def _read_log_level(environ: Mapping[str, str]) -> str:
    """
    Read and validate the ATOS log level.
    """
    raw_value = environ.get("ATOS_LOG_LEVEL", DEFAULT_LOG_LEVEL)

    if not isinstance(raw_value, str) or not raw_value.strip():
        raise InvalidConfigurationValueError(
            "ATOS_LOG_LEVEL must be a non-empty string."
        )

    normalized_value = raw_value.strip().upper()

    if normalized_value not in VALID_LOG_LEVELS:
        raise InvalidConfigurationValueError(
            "ATOS_LOG_LEVEL must be one of: "
            f"{', '.join(sorted(VALID_LOG_LEVELS))}."
        )

    return normalized_value