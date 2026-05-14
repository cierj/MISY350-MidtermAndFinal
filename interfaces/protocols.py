"""Protocol definitions for Breeze Buddy services and stores."""

from abc import ABC, abstractmethod
from typing import List, Optional, Protocol

from Data.journal_store import JournalEntry, User


class UserStoreProtocol(Protocol):
    """Protocol for user data storage operations."""

    def add_user(self, user: User) -> None:
        """Add a new user to storage."""
        ...

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        ...

    def get_user_by_identifier(self, identifier: str) -> Optional[User]:
        """Get user by username or email."""
        ...

    def find_user_by_login(self, login_value: str) -> Optional[User]:
        """Find user by username or email for login."""
        ...


class JournalStoreProtocol(Protocol):
    """Protocol for journal data storage operations."""

    def add_entry(self, entry: JournalEntry) -> None:
        """Add a new journal entry."""
        ...

    def get_entries(self, user_identifier: str) -> List[JournalEntry]:
        """Get all entries for a user."""
        ...

    def has_entry_today(self, user_identifier: str) -> bool:
        """Check if user has an entry for today."""
        ...


class ChatStoreProtocol(Protocol):
    """Protocol for chat history storage operations."""

    def load_chat(self, username: str) -> List:
        """Load chat history for a user."""
        ...

    def append_message(self, username: str, message) -> None:
        """Append a message to user's chat history."""
        ...

    def clear_chat_history(self, username: str) -> None:
        """Clear chat history for a user."""
        ...


class AuthServiceProtocol(Protocol):
    """Protocol for authentication service operations."""

    def authenticate(self, login_value: str, password: str) -> Optional[User]:
        """Authenticate a user with login credentials."""
        ...

    def register(self, username: str, email: str, password: str, role: str) -> User:
        """Register a new user."""
        ...

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        ...

    def find_user_by_identifier(self, identifier: str) -> Optional[User]:
        """Find user by identifier."""
        ...

    def link_child(self, parent_user: User, child_login: str) -> User:
        """Link a child account to a parent."""
        ...


class JournalServiceProtocol(Protocol):
    """Protocol for journal service operations."""

    def add_entry(self, user_identifier: str, feeling: str, breathing: int, notes: str) -> JournalEntry:
        """Add a new journal entry."""
        ...

    def list_entries(self, user_identifier: str) -> List[JournalEntry]:
        """List all entries for a user."""
        ...

    def has_entry_today(self, user_identifier: str) -> bool:
        """Check if user has entry today."""
        ...