"""Journal and authentication services for Breeze Buddy."""

import uuid
from datetime import datetime
from typing import List, Optional

from werkzeug.security import check_password_hash, generate_password_hash

from utils.exceptions import AuthenticationError, ValidationError
from utils.logging import get_logger
from Data.journal_store import JournalEntry, JournalStore, User, UserStore

logger = get_logger(__name__)


class AuthService:
    """Service for handling user authentication and registration."""

    def __init__(self, user_store: UserStore) -> None:
        """Initialize auth service with user store.

        Args:
            user_store: User data store
        """
        self._user_store = user_store

    def authenticate(self, login_value: str, password: str) -> Optional[User]:
        """Authenticate a user with login credentials.

        Args:
            login_value: Username or email
            password: User password

        Returns:
            User object if authentication successful, None otherwise

        Raises:
            AuthenticationError: If authentication fails due to system error
        """
        try:
            user = self._user_store.find_user_by_login(login_value)
            if user and check_password_hash(user.password, password):
                logger.info(f"User {user.username} authenticated successfully")
                return user
            logger.warning(f"Failed authentication attempt for: {login_value}")
            return None
        except Exception as e:
            logger.error(f"Authentication error for {login_value}: {e}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    def register(self, username: str, email: str, password: str, role: str) -> User:
        """Register a new user.

        Args:
            username: Desired username
            email: User email
            password: User password
            role: User role (Parent/Child)

        Returns:
            Created user object

        Raises:
            ValidationError: If registration data is invalid
        """
        try:
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters")

            if self._user_store.find_user_by_login(username) is not None:
                raise ValidationError("Username already taken")

            if self._user_store.find_user_by_login(email) is not None:
                raise ValidationError("Email already registered")

            user = User(
                id=str(uuid.uuid4()),
                username=username.strip().lower(),
                email=email.strip().lower(),
                password=generate_password_hash(password),
                role=role,
            )
            self._user_store.add_user(user)
            logger.info(f"New user registered: {username} ({role})")
            return user
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Registration error for {username}: {e}")
            raise ValidationError(f"Registration failed: {str(e)}")

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        try:
            return self._user_store.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None

    def find_user_by_identifier(self, identifier: str) -> Optional[User]:
        """Find user by username or email.

        Args:
            identifier: Username or email

        Returns:
            User object if found, None otherwise
        """
        try:
            return self._user_store.get_user_by_identifier(identifier)
        except Exception as e:
            logger.error(f"Error finding user by identifier {identifier}: {e}")
            return None

    def link_child(self, parent_user: User, child_login: str) -> User:
        """Link a child account to a parent.

        Args:
            parent_user: Parent user object
            child_login: Child username or email

        Returns:
            Child user object

        Raises:
            ValidationError: If linking fails
        """
        try:
            child_user = self._user_store.find_user_by_login(child_login)
            if child_user is None or child_user.role.lower() != "child":
                raise ValidationError("Child account not found or not a child account")

            # Update parent user with child link
            if child_user.identifier not in parent_user.children:
                parent_user.children.append(child_user.identifier)
                # Note: This assumes the user store handles updating the user
                logger.info(f"Linked child {child_user.username} to parent {parent_user.username}")

            return child_user
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error linking child {child_login} to parent {parent_user.username}: {e}")
            raise ValidationError(f"Failed to link child account: {str(e)}")

        child_id = child_user.identifier
        if child_id in parent_user.children:
            raise ValueError("Child already linked")

        parent_user.children.append(child_id)
        self._user_store.update_user(parent_user)
        return parent_user


class JournalService:
    """Service for managing journal entries."""

    def __init__(self, journal_store: JournalStore) -> None:
        """Initialize journal service with journal store.

        Args:
            journal_store: Journal data store
        """
        self._journal_store = journal_store

    def list_entries(self, username: str) -> List[JournalEntry]:
        """List all journal entries for a user.

        Args:
            username: User's identifier

        Returns:
            List of journal entries sorted by date (newest first)
        """
        try:
            journal_data = self._journal_store.load_journal(username)
            entries = [
                JournalEntry.from_dict(payload)
                for _, payload in sorted(journal_data.items(), reverse=True)
            ]
            logger.debug(f"Retrieved {len(entries)} entries for {username}")
            return entries
        except Exception as e:
            logger.error(f"Error listing entries for {username}: {e}")
            return []

    def has_entry_today(self, username: str) -> bool:
        """Check if user has a journal entry for today.

        Args:
            username: User's identifier

        Returns:
            True if entry exists for today, False otherwise
        """
        try:
            journal_data = self._journal_store.load_journal(username)
            today = datetime.now().strftime("%Y-%m-%d")
            has_entry = any(key.startswith(today) for key in journal_data.keys())
            logger.debug(f"User {username} has entry today: {has_entry}")
            return has_entry
        except Exception as e:
            logger.error(f"Error checking today's entry for {username}: {e}")
            return False

    def add_entry(self, username: str, feeling: str, breathing: int, notes: str) -> JournalEntry:
        """Add a new journal entry for a user.

        Args:
            username: User's identifier
            feeling: User's feeling description
            breathing: Breathing quality rating (1-10)
            notes: Additional notes

        Returns:
            Created journal entry

        Raises:
            ValidationError: If entry data is invalid
        """
        try:
            # Validate input
            if not feeling or not feeling.strip():
                raise ValidationError("Feeling is required")

            if not isinstance(breathing, int) or breathing < 1 or breathing > 10:
                raise ValidationError("Breathing must be an integer between 1 and 10")

            now = datetime.now()
            entry = JournalEntry(
                date=now.strftime("%Y-%m-%d"),
                time=now.strftime("%H:%M:%S"),
                feeling=feeling.strip(),
                breathing=str(breathing),
                notes=notes.strip() if notes else ""
            )

            journal_data = self._journal_store.load_journal(username)
            journal_data[entry.key] = entry.to_dict()
            self._journal_store.save_journal(username, journal_data)

            logger.info(f"Added journal entry for {username}: {feeling}")
            return entry

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error adding journal entry for {username}: {e}")
            raise ValidationError(f"Failed to add journal entry: {str(e)}")
