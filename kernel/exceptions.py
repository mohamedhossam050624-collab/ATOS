class KernelError(Exception):
    """Base exception for the kernel."""


class ServiceAlreadyRegisteredError(KernelError):
    """Raised when attempting to register a duplicate service."""


class ServiceNotFoundError(KernelError):
    """Raised when a service cannot be found."""


class ServiceStartupError(KernelError):
    """Raised when a service fails during startup."""


class ServiceShutdownError(KernelError):
    """Raised when a service fails during shutdown."""