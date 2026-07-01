from __future__ import annotations

from kernel.exceptions import (
    DependencyResolutionError,
    InvalidServiceStateError,
    KernelError,
    KernelShutdownError,
    KernelStartupError,
    ServiceAlreadyRegisteredError,
    ServiceError,
    ServiceNotFoundError,
    ServiceRegistrationError,
    ServiceShutdownError,
    ServiceStartupError,
)


def test_kernel_errors_inherit_from_kernel_error() -> None:
    """
    Ensure Kernel-level errors inherit from KernelError.
    """
    assert issubclass(KernelStartupError, KernelError)
    assert issubclass(KernelShutdownError, KernelError)
    assert issubclass(DependencyResolutionError, KernelError)


def test_service_errors_inherit_from_service_error() -> None:
    """
    Ensure service-level errors inherit from ServiceError.
    """
    assert issubclass(ServiceRegistrationError, ServiceError)
    assert issubclass(ServiceAlreadyRegisteredError, ServiceError)
    assert issubclass(ServiceNotFoundError, ServiceError)
    assert issubclass(ServiceStartupError, ServiceError)
    assert issubclass(ServiceShutdownError, ServiceError)
    assert issubclass(InvalidServiceStateError, ServiceError)


def test_service_error_inherits_from_kernel_error() -> None:
    """
    Ensure all service errors are also Kernel errors.
    """
    assert issubclass(ServiceError, KernelError)


def test_service_already_registered_error_inherits_from_registration_error() -> None:
    """
    Ensure duplicate registration errors are a specialized registration error.
    """
    assert issubclass(ServiceAlreadyRegisteredError, ServiceRegistrationError)


def test_exception_message_is_preserved() -> None:
    """
    Ensure exception messages are preserved.
    """
    error = ServiceStartupError("Startup failed.")

    assert str(error) == "Startup failed."