# Origin Prompt

Create a file named Improvement_Plan.md. I want you to create a plan first based on the feature analysis on what to improve, do not implement any changes, just take what i am telling you and create a plan for adding this functionality. List the plan in the Improvement_Plan.md file. At the top of the file there should be a section Titled Origin Prompt That contains everything written for this prompt.

# Improvement Plan for Breeze Buddy

## Summary
This plan outlines improvements to Breeze Buddy based on the current feature set and application structure. The app currently includes user authentication, parent/child role handling, journal entry recording, child management, and an AI FAQ/chat interface. The main areas for enhancement are usability, data validation, robustness, configuration management, and feature completeness.

## Improvement Areas

1. Authentication and user experience
   - Add persistent login state and better session handling.
   - Improve registration validation and user feedback for duplicate usernames/emails.
   - Add password strength guidance and a "show password" option.
   - Fix child linking logic and ensure parent user store updates are saved consistently.

2. Journal management
   - Add proper timestamp handling and deduplication for same-day entries.
   - Enable editing and deleting journal entries.
   - Improve journal display with sorted entries and clear date headers.
   - Add summary/statistics for recent feelings and breathing scores.

3. Child account management
   - Add ability to unlink children and handle missing child records gracefully.
   - Improve parent dashboard with clickable child cards and child activity summaries.
   - Add a parent view of child journal history and alerts for missed daily check-ins.

4. AI FAQ/chat integration
   - Provide a fallback path if OpenAI API key is missing without blocking the whole app.
   - Add a local mock chatbot mode for testing and demo without OpenAI credentials.
   - Improve chat history loading and display with timestamps.
   - Add error handling and user notifications when AI service is unavailable.

5. Configuration and environment management
   - Consolidate settings loading in `config.py` and avoid global OpenAI client creation at import time.
   - Use `.env` loading and validate required environment variables at startup.
   - Add documentation for required environment variables and local run commands.

6. Data storage and robustness
   - Add storage validation for JSON files and recover from corrupted files.
   - Use unique safe filenames for journals and chat history.
   - Ensure store update methods persist changes consistently.

7. UI/UX improvements
   - Use Streamlit form state correctly and avoid rerun loops after successful actions.
   - Add clear navigation labels and user guidance for each page.
   - Improve layout for dashboard, journal, and FAQ pages with better spacing.
   - Add a landing page or welcome screen for unauthenticated users.

## Implementation Plan

1. Review the current data store models and fix any inconsistent save/update logic.
2. Add validation and error handling in `AuthService.register`, `AuthService.link_child`, and `JournalService.add_entry`.
3. Refactor AI client initialization into a lazy factory in `Data/ai_store.py` with optional mock mode.
4. Add configuration settings support for API key, model, temperature, and token limits.
5. Enhance `UI/breath_dashboard.py` with more explicit navigation state, page fallback logic, and child management flows.
6. Add journal editing/deleting UI controls and data operations.
7. Document required environment setup and run commands in `README.md` or `STEPS.md`.

## Priority Recommendations

- Highest priority: fix OpenAI initialization and provide a no-key fallback for app startup.
- High priority: ensure parent-child linking persists correctly and user update operations are not skipped.
- Medium priority: add journal entry editing/deletion and improve journal UI clarity.
- Lower priority: polish chat UX, add local mock mode, and enhance overall page layout.

## Notes

- The current app already includes core Breeze Buddy flows, so improvements should focus on stability and user-facing completeness.
- Avoid changing feature scope drastically; keep the user stories centered on asthma journaling, parent-child account management, and FAQ assistance.
- Ensure any changes are tested through the Streamlit flow and do not break the app startup path.
