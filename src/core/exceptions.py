"""
Custom exceptions for the Editorial PR Matchmaking platform.

These exceptions provide clear, typed error handling throughout the application.
Routers convert these to appropriate HTTP responses.
"""


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, detail: str | None = None):
        self.message = message
        self.detail = detail or message
        super().__init__(self.message)


# --- Authentication & Authorization ---


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    pass


class AuthorizationError(AppException):
    """Raised when user lacks permission for an action."""

    pass


# --- Resource Errors ---


class NotFoundError(AppException):
    """Raised when a requested resource doesn't exist."""

    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(message)
        self.resource = resource
        self.identifier = identifier


class AlreadyExistsError(AppException):
    """Raised when attempting to create a resource that already exists."""

    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} already exists"
        if identifier:
            message = f"{resource} '{identifier}' already exists"
        super().__init__(message)
        self.resource = resource
        self.identifier = identifier


class ValidationError(AppException):
    """Raised when input validation fails beyond Pydantic."""

    pass


# --- Profile-specific Errors ---


class ProfileNotFoundError(NotFoundError):
    """Raised when a profile doesn't exist."""

    def __init__(self, profile_type: str, identifier: str | None = None):
        super().__init__(f"{profile_type} profile", identifier)
        self.profile_type = profile_type


class ProfileExistsError(AlreadyExistsError):
    """Raised when a profile already exists for a user."""

    def __init__(self, profile_type: str):
        super().__init__(f"{profile_type} profile")
        self.profile_type = profile_type


# --- External Service Errors ---


class ExternalServiceError(AppException):
    """Raised when an external service (LLM, embedding model) fails."""

    def __init__(self, service: str, message: str):
        super().__init__(f"{service} error: {message}")
        self.service = service
