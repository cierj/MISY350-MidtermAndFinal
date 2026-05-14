#Stephen Folkart and Jacob Cierniak

# Origin Prompt

Create a file named Improvement_Plan.md. I want you to create a plan first based on the feature analysis on what to improve, do not implement any changes, just take what i am telling you and create a plan for adding this functionality. List the plan in the Improvement_Plan.md file. At the top of the file there should be a section Titled Origin Prompt That contains everything written for this prompt.

In the improvement_plan markdown, create a plan to implement this feature: We want KPIs for both parent and child. We want the same KPIs for both and we want the child to be more colorful and keep a streak using stars for days in a row logged. We want the streak to show a star when the kid hits one week, two weeks, one month, 6 months, and a year logged. We want a number to show the average breath rating taken from the logged entries and every breath logged will update that rating. We want a message to show if a child has a good day that says “Thats amazing! Keep up the great work!” And that should pop up once the child logs it.  I think primary colors are best here, yellow for the star streak. Messages with  “That's amazing! Keep up the great work!” Can be in rainbow font. Breath rating could be in red so it appears bright for the child to see immediately. We want these KPIs to appear right on the dashboard underneath the welcome message. We want it in a bigger font and for it to enhance the look of our current dashboard. We want three squares, and one square per KPI. The furthest on the left should be the streak square, middle should be the days logged in a row, and the far right should be the average breath rating. Go file by file and list what lines change, as well as what layer of the code changes, and what the goal of this code is. Add it to the origin prompt.

# Improvement Plan for Breeze Buddy

## Summary
This plan outlines improvements to Breeze Buddy based on the current feature set and application structure. The app currently includes user authentication, parent/child role handling, journal entry recording, child management, and an AI FAQ/chat interface. The main areas for enhancement are usability, data validation, robustness, configuration management, and feature completeness.

## KPI Dashboard Feature Plan
This feature introduces shared KPIs for parent and child dashboards, with a child-specific colorful presentation and streak tracking.

- Add a new KPI section on the dashboard directly underneath the welcome message.
- Display three KPI squares in a row: streak, consecutive days logged, and average breath rating.
- Keep the KPIs the same for parent and child while applying a more colorful, child-friendly style for child users.
- Track and display streak milestones as yellow stars at 1 week, 2 weeks, 1 month, 6 months, and 1 year of consecutive logging.
- Compute and display a live average breath rating from journal entries, updating immediately after each breath submission.
- For child users, show a one-time celebratory message when a particularly good day is logged: "That's amazing! Keep up the great work!" in rainbow font.
- Style the breath rating number in bright red for child users so it is immediately noticeable.
- Use primary colors and larger font sizes to make the KPI section visually prominent.
- Ensure the dashboard layout enhances the current UI while remaining easy to read and accessible.

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

### File-specific KPI change plan
- `UI/breath_dashboard.py` (UI layer): update the dashboard render flow near the top of the file, in `run_app()`/`render_dashboard()` just below the welcome message. Add three KPI squares for streak, consecutive days, and average breath rating, including child-specific color styling, star milestone display, and the celebratory message popup. Goal: place the KPIs prominently on the dashboard and improve visual appeal.
- `Services/journal_manager.py` (business logic layer): add helper methods or extend `JournalService` around the existing journal entry operations to compute streak length, consecutive days logged, milestone eligibility, and updated average breath rating. Goal: centralize KPI calculations so the UI only renders precomputed metrics.
- `Data/journal_store.py` (data layer): adjust the journal-loading helper functions near `load_journal()` to ensure journal entries are parsed consistently and permit date-based streak analysis. Goal: support accurate streak/milestone computations from stored history.
- `Data/ai_store.py` / `config.py` (support/config layer): expose or document configuration for the child congratulatory message, primary color UI flags, and any display settings needed for the KPI feature. Goal: separate presentation settings from UI code and keep styling logic maintainable.
- `README.md` / `STEPS.md` (documentation layer): update the project documentation to describe the KPI dashboard, required breath log behavior, and where to observe the child streak and average rating features. Goal: ensure the new feature is clear for users and developers.

## Priority Recommendations

- Highest priority: fix OpenAI initialization and provide a no-key fallback for app startup.
- High priority: ensure parent-child linking persists correctly and user update operations are not skipped.
- Medium priority: add journal entry editing/deletion and improve journal UI clarity.
- Lower priority: polish chat UX, add local mock mode, and enhance overall page layout.

## Notes

- The current app already includes core Breeze Buddy flows, so improvements should focus on stability and user-facing completeness.
- Avoid changing feature scope drastically; keep the user stories centered on asthma journaling, parent-child account management, and FAQ assistance.
- Ensure any changes are tested through the Streamlit flow and do not break the app startup path.
