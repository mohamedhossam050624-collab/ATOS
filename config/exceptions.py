from __future__ import annotations


class ConfigurationError(Exception):
    """
    Base exception for all configuration-related errors.

    All Configuration Domain errors must inherit from this class so they can be
    handled consistently by the Kernel, startup process, APIs, tests, and future
    deployment tooling.
    """


class ConfigurationLoadError(ConfigurationError):
    """
    Raised when configuration cannot be loaded from a configured source.
    """


class ConfigurationValidationError(ConfigurationError):
    """
    Raised when loaded configuration fails validation rules.
    """


class MissingConfigurationValueError(ConfigurationValidationError):
    """
    Raised when a required configuration value is missing.
    """


class InvalidConfigurationValueError(ConfigurationValidationError):
    """
    Raised when a configuration value exists but has an invalid format or value.
    """


class MissingSecretError(MissingConfigurationValueError):
    """
    Raised when a required secret is missing.

    Secret values must never be hardcoded in source code.
    They must come from approved configuration sources such as environment
    variables or future secret-management integrations.
    """


class UnsupportedEnvironmentError(ConfigurationValidationError):
    """
    Raised when an unsupported runtime environment is configured.
    """


class ConfigurationSourceError(ConfigurationError):
    """
    Raised when a configuration source is unavailable, malformed, or unsafe.
    """