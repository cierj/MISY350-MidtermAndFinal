"""Custom exception classes for Breeze Buddy application."""


class BreezeBuddyError(Exception):
    """Base exception class for Breeze Buddy application."""

    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class AuthenticationError(BreezeBuddyError):
    """Raised when authentication fails."""
    pass


class ValidationError(BreezeBuddyError):
    """Raised when input validation fails."""
    pass


class DataAccessError(BreezeBuddyError):
    """Raised when data access operations fail."""
    pass


class AIServiceError(BreezeBuddyError):
    """Raised when AI service operations fail."""
    pass


class ConfigurationError(BreezeBuddyError):
    """Raised when configuration is invalid."""
    pass