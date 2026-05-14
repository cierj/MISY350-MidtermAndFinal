import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class User:
    id: str
    username: str
    email: str
    password: str
    role: str = "Child"
    children: List[str] = field(default_factory=list)

    @property
    def identifier(self) -> str:
        return self.username or self.email

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "User":
        return cls(
            id=payload.get("id", ""),
            username=payload.get("username", ""),
            email=payload.get("email", ""),
            password=payload.get("password", ""),
            role=payload.get("role", "Child"),
            children=payload.get("children", []) or [],
        )


@dataclass
class JournalEntry:
    date: str
    time: str
    feeling: str
    breathing: str
    notes: str = ""

    @property
    def key(self) -> str:
        return f"{self.date} {self.time}"

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "JournalEntry":
        date = payload.get("date", "") or ""
        time = payload.get("time", "") or ""
        if not date and time and len(time) >= 10 and time[4] == "-" and time[7] == "-":
            date = time[:10]
            if len(time) > 10 and time[10] == " ":
                time = time[11:]

        return cls(
            date=date,
            time=time,
            feeling=payload.get("feeling", ""),
            breathing=str(payload.get("breathing", "")),
            notes=payload.get("notes", ""),
        )


class UserStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = path or Path("users.json")
        self.users = self._load_users()

    def _load_users(self) -> List[User]:
        if not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8") as handle:
            try:
                payload = json.load(handle)
            except json.JSONDecodeError:
                return []

        return [User.from_dict(item) for item in payload if isinstance(item, dict)]

    def _save_users(self) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump([user.to_dict() for user in self.users], handle, indent=4)

    def add_user(self, user: User) -> None:
        self.users.append(user)
        self._save_users()

    def update_user(self, user: User) -> None:
        for index, existing in enumerate(self.users):
            if existing.id == user.id:
                self.users[index] = user
                self._save_users()
                return
        self.add_user(user)

    def find_user_by_login(self, login_value: str) -> Optional[User]:
        login_lower = login_value.strip().lower()
        for user in self.users:
            if user.username.lower() == login_lower or user.email.lower() == login_lower:
                return user
        return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return next((user for user in self.users if user.id == user_id), None)

    def get_user_by_identifier(self, identifier: str) -> Optional[User]:
        identifier_lower = identifier.strip().lower()
        return next(
            (
                user
                for user in self.users
                if user.username.lower() == identifier_lower or user.email.lower() == identifier_lower
            ),
            None,
        )

    def get_child_user(self, child_id: str) -> Optional[User]:
        child_lower = child_id.strip().lower()
        return next(
            (user for user in self.users if user.username.lower() == child_lower or user.email.lower() == child_lower),
            None,
        )


class JournalStore:
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path(".")

    def _journal_file(self, username: str) -> Path:
        safe_name = username.replace("/", "_").replace("\\", "_")
        return self.base_path / f"journal_{safe_name}.json"

    def load_journal(self, username: str) -> Dict[str, Dict[str, str]]:
        journal_path = self._journal_file(username)
        if not journal_path.exists():
            return {}

        with journal_path.open("r", encoding="utf-8") as handle:
            try:
                payload = json.load(handle)
            except json.JSONDecodeError:
                return {}

        return payload if isinstance(payload, dict) else {}

    def save_journal(self, username: str, journal_data: Dict[str, Dict[str, str]]) -> None:
        journal_path = self._journal_file(username)
        with journal_path.open("w", encoding="utf-8") as handle:
            json.dump(journal_data, handle, indent=4)
