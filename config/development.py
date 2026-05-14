"""Development environment configuration."""

from .settings import Settings


def get_development_settings() -> Settings:
    """Get settings optimized for development environment."""
    return Settings(
        environment="development",
        log_level="DEBUG",
        openai_max_tokens=500,  # Higher limit for development testing
    )