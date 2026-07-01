from __future__ import annotations

from enum import Enum

from config.exceptions import UnsupportedEnvironmentError


class RuntimeEnvironment(str, Enum):
    """
    Supported ATOS runtime environments.

    These values are intentionally stable because they may be used later in:
    - Configuration loading
    - Logging behavior
    - Security policies
    - Feature flags
    - Deployment pipelines
    - Testing isolation
    """

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

    @classmethod
    def from_value(cls, value: str) -> "RuntimeEnvironment":
        """
        Create a RuntimeEnvironment from a raw string value.

        The input is normalized to support safe parsing from environment
        variables such as ATOS_ENV.

        Raises:
            UnsupportedEnvironmentError: If the value does not match a
            supported runtime environment.
        """
        if not isinstance(value, str) or not value.strip():
            raise UnsupportedEnvironmentError(
                "Runtime environment must be a non-empty string."
            )

        normalized_value = value.strip().lower()

        for environment in cls:
            if environment.value == normalized_value:
                return environment

        supported_values = ", ".join(environment.value for environment in cls)

        raise UnsupportedEnvironmentError(
            f"Unsupported runtime environment '{value}'. "
            f"Supported environments: {supported_values}."
        )

    @property
    def is_local(self) -> bool:
        """
        Return True for local developer-oriented environments.
        """
        return self in {
            RuntimeEnvironment.DEVELOPMENT,
            RuntimeEnvironment.TESTING,
        }

    @property
    def is_deployed(self) -> bool:
        """
        Return True for deployed runtime environments.
        """
        return self in {
            RuntimeEnvironment.STAGING,
            RuntimeEnvironment.PRODUCTION,
        }

    @property
    def is_production(self) -> bool:
        """
        Return True only for the production environment.
        """
        return self == RuntimeEnvironment.PRODUCTION