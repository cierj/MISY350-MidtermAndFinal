"""Streamlit UI for Breeze Buddy asthma management application."""

import streamlit as st
from typing import Optional

from config import get_settings
from utils.exceptions import AuthenticationError, ValidationError, AIServiceError
from Services.ai_manager import AIService
from Services.journal_manager import AuthService, JournalService
from Data.journal_store import User


def initialize_session_state() -> None:
    """Initialize Streamlit session state with default values."""
    settings = get_settings()
    defaults = {
        "logged_in": False,
        "user_id": None,
        "role": None,
        "page": "Login",
        "viewing_child_id": None,
        "faq_messages": [],
        "faq_user_input": "",
        "good_day_message": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_current_user(auth_service: AuthService) -> Optional[User]:
    """Get the currently logged-in user from session state.

    Args:
        auth_service: Authentication service

    Returns:
        User object if logged in, None otherwise
    """
    if not st.session_state.get("logged_in"):
        return None
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None
    return auth_service.get_user_by_id(user_id)


def render_dashboard_kpis(user: User, journal_service: JournalService) -> None:
    """Render dashboard KPI cards for both parent and child users."""
    is_child = user.role.lower() == "child"
    streak = journal_service.get_consecutive_streak(user.identifier)
    average_breath = journal_service.get_average_breath_rating(user.identifier)
    milestones = journal_service.get_streak_milestones(streak)
    milestone_display = " ".join(
        f"{'⭐' if earned else '☆'} {label}"
        for label, earned in milestones.items()
    )

    if is_child and st.session_state.get("good_day_message"):
        st.markdown(
            '''<div style='margin-bottom:18px; font-size:24px; font-weight:bold; text-align:center; background: linear-gradient(90deg, red, orange, yellow, green, blue, violet); -webkit-background-clip: text; color: transparent;'>That's amazing! Keep up the great work!</div>''',
            unsafe_allow_html=True,
        )
        st.session_state["good_day_message"] = False

    card_style = (
        "border-radius: 18px; padding: 22px; min-height: 190px; "
        "box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);"
    )
    child_style = "background: linear-gradient(135deg, #fff7d6, #ffdfe0);"
    parent_style = "background: #f5f7fb;"
    container_style = card_style + (child_style if is_child else parent_style) + " text-align:center;"

    average_text = f"{average_breath:.1f}" if average_breath > 0 else "—"
    streak_label = f"{streak} day{'s' if streak != 1 else ''}"

    col1, col2, col3 = st.columns([1, 1, 1], gap="large")
    with col1:
        st.markdown(
            f"<div style='{container_style}'>"
            f"<div style='font-size:18px; font-weight:700; margin-bottom:10px;'>Streak</div>"
            f"<div style='font-size:44px; color:#FFD700; margin-bottom:8px;'>{'⭐' if streak >= 1 else '☆'}</div>"
            f"<div style='font-size:15px; margin-bottom:6px;'>{milestone_display}</div>"
            f"<div style='font-size:14px; color:#444;'>Milestone progress</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div style='{container_style}'>"
            f"<div style='font-size:18px; font-weight:700; margin-bottom:10px;'>Days Logged</div>"
            f"<div style='font-size:56px; color:#0072C6; margin-bottom:6px;'>{streak}</div>"
            f"<div style='font-size:15px; color:#444;'>{streak_label} in a row</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col3:
        breath_color = "red" if is_child else "#333"
        st.markdown(
            f"<div style='{container_style}'>"
            f"<div style='font-size:18px; font-weight:700; margin-bottom:10px;'>Average Breath</div>"
            f"<div style='font-size:58px; color:{breath_color}; margin-bottom:8px;'>{average_text}</div>"
            f"<div style='font-size:15px; color:#444;'>Updated with every breath log</div>"
            "</div>",
            unsafe_allow_html=True,
        )


def run_app(auth_service: AuthService, journal_service: JournalService, ai_service: AIService) -> None:
    """Run the main Streamlit application.

    Args:
        auth_service: Authentication service
        journal_service: Journal service
        ai_service: AI service
    """
    settings = get_settings()
    st.set_page_config(
        page_title=settings.app_title,
        page_icon=settings.app_icon
    )
    initialize_session_state()

    with st.sidebar:
        st.title("Breeze Buddy")
        if st.session_state.get("logged_in"):
            if st.button("Logout"):
                perform_logout()
        else:
            st.info("Please log in to continue")

        menu_options = ["Dashboard", "Journal", "Frequently asked questions"] if st.session_state.get("logged_in") else ["Login"]
        if st.session_state.get("logged_in") and st.session_state.get("role") == "Parent":
            menu_options.append("Manage Children")

        selected = st.radio("Navigate", menu_options, index=menu_options.index(st.session_state.get("page")))
        st.session_state["page"] = selected

    st.title(settings.app_title)

    if st.session_state["page"] == "Login":
        render_login(auth_service)
    elif st.session_state["page"] == "Dashboard":
        render_dashboard(auth_service, journal_service)
    elif st.session_state["page"] == "Journal":
        render_journal_page(auth_service, journal_service)
    elif st.session_state["page"] == "Frequently asked questions":
        render_faq_page(auth_service, ai_service)
    elif st.session_state["page"] == "Manage Children":
        render_manage_children(auth_service)


def perform_logout() -> None:
    """Perform user logout and clear session state."""
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["role"] = None
    st.session_state["page"] = "Login"
    st.session_state["viewing_child_id"] = None
    st.success("You have been logged out")


def render_login(auth_service: AuthService) -> None:
    """Render the login page.

    Args:
        auth_service: Authentication service
    """
    st.header("Login")

    # Demo info box
    st.info("""
    **Demo Accounts for Testing:**

    Parent: username: `sfolkart` password: `12345678`

    Child: username: `child` password: `123456789`

    These accounts are pre-configured and connected for demonstration purposes.
    """)

    with st.form(key="login_form"):
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            if not username or not password:
                st.error("Please enter both username/email and password.")
                return

            try:
                user = auth_service.authenticate(username, password)
                if user is None:
                    st.error("Invalid login credentials.")
                    return

                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user.id
                st.session_state["role"] = user.role
                st.session_state["page"] = "Dashboard"
                st.success(f"Welcome back, {user.username}!")
                st.rerun()

            except AuthenticationError as e:
                st.error(f"Login failed: {e.message}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                return

            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user.id
            st.session_state["role"] = user.role
            st.session_state["page"] = "Dashboard"
            st.success(f"Welcome back, {user.username}!")
            st.rerun()

    st.markdown("---")
    st.header("Create New Account")
    with st.form(key="register_form"):
        new_username = st.text_input("Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.radio("Select your role", ["Parent", "Child"], horizontal=True)
        register_clicked = st.form_submit_button("Create Account")

        if register_clicked:
            if not new_username or not new_email or not new_password or not confirm_password:
                st.error("Please fill in all registration fields.")
                return
            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return
            try:
                auth_service.register(new_username, new_email, new_password, role)
                st.success("Account created successfully. Please log in.")
                st.session_state["page"] = "Login"
            except ValidationError as e:
                st.error(f"Registration failed: {e.message}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")


def render_dashboard(auth_service: AuthService, journal_service: JournalService) -> None:
    user = get_current_user(auth_service)
    if user is None:
        st.error("Please log in first.")
        return

    st.header("Dashboard")
    st.markdown(f"### Welcome, {user.username}! 👋")
    render_dashboard_kpis(user, journal_service)

    if user.role.lower() == "parent":
        st.subheader("Parent Overview")
        st.write(f"Linked children: {len(user.children)}")
        if st.button("Manage Children"):
            st.session_state["page"] = "Manage Children"
            st.rerun()
            return

        if user.children:
            st.write("### Your linked children")
            for child_id in user.children:
                child = auth_service.find_user_by_identifier(child_id)
                child_name = child.username if child else child_id
                st.write(f"- {child_name}")
        else:
            st.info("You haven't linked any children yet.")
            st.write("Use the Manage Children page to connect a child account.")
    else:
        st.subheader("Child Dashboard")
        if journal_service.has_entry_today(user.identifier):
            st.success("✅ Feeling submitted today. Great job!")
        else:
            st.warning("❌ No feeling recorded yet today.")
        st.write("Remember to log your mood and breathing status.")

        if st.button("Record Feeling Now"):
            st.session_state["page"] = "Journal"
            st.rerun()


def render_faq_page(auth_service: AuthService, ai_service: AIService) -> None:
    user = get_current_user(auth_service)
    if user is None:
        st.error("Please log in first.")
        return

    st.header("Frequently asked questions")
    left_column, right_column = st.columns(2)

    with left_column:
        faqs = [
            (
                "What are the most common asthma symptoms?",
                "Common symptoms include coughing, wheezing, chest tightness, and shortness of breath."
            ),
            (
                "How should I use my inhaler?",
                "Use your inhaler exactly as prescribed. Shake before use, breathe out fully, then inhale slowly while pressing the canister."
            ),
            (
                "What can trigger an asthma attack?",
                "Triggers can include pollen, dust, smoke, strong smells, cold air, exercise, and respiratory infections."
            ),
            (
                "When should I seek medical help?",
                "Seek help if your symptoms worsen, your rescue inhaler does not help, or you feel dizzy, confused, or too tired to breathe comfortably."
            ),
        ]

        for question, answer in faqs:
            with st.expander(question):
                st.write(answer)

    with right_column:
        st.subheader("Asthma Help Chatbot")
        if st.session_state.get("faq_messages") == []:
            stored_history = ai_service.load_chat_history(user.identifier)
            st.session_state["faq_messages"] = [message.to_dict() for message in stored_history]

        if st.button("Clear conversation", key="clear_faq_chat"):
            try:
                ai_service.clear_chat_history(user.identifier)
                st.session_state["faq_messages"] = []
                st.session_state["faq_user_input"] = ""
                st.rerun()
            except AIServiceError as e:
                st.error(f"Failed to clear conversation: {e.message}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

        for message in st.session_state.get("faq_messages", []):
            if message["role"] == "assistant":
                st.info(message["content"], icon="🤖")
            else:
                st.write(f"**You:** {message['content']}")

        with st.form(key="faq_chat_form"):
            user_input = st.text_input("Ask a question about asthma", key="faq_user_input")
            submitted = st.form_submit_button("Send")

            if submitted and user_input:
                try:
                    response = ai_service.process_user_message(user.identifier, user_input)
                    st.session_state["faq_messages"].append({"role": "user", "content": user_input})
                    st.session_state["faq_messages"].append({"role": "assistant", "content": response})
                    st.session_state["faq_user_input"] = ""
                    st.rerun()
                except AIServiceError as e:
                    st.error(f"AI service error: {e.message}")
                    st.info("Please try again or check your internet connection.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")


def render_journal_page(auth_service: AuthService, journal_service: JournalService) -> None:
    user = get_current_user(auth_service)
    if user is None:
        st.error("Please log in first.")
        return

    st.header("Health Journal")

    if user.role.lower() == "parent":
        render_parent_journal(auth_service, journal_service, user)
    else:
        render_child_journal(auth_service, journal_service, user)


def render_parent_journal(auth_service: AuthService, journal_service: JournalService, user: User) -> None:
    if not user.children:
        st.info("No children linked yet. Add a child from Manage Children.")
        return

    child_options = []
    for child_id in user.children:
        child = auth_service.find_user_by_identifier(child_id)
        if child:
            child_options.append((child.username, child.identifier))
        else:
            child_options.append((child_id, child_id))

    selected_child = st.selectbox("Pick a child to view their journal", [label for label, _ in child_options])
    child_identifier = next((identifier for label, identifier in child_options if label == selected_child), user.children[0])
    child_user = auth_service.find_user_by_identifier(child_identifier)

    if child_user is None:
        st.error("Selected child account could not be found.")
        return

    st.subheader(f"Journal for {child_user.username}")
    entries = journal_service.list_entries(child_user.identifier)
    render_entry_list(entries)


def render_child_journal(auth_service: AuthService, journal_service: JournalService, user: User) -> None:
    if st.session_state.get("good_day_message"):
        st.markdown(
            '''<div style='margin-bottom:18px; font-size:24px; font-weight:bold; text-align:center; background: linear-gradient(90deg, red, orange, yellow, green, blue, violet); -webkit-background-clip: text; color: transparent;'>That's amazing! Keep up the great work!</div>''',
            unsafe_allow_html=True,
        )
        st.session_state["good_day_message"] = False

    with st.expander("Record a new feeling", expanded=True):
        feeling = st.selectbox(
            "How are you feeling today?",
            ["Happy 😊", "Sad 😢", "Calm 😌", "Anxious 😰", "Energetic ⚡", "Tired 😴", "Frustrated 😤"],
            key="feeling_select"
        )
        breathing = st.slider("Breathing quality", 1, 10, 10, key="breathing_slider")
        notes = st.text_area("Notes", placeholder="Add any symptoms, triggers, or thoughts.", key="notes_area")

        if st.button("Submit Feeling", key="submit_feeling"):
            try:
                entry = journal_service.add_entry(user.identifier, feeling, breathing, notes)
                is_good_day = breathing >= 8 or "happy" in feeling.lower()
                if is_good_day:
                    st.session_state["good_day_message"] = True
                st.success("Your feeling has been submitted.")
                st.info(f"Saved entry for {entry.date} at {entry.time}.")
                st.experimental_rerun()
            except ValidationError as e:
                st.error(f"Failed to submit entry: {e.message}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

    entries = journal_service.list_entries(user.identifier)
    render_entry_list(entries)


def render_entry_list(entries: list) -> None:
    if not entries:
        st.info("No journal entries yet. Add your first feeling entry above.")
        return

    for entry in entries:
        with st.expander(f"{entry.date} {entry.time} — {entry.feeling}"):
            st.write(f"**Breathing:** {entry.breathing}")
            st.write(f"**Notes:** {entry.notes}")


def render_manage_children(auth_service: AuthService) -> None:
    user = get_current_user(auth_service)
    if user is None:
        st.error("Please log in first.")
        return
    if user.role.lower() != "parent":
        st.error("Only parents can manage child accounts.")
        return

    st.header("Manage Children")
    with st.form(key="link_child_form"):
        child_login = st.text_input("Child username or email")
        linked = st.form_submit_button("Link Child")

        if linked:
            try:
                auth_service.link_child(user, child_login)
                st.success("Child linked successfully.")
                st.rerun()
            except ValidationError as e:
                st.error(f"Failed to link child: {e.message}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

    if not user.children:
        st.info("You have not linked any child accounts yet.")
        return

    st.subheader("Linked Children")
    for child_id in user.children:
        child = auth_service.find_user_by_identifier(child_id)
        child_name = child.username if child else child_id
        with st.expander(child_name):
            if child:
                st.write(f"Email: {child.email}")
            else:
                st.write("Child account not found.")

            if st.button(f"View {child_name} Journal", key=f"view_{child_id}"):
                st.session_state["page"] = "Journal"
                st.rerun()
                return
