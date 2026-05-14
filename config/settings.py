"""Application settings and configuration management."""

import os
from pathlib import Path
from typing import Optional

# Try to load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Settings:
    """Main application settings with validation."""

    def __init__(self):
        """Initialize settings from environment variables."""
        # Environment
        self.environment = os.getenv("ENVIRONMENT", "development")

        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        try:
            self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        except ValueError:
            self.openai_temperature = 0.7
        
        try:
            self.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "250"))
        except ValueError:
            self.openai_max_tokens = 250

        # Data Storage
        data_dir = os.getenv("DATA_DIRECTORY", ".")
        self.data_directory = Path(data_dir)
        self.users_file = os.getenv("USERS_FILE", "users.json")
        self.journal_file = os.getenv("JOURNAL_FILE", "journal.json")
        self.journal_child_file = os.getenv("JOURNAL_CHILD_FILE", "journal_child.json")

        # Application Settings
        self.app_title = os.getenv("APP_TITLE", "Breeze Buddy - Your Asthma Companion")
        self.app_icon = os.getenv("APP_ICON", "🌬️")

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", None)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance.
    
    Returns:
        Settings instance with all configuration values
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment.
    
    Returns:
        Newly created Settings instance
    """
    global _settings
    _settings = Settings()
    return _settings