import uuid
from datetime import datetime
from typing import List, Optional

from werkzeug.security import check_password_hash, generate_password_hash

from Data.journal_store import JournalEntry, JournalStore, User, UserStore


class AuthService:
    def __init__(self, user_store: UserStore):
        self._user_store = user_store

    def authenticate(self, login_value: str, password: str) -> Optional[User]:
        user = self._user_store.find_user_by_login(login_value)
        if user and check_password_hash(user.password, password):
            return user
        return None

    def register(self, username: str, email: str, password: str, role: str) -> User:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        if self._user_store.find_user_by_login(username) is not None:
            raise ValueError("Username already taken")

        if self._user_store.find_user_by_login(email) is not None:
            raise ValueError("Email already registered")

        user = User(
            id=str(uuid.uuid4()),
            username=username.strip().lower(),
            email=email.strip().lower(),
            password=generate_password_hash(password),
            role=role,
        )
        self._user_store.add_user(user)
        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self._user_store.get_user_by_id(user_id)

    def find_user_by_identifier(self, identifier: str) -> Optional[User]:
        return self._user_store.get_user_by_identifier(identifier)

    def link_child(self, parent_user: User, child_login: str) -> User:
        child_user = self._user_store.find_user_by_login(child_login)
        if child_user is None or child_user.role.lower() != "child":
            raise ValueError("Child account not found or not a child account")

        child_id = child_user.identifier
        if child_id in parent_user.children:
            raise ValueError("Child already linked")

        parent_user.children.append(child_id)
        self._user_store.update_user(parent_user)
        return parent_user


class JournalService:
    def __init__(self, journal_store: JournalStore):
        self._journal_store = journal_store

    def list_entries(self, username: str) -> List[JournalEntry]:
        journal_data = self._journal_store.load_journal(username)
        entries = [JournalEntry.from_dict(payload) for _, payload in sorted(journal_data.items(), reverse=True)]
        return entries

    def has_entry_today(self, username: str) -> bool:
        journal_data = self._journal_store.load_journal(username)
        today = datetime.now().strftime("%Y-%m-%d")
        return any(key.startswith(today) for key in journal_data.keys())

    def add_entry(self, username: str, feeling: str, breathing: int, notes: str) -> JournalEntry:
        now = datetime.now()
        entry = JournalEntry(
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S"),
            feeling=feeling,
            breathing=str(breathing),
            notes=notes or ""
        )
        journal_data = self._journal_store.load_journal(username)
        journal_data[entry.key] = entry.to_dict()
        self._journal_store.save_journal(username, journal_data)
        return entry
