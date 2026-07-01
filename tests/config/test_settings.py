from __future__ import annotations

import pytest

from config.environment import RuntimeEnvironment
from config.exceptions import (
    InvalidConfigurationValueError,
    UnsupportedEnvironmentError,
)
from config.settings import AppSettings, load_settings


def test_load_settings_uses_safe_defaults() -> None:
    """
    Ensure settings load safe defaults when no environment variables are set.
    """
    settings = load_settings(environ={})

    assert isinstance(settings, AppSettings)
    assert settings.app_name == "ATOS"
    assert settings.environment == RuntimeEnvironment.DEVELOPMENT
    assert settings.debug is False
    assert settings.log_level == "INFO"


def test_load_settings_reads_app_name() -> None:
    """
    Ensure ATOS_APP_NAME is loaded and normalized.
    """
    settings = load_settings(
        environ={
            "ATOS_APP_NAME": "  ATOS Local  ",
        }
    )

    assert settings.app_name == "ATOS Local"


def test_load_settings_rejects_empty_app_name() -> None:
    """
    Ensure empty ATOS_APP_NAME values are rejected.
    """
    with pytest.raises(InvalidConfigurationValueError):
        load_settings(
            environ={
                "ATOS_APP_NAME": "   ",
            }
        )


def test_load_settings_reads_runtime_environment() -> None:
    """
    Ensure ATOS_ENV is loaded correctly.
    """
    settings = load_settings(
        environ={
            "ATOS_ENV": "testing",
        }
    )

    assert settings.environment == RuntimeEnvironment.TESTING
    assert settings.is_testing is True


def test_load_settings_rejects_invalid_runtime_environment() -> None:
    """
    Ensure unsupported ATOS_ENV values are rejected.
    """
    with pytest.raises(UnsupportedEnvironmentError):
        load_settings(
            environ={
                "ATOS_ENV": "local",
            }
        )


@pytest.mark.parametrize(
    "raw_value",
    ["1", "true", "TRUE", "yes", "y", "on"],
)
def test_load_settings_accepts_true_debug_values(raw_value: str) -> None:
    """
    Ensure valid true debug values are parsed correctly.
    """
    settings = load_settings(
        environ={
            "ATOS_DEBUG": raw_value,
        }
    )

    assert settings.debug is True


@pytest.mark.parametrize(
    "raw_value",
    ["0", "false", "FALSE", "no", "n", "off"],
)
def test_load_settings_accepts_false_debug_values(raw_value: str) -> None:
    """
    Ensure valid false debug values are parsed correctly.
    """
    settings = load_settings(
        environ={
            "ATOS_DEBUG": raw_value,
        }
    )

    assert settings.debug is False


def test_load_settings_rejects_invalid_debug_value() -> None:
    """
    Ensure invalid ATOS_DEBUG values are rejected.
    """
    with pytest.raises(InvalidConfigurationValueError):
        load_settings(
            environ={
                "ATOS_DEBUG": "maybe",
            }
        )


def test_load_settings_rejects_empty_debug_value() -> None:
    """
    Ensure empty ATOS_DEBUG values are rejected.
    """
    with pytest.raises(InvalidConfigurationValueError):
        load_settings(
            environ={
                "ATOS_DEBUG": "   ",
            }
        )


@pytest.mark.parametrize(
    "raw_value, expected",
    [
        ("trace", "TRACE"),
        ("debug", "DEBUG"),
        ("info", "INFO"),
        ("success", "SUCCESS"),
        ("warning", "WARNING"),
        ("error", "ERROR"),
        ("critical", "CRITICAL"),
    ],
)
def test_load_settings_accepts_valid_log_levels(
    raw_value: str,
    expected: str,
) -> None:
    """
    Ensure valid ATOS_LOG_LEVEL values are accepted and normalized.
    """
    settings = load_settings(
        environ={
            "ATOS_LOG_LEVEL": raw_value,
        }
    )

    assert settings.log_level == expected


def test_load_settings_rejects_invalid_log_level() -> None:
    """
    Ensure invalid ATOS_LOG_LEVEL values are rejected.
    """
    with pytest.raises(InvalidConfigurationValueError):
        load_settings(
            environ={
                "ATOS_LOG_LEVEL": "LOUD",
            }
        )


def test_load_settings_rejects_empty_log_level() -> None:
    """
    Ensure empty ATOS_LOG_LEVEL values are rejected.
    """
    with pytest.raises(InvalidConfigurationValueError):
        load_settings(
            environ={
                "ATOS_LOG_LEVEL": "   ",
            }
        )


def test_debug_must_not_be_enabled_in_production() -> None:
    """
    Ensure production mode rejects debug=True.
    """
    with pytest.raises(InvalidConfigurationValueError):
        load_settings(
            environ={
                "ATOS_ENV": "production",
                "ATOS_DEBUG": "true",
            }
        )


def test_settings_environment_flags() -> None:
    """
    Ensure AppSettings exposes correct environment helpers.
    """
    development_settings = load_settings(
        environ={
            "ATOS_ENV": "development",
        }
    )
    testing_settings = load_settings(
        environ={
            "ATOS_ENV": "testing",
        }
    )
    production_settings = load_settings(
        environ={
            "ATOS_ENV": "production",
        }
    )

    assert development_settings.is_development is True
    assert development_settings.is_testing is False
    assert development_settings.is_production is False

    assert testing_settings.is_development is False
    assert testing_settings.is_testing is True
    assert testing_settings.is_production is False

    assert production_settings.is_development is False
    assert production_settings.is_testing is False
    assert production_settings.is_production is True