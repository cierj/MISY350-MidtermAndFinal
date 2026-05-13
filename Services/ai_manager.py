from typing import List

from Data.ai_store import ChatMessage, ChatStore, OPENAI_CLIENT


class AIService:
    def __init__(self, chat_store: ChatStore):
        self._chat_store = chat_store

    def load_chat_history(self, username: str) -> List[ChatMessage]:
        return self._chat_store.load_chat(username)

    def build_openai_messages(self, user_message: str, history: List[ChatMessage]) -> List[dict]:
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
        completion = OPENAI_CLIENT.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=250,
        )
        return completion.choices[0].message.content.strip()

    def process_user_message(self, username: str, user_message: str) -> str:
        history = self._chat_store.load_chat(username)
        user_chat = ChatMessage(role="user", content=user_message)
        self._chat_store.append_message(username, user_chat)

        messages = self.build_openai_messages(user_message, history)
        response = self.get_ai_response(messages)

        assistant_chat = ChatMessage(role="assistant", content=response)
        self._chat_store.append_message(username, assistant_chat)
        return response

    def clear_chat_history(self, username: str) -> None:
        self._chat_store.clear_chat(username)