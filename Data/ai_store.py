"""AI data storage and OpenAI client management."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import get_settings

# Initialize OpenAI client lazily when needed
_OPENAI_CLIENT = None


def get_openai_client():
    """Get or create the OpenAI client.
    
    Returns:
        OpenAI client instance
        
    Raises:
        ImportError: If OpenAI client cannot be created due to missing credentials
    """
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is None:
        try:
            from openai import OpenAI
            settings = get_settings()
            if not settings.openai_api_key:
                # Create a client without validation for development/testing
                _OPENAI_CLIENT = None
                return None
            _OPENAI_CLIENT = OpenAI(api_key=settings.openai_api_key)
        except Exception as e:
            raise ImportError(f"Failed to initialize OpenAI client: {e}")
    return _OPENAI_CLIENT


# For backward compatibility, create an alias
OPENAI_CLIENT = None



@dataclass
class ChatMessage:
    role: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ChatMessage":
        return cls(role=payload.get("role", "user"), content=payload.get("content", ""))


class ChatStore:
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path(".")

    def _chat_file(self, username: str) -> Path:
        safe_name = username.replace("/", "_").replace("\\", "_")
        return self.base_path / f"chat_history_{safe_name}.json"

    def load_chat(self, username: str) -> List[ChatMessage]:
        chat_path = self._chat_file(username)
        if not chat_path.exists():
            return []

        with chat_path.open("r", encoding="utf-8") as handle:
            try:
                payload = json.load(handle)
            except json.JSONDecodeError:
                return []

        if not isinstance(payload, list):
            return []

        return [ChatMessage.from_dict(item) for item in payload if isinstance(item, dict)]

    def save_chat(self, username: str, messages: List[ChatMessage]) -> None:
        chat_path = self._chat_file(username)
        with chat_path.open("w", encoding="utf-8") as handle:
            json.dump([message.to_dict() for message in messages], handle, indent=4)

    def append_message(self, username: str, message: ChatMessage) -> None:
        messages = self.load_chat(username)
        messages.append(message)
        self.save_chat(username, messages)

    def clear_chat(self, username: str) -> None:
        chat_path = self._chat_file(username)
        if chat_path.exists():
            chat_path.unlink()