import streamlit as st
from typing import Optional

from Services.journal_manager import AuthService, JournalService
from Data.journal_store import User


def initialize_session_state() -> None:
    defaults = {
        "logged_in": False,
        "user_id": None,
        "role": None,
        "page": "Login",
        "viewing_child_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_current_user(auth_service: AuthService) -> Optional[User]:
    if not st.session_state.get("logged_in"):
        return None
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None
    return auth_service.get_user_by_id(user_id)


def run_app(auth_service: AuthService, journal_service: JournalService) -> None:
    st.set_page_config(page_title="Breeze Buddy - Your Asthma Companion", page_icon="🌬️")
    initialize_session_state()

    with st.sidebar:
        st.title("Breeze Buddy")
        if st.session_state.get("logged_in"):
            if st.button("Logout"):
                perform_logout()
        else:
            st.info("Please log in to continue")

        menu_options = ["Dashboard", "Journal"] if st.session_state.get("logged_in") else ["Login"]
        if st.session_state.get("logged_in") and st.session_state.get("role") == "Parent":
            menu_options.append("Manage Children")

        selected = st.radio("Navigate", menu_options, index=menu_options.index(st.session_state.get("page")))
        st.session_state["page"] = selected

    st.title("Breeze Buddy - Your Asthma Companion")

    if st.session_state["page"] == "Login":
        render_login(auth_service)
    elif st.session_state["page"] == "Dashboard":
        render_dashboard(auth_service, journal_service)
    elif st.session_state["page"] == "Journal":
        render_journal_page(auth_service, journal_service)
    elif st.session_state["page"] == "Manage Children":
        render_manage_children(auth_service)


def perform_logout() -> None:
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["role"] = None
    st.session_state["page"] = "Login"
    st.session_state["viewing_child_id"] = None
    st.success("You have been logged out")


def render_login(auth_service: AuthService) -> None:
    st.header("Login")

    # Demo info box
    st.info("""
    **Demo Accounts for Testing:**
    
    Parent: username: `sfolkart` password: `123456789`
    
    Child: username: `child` password: `12345678`
    
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
            except ValueError as error:
                st.error(str(error))


def render_dashboard(auth_service: AuthService, journal_service: JournalService) -> None:
    user = get_current_user(auth_service)
    if user is None:
        st.error("Please log in first.")
        return

    st.header("Dashboard")
    st.markdown(f"### Welcome, {user.username}! 👋")

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
    with st.expander("Record a new feeling", expanded=True):
        feeling = st.selectbox(
            "How are you feeling today?",
            ["Happy 😊", "Sad 😢", "Calm 😌", "Anxious 😰", "Energetic ⚡", "Tired 😴", "Frustrated 😤"],
            key="feeling_select"
        )
        breathing = st.slider("Breathing quality", 1, 10, 10, key="breathing_slider")
        notes = st.text_area("Notes", placeholder="Add any symptoms, triggers, or thoughts.", key="notes_area")

        if st.button("Submit Feeling", key="submit_feeling"):
            entry = journal_service.add_entry(user.identifier, feeling, breathing, notes)
            st.success("Your feeling has been submitted.")
            st.info(f"Saved entry for {entry.date} at {entry.time}.")

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
            except ValueError as error:
                st.error(str(error))
                return

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
