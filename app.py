"""Main application entry point for Breeze Buddy."""

from config import get_settings
from utils import setup_logging
from utils.logging import get_logger

from Data.ai_store import ChatStore
from Data.journal_store import JournalStore, UserStore
from Services.ai_manager import AIService
from Services.journal_manager import AuthService, JournalService
from UI.breath_dashboard import run_app

logger = get_logger(__name__)


def main() -> None:
    """Initialize and run the Breeze Buddy application."""
    # Load configuration
    settings = get_settings()

    # Setup logging
    setup_logging(
        level=settings.log_level,
        log_file=settings.log_file
    )

    logger.info("Starting Breeze Buddy application")
    logger.info(f"Environment: {settings.environment}")

    try:
        # Initialize data stores
        user_store = UserStore()
        journal_store = JournalStore()
        chat_store = ChatStore()

        # Initialize services
        auth_service = AuthService(user_store)
        journal_service = JournalService(journal_store)
        ai_service = AIService(chat_store)

        # Run the application
        run_app(auth_service, journal_service, ai_service)

    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        raise


if __name__ == "__main__":
    main()
