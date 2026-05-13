from Data.ai_store import ChatStore
from Data.journal_store import JournalStore, UserStore
from Services.ai_manager import AIService
from Services.journal_manager import AuthService, JournalService
from UI.breath_dashboard import run_app


def main():
    user_store = UserStore()
    journal_store = JournalStore()
    chat_store = ChatStore()

    auth_service = AuthService(user_store)
    journal_service = JournalService(journal_store)
    ai_service = AIService(chat_store)

    run_app(auth_service, journal_service, ai_service)


if __name__ == "__main__":
    main()
