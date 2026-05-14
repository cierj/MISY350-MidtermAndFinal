"""Production environment configuration."""

from .settings import Settings


def get_production_settings() -> Settings:
    """Get settings optimized for production environment."""
    return Settings(
        environment="production",
        log_level="WARNING",
        # In production, ensure all required settings are provided via environment
    )