"""AI service for managing chat interactions and OpenAI API calls."""

from typing import List

from openai import OpenAIError

from config import get_settings
from utils.exceptions import AIServiceError
from utils.logging import get_logger
from Data.ai_store import ChatMessage, ChatStore, get_openai_client

logger = get_logger(__name__)


class AIService:
    """Service for handling AI-powered chat interactions."""

    def __init__(self, chat_store: ChatStore) -> None:
        """Initialize AI service with chat store.

        Args:
            chat_store: Chat store for persisting conversations
        """
        self._chat_store = chat_store
        self._settings = get_settings()

    def load_chat_history(self, username: str) -> List[ChatMessage]:
        """Load chat history for a user.

        Args:
            username: User's identifier

        Returns:
            List of chat messages
        """
        try:
            return self._chat_store.load_chat(username)
        except Exception as e:
            logger.error(f"Failed to load chat history for {username}: {e}")
            return []

    def build_openai_messages(self, user_message: str, history: List[ChatMessage]) -> List[dict]:
        """Build messages array for OpenAI API call.

        Args:
            user_message: Current user message
            history: Previous chat messages

        Returns:
            Messages formatted for OpenAI API
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly asthma support assistant for Breeze Buddy. "
                    "Answer questions clearly, calmly, and in plain language. "
                    "Use the conversation history to keep the chat stateful and helpful. "
                    "If you are unsure, offer general asthma care advice and encourage the user to seek medical support when needed."
                ),
            }
        ]

        for message in history:
            messages.append({"role": message.role, "content": message.content})

        messages.append({"role": "user", "content": user_message})
        return messages

    def get_ai_response(self, messages: List[dict]) -> str:
        """Get AI response from OpenAI API.

        Args:
            messages: Messages to send to OpenAI

        Returns:
            AI response text

        Raises:
            AIServiceError: If API call fails
        """
        try:
            client = get_openai_client()
            if client is None:
                raise AIServiceError("OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
            
            completion = client.chat.completions.create(
                model=self._settings.openai_model,
                messages=messages,
                temperature=self._settings.openai_temperature,
                max_tokens=self._settings.openai_max_tokens,
            )
            return completion.choices[0].message.content.strip()
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise AIServiceError(f"AI service unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in AI response: {e}")
            raise AIServiceError(f"Failed to get AI response: {str(e)}")

    def process_user_message(self, username: str, user_message: str) -> str:
        """Process a user message and return AI response.

        Args:
            username: User's identifier
            user_message: User's message

        Returns:
            AI response text

        Raises:
            AIServiceError: If processing fails
        """
        try:
            history = self._chat_store.load_chat(username)
            user_chat = ChatMessage(role="user", content=user_message)
            self._chat_store.append_message(username, user_chat)

            messages = self.build_openai_messages(user_message, history)
            response = self.get_ai_response(messages)

            assistant_chat = ChatMessage(role="assistant", content=response)
            self._chat_store.append_message(username, assistant_chat)

            return response
        except Exception as e:
            logger.error(f"Failed to process message for {username}: {e}")
            raise AIServiceError(f"Failed to process message: {str(e)}")

    def clear_chat_history(self, username: str) -> None:
        """Clear chat history for a user.

        Args:
            username: User's identifier
        """
        try:
            self._chat_store.clear_chat(username)
            logger.info(f"Cleared chat history for {username}")
        except Exception as e:
            logger.error(f"Failed to clear chat history for {username}: {e}")
            raise AIServiceError(f"Failed to clear chat history: {str(e)}")
        return response

    def clear_chat_history(self, username: str) -> None:
        self._chat_store.clear_chat(username)