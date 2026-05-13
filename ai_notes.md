# AI Chatbot and FAQ Tab Implementation Notes

## Summary
Added a new "Frequently asked questions" tab for all logged-in users with two equal columns: 4 asthma FAQ expanders on the left and a stateful OpenAI-style chatbot on the right.

## Files Changed

### `app.py`
- Added `ChatStore` import and initialization (lines 1, 11).
- Added `AIService` import and initialization (lines 3, 15).
- Passed `ai_service` into `run_app()` so the UI can render the FAQ/chat page.

### `UI/breath_dashboard.py`
- Added `AIService` import (line 4).
- Initialized session state keys for `faq_messages` and `faq_user_input` (lines 16-17).
- Added "Frequently asked questions" to the navigation menu for logged-in users (line 33).
- Added page routing for `render_faq_page()` (line 61).
- Implemented `render_faq_page()` with two-side layout:
  - Left column: 4 asthma FAQ expander boxes (starting at line 184).
  - Right column: chatbot message history, clear chat button, and text input form (starting at line 209).
- Kept chatbot messages stateful with `st.session_state` updates after each submission (lines 229-233).

### `Data/ai_store.py`
- Created `ChatMessage` dataclass for role/content message storage.
- Created `ChatStore` with methods to load, save, append, and clear chat history per user (line 20 onward).
- Added OpenAI environment loading via `load_dotenv()` and created `OPENAI_CLIENT` from `OpenAI(api_key=os.getenv("OPENAI_API_KEY"))` (lines 6, 9-10).
- Persisted chat records as `chat_history_<username>.json` files.

### `Services/ai_manager.py`
- Created `AIService` to handle chat prompt building, response generation, persistence, and state updates.
- Added `build_openai_messages()` to construct message history for the OpenAI chat endpoint (line 13).
- Added `get_ai_response()` to call `OPENAI_CLIENT.chat.completions.create(...)` with `gpt-3.5-turbo` and return the assistant response (lines 32-33).
- Added `process_user_message()` to append the user message, send it to OpenAI, and store both user and assistant messages (lines 46-47).
- Added `clear_chat_history()` to reset stored chat history.

### `.env`
- Added a local `.env` file containing a fake OpenAI API key for configuration.

### `.gitignore`
- Added `.env` to `.gitignore` to prevent sensitive keys from being committed.

## Notes
- The chatbot side does not connect to OpenAI, but it includes a full service/data/UI setup as requested.
- `st.session_state` is used throughout the FAQ page to maintain chat history and user input between reruns.
- The FAQ tab is available to every authenticated user and is integrated into the sidebar navigation.
