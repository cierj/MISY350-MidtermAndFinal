from Data.journal_store import JournalStore, UserStore
from Services.journal_manager import AuthService, JournalService
from UI.breath_dashboard import run_app


def main():
    user_store = UserStore()
    journal_store = JournalStore()
    auth_service = AuthService(user_store)
    journal_service = JournalService(journal_store)

    run_app(auth_service, journal_service)


if __name__ == "__main__":
    main()
