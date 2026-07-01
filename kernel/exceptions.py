from __future__ import annotations


class KernelError(Exception):
    """
    Base exception for all Kernel-related errors.

    All Kernel exceptions should inherit from this class so they can be
    caught and handled consistently at the platform boundary.
    """


class KernelStartupError(KernelError):
    """
    Raised when the Kernel fails during startup.
    """


class KernelShutdownError(KernelError):
    """
    Raised when the Kernel fails during shutdown.
    """


class ServiceError(KernelError):
    """
    Base exception for all service-related Kernel errors.
    """


class ServiceRegistrationError(ServiceError):
    """
    Raised when a service cannot be registered in the service registry.
    """


class ServiceAlreadyRegisteredError(ServiceRegistrationError):
    """
    Raised when attempting to register a service that already exists.
    """


class ServiceNotFoundError(ServiceError):
    """
    Raised when a requested service does not exist in the service registry.
    """


class ServiceStartupError(ServiceError):
    """
    Raised when a service fails during initialization or startup.
    """


class ServiceShutdownError(ServiceError):
    """
    Raised when a service fails during shutdown.
    """


class InvalidServiceStateError(ServiceError):
    """
    Raised when a service receives an invalid lifecycle state transition.
    """


class DependencyResolutionError(KernelError):
    """
    Raised when Kernel dependencies cannot be resolved.
    """