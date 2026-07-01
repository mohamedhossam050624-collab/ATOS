from __future__ import annotations

import pytest

from config.environment import RuntimeEnvironment
from config.exceptions import UnsupportedEnvironmentError


def test_runtime_environment_values_are_stable() -> None:
    """
    Ensure runtime environment values remain stable.

    These values may be used later in configuration files, deployment pipelines,
    logs, feature flags, and environment-specific behavior.
    """
    assert RuntimeEnvironment.DEVELOPMENT.value == "development"
    assert RuntimeEnvironment.TESTING.value == "testing"
    assert RuntimeEnvironment.STAGING.value == "staging"
    assert RuntimeEnvironment.PRODUCTION.value == "production"


def test_from_value_accepts_supported_environments() -> None:
    """
    Ensure supported environment strings are parsed correctly.
    """
    assert RuntimeEnvironment.from_value("development") == RuntimeEnvironment.DEVELOPMENT
    assert RuntimeEnvironment.from_value("testing") == RuntimeEnvironment.TESTING
    assert RuntimeEnvironment.from_value("staging") == RuntimeEnvironment.STAGING
    assert RuntimeEnvironment.from_value("production") == RuntimeEnvironment.PRODUCTION


def test_from_value_normalizes_case_and_whitespace() -> None:
    """
    Ensure environment values are normalized before parsing.
    """
    assert RuntimeEnvironment.from_value(" DEVELOPMENT ") == RuntimeEnvironment.DEVELOPMENT
    assert RuntimeEnvironment.from_value("Testing") == RuntimeEnvironment.TESTING
    assert RuntimeEnvironment.from_value(" STAGING ") == RuntimeEnvironment.STAGING
    assert RuntimeEnvironment.from_value("Production") == RuntimeEnvironment.PRODUCTION


def test_from_value_rejects_empty_environment() -> None:
    """
    Ensure empty environment values are rejected.
    """
    with pytest.raises(UnsupportedEnvironmentError):
        RuntimeEnvironment.from_value("")


def test_from_value_rejects_unsupported_environment() -> None:
    """
    Ensure unsupported environment values are rejected.
    """
    with pytest.raises(UnsupportedEnvironmentError):
        RuntimeEnvironment.from_value("local")


def test_local_environment_flags() -> None:
    """
    Ensure local environment flags are correct.
    """
    assert RuntimeEnvironment.DEVELOPMENT.is_local is True
    assert RuntimeEnvironment.TESTING.is_local is True
    assert RuntimeEnvironment.STAGING.is_local is False
    assert RuntimeEnvironment.PRODUCTION.is_local is False


def test_deployed_environment_flags() -> None:
    """
    Ensure deployed environment flags are correct.
    """
    assert RuntimeEnvironment.DEVELOPMENT.is_deployed is False
    assert RuntimeEnvironment.TESTING.is_deployed is False
    assert RuntimeEnvironment.STAGING.is_deployed is True
    assert RuntimeEnvironment.PRODUCTION.is_deployed is True


def test_production_environment_flag() -> None:
    """
    Ensure only production is marked as production.
    """
    assert RuntimeEnvironment.DEVELOPMENT.is_production is False
    assert RuntimeEnvironment.TESTING.is_production is False
    assert RuntimeEnvironment.STAGING.is_production is False
    assert RuntimeEnvironment.PRODUCTION.is_production is True