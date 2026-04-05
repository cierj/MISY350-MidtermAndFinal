import streamlit as st
import json
from pathlib import Path
import uuid
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

json_file = Path("users.json")

if json_file.exists():
    with open(json_file, "r") as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = []
else:
    users = []

for user in users:
    if not user.get("username"):
        user["username"] = user.get("email", "")
    if "children" not in user:
        user["children"] = []
    if "role" not in user:
        user["role"] = "Child"


def save_users():
    with open(json_file, "w") as f:
        json.dump(users, f, indent=4)


def get_user_identifier(user):
    return user.get("username") or user.get("email")


def find_user_by_login(login_value):
    login_value = login_value.lower()
    for user in users:
        if user.get("username", "").lower() == login_value or user.get("email", "").lower() == login_value:
            return user
    return None


def load_journal(username):
    journal_path = Path(f"journal_{username}.json")
    if journal_path.exists():
        with open(journal_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_journal(username, data):
    journal_path = Path(f"journal_{username}.json")
    with open(journal_path, "w") as f:
        json.dump(data, f, indent=4)


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "viewing_child" not in st.session_state:
    st.session_state["viewing_child"] = None

st.set_page_config(page_title="Breeze Buddy - Your Asthma Companion")
st.title("Breeze Buddy - Your Asthma Companion")


def login():
    st.subheader("Login")
    username_input = st.text_input("Username or Email", key="username_login")
    password_input = st.text_input("Password", type="password", key="password_login")

    if st.button("Log In", type="primary", use_container_width=True):
        if not username_input or not password_input:
            st.error("Please fill in all fields")
            return

        found_user = None
        with st.spinner("Logging in..."):
            time.sleep(1)
            for user in users:
                if user.get("username", "").lower() == username_input.lower() or user.get("email", "").lower() == username_input.lower():
                    if check_password_hash(user.get("password", ""), password_input):
                        found_user = user
                        break

        if found_user:
            st.success(f"Welcome back, {found_user.get('username')}!")
            st.session_state["logged_in"] = True
            st.session_state["user"] = found_user
            st.session_state["role"] = found_user.get("role", "Child")
            st.session_state["page"] = "dashboard"
            time.sleep(0.5)
            st.experimental_rerun()
            return
        else:
            st.error("Invalid username or password")

    st.write("---")
    st.subheader("Create New Account")
    new_username = st.text_input("Username", key="username_register")
    new_email = st.text_input("Email", key="email_register")
    new_password = st.text_input("Password", type="password", key="password_register")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
    role = st.radio("Select your role:", options=["Parent", "Child"], horizontal=True, key="role_select")

    if st.button("Create Account", key="register_btn"):
        if not new_username or not new_email or not new_password or not confirm_password:
            st.error("Please fill in all fields")
            return
        if new_password != confirm_password:
            st.error("Passwords do not match")
            return
        if len(new_password) < 8:
            st.error("Password must be at least 8 characters")
            return
        if any(u.get("username", "").lower() == new_username.lower() for u in users):
            st.error("Username already taken")
            return
        if any(u.get("email", "").lower() == new_email.lower() for u in users):
            st.error("Email already registered")
            return

        with st.spinner("Creating account..."):
            time.sleep(1)
            new_user = {
                "id": str(uuid.uuid4()),
                "username": new_username.lower(),
                "email": new_email.lower(),
                "password": generate_password_hash(new_password),
                "role": role,
                "children": []
            }
            users.append(new_user)
            save_users()
            st.success("Account created! Please log in.")
            time.sleep(0.5)
            st.experimental_rerun()

        st.info("Please use the login form above to sign in with your new account.")

    st.write("---")
    # For debugging. Shows list of accounts
    #st.write("Existing accounts")
    #st.dataframe([
    #    {"username": u.get("username"), "email": u.get("email"), "role": u.get("role")} for u in users
    #])


def logout():
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.session_state["role"] = None
    st.session_state["page"] = "login"
    st.session_state["viewing_child"] = None
    st.success("Logged out successfully")
    st.experimental_rerun()


def dashboard():
    st.subheader("Dashboard")
    current_user = st.session_state.get("user")
    if not current_user:
        st.error("Please log in first.")
        return

    username = current_user.get('username')
    st.markdown(f"# Welcome, {username}! 👋")
    
    if current_user.get("role") == "Parent":
        st.write("### Parent Dashboard")
        st.write(f"Linked children: {len(current_user.get('children', []))}")
        
        # Parent recommendations
        st.write("### 📋 Today's Tasks")
        if current_user.get("children"):
            st.write("✅ Check in on your children's progress")
            st.write("💡 View their journal entries to stay informed")
        else:
            st.write("❌ You haven't linked any children yet")
            st.write("💡 Link a child account to start monitoring their health")
        
        if st.button("Manage Children", key="dashboard_manage_children"):
            st.session_state["page"] = "manage_children"
            st.experimental_rerun()
            return

        if current_user.get("children"):
            st.write("### Your linked children")
            for child_id in current_user.get("children", []):
                child_user = next((u for u in users if get_user_identifier(u) == child_id), None)
                display_name = child_user.get("username") if child_user else child_id
                st.write(f"- {display_name}")
    else:
        st.write("### Child Dashboard")
        
        # Check today's entries
        username = get_user_identifier(current_user)
        journal_data = load_journal(username)
        today = datetime.now().strftime("%Y-%m-%d")
        
        has_entry_today = any(entry_key.startswith(today) for entry_key in journal_data.keys())
        
        st.write("### 📋 Today's Checklist")
        if has_entry_today:
            st.write("✅ **Logged your feelings** - Great job!")
        else:
            st.write("❌ **Log your feelings** - Don't forget to track how you're feeling today!")
        
        st.write("### 💡 Recommendations for Today")
        if not has_entry_today:
            st.write("- 📝 Log your feelings and breathing quality")
            st.write("- 💬 Take a moment to write any symptoms or observations")
        else:
            st.write("- 👍 You've done great today! Keep up the habit")
            st.write("- 📊 Check back later to update your entry if needed")


def manage_children():
    st.subheader("Manage Children")
    current_user = st.session_state.get("user")
    if not current_user or current_user.get("role") != "Parent":
        st.error("Only parents can manage children")
        return

    st.write("### Add a Child to Your Account")
    child_login = st.text_input("Child username or email", key="child_login")

    if st.button("Link Child", key="link_child"):
        if not child_login:
            st.error("Please enter a username or email")
            return

        child_user = find_user_by_login(child_login)
        if not child_user or child_user.get("role") != "Child":
            st.error("Child account not found or not a child account")
            return

        child_id = get_user_identifier(child_user)
        if child_id in current_user.get("children", []):
            st.warning("Child already linked")
            return

        # Persist the parent-child link in the stored users list as well
        parent_id = current_user.get("id")
        parent_user = next((u for u in users if u.get("id") == parent_id), None)
        if parent_user is not None:
            parent_user.setdefault("children", []).append(child_id)
            current_user = parent_user
            st.session_state["user"] = parent_user
        else:
            current_user.setdefault("children", []).append(child_id)

        save_users()
        st.success(f"Child {child_id} linked successfully")
        st.experimental_rerun()
        return

    st.write("---")
    st.write("### Linked Children")
    children = current_user.get("children", [])
    if not children:
        st.info("No children linked yet")
        return

    for child_id in children:
        child_user = next((u for u in users if get_user_identifier(u) == child_id), None)
        display_name = child_user.get("username") if child_user else child_id
        with st.expander(f"👶 {display_name}"):
            if child_user:
                st.write(f"Email: {child_user.get('email')}")
                st.write(f"Role: {child_user.get('role')}")
            if st.button(f"View {display_name}'s Info", key=f"view_{child_id}"):
                st.session_state["viewing_child"] = child_id
                st.session_state["page"] = "child_info"
                st.experimental_rerun()
                return
            if st.button(f"Unlink {display_name}", key=f"unlink_{child_id}"):
                parent_id = current_user.get("id")
                parent_user = next((u for u in users if u.get("id") == parent_id), None)
                if parent_user is not None and child_id in parent_user.get("children", []):
                    parent_user["children"].remove(child_id)
                    current_user = parent_user
                    st.session_state["user"] = parent_user

                if child_id in current_user.get("children", []):
                    current_user["children"].remove(child_id)
                save_users()
                st.success(f"{display_name} has been removed from your account")
                st.experimental_rerun()
                return


def child_info():
    child_id = st.session_state.get("viewing_child")
    if not child_id:
        st.error("No child selected")
        return

    child_user = next((u for u in users if get_user_identifier(u) == child_id), None)
    if not child_user:
        st.error("Child account not found")
        return

    st.subheader(f"{child_user.get('username')}\'s Info")
    st.write(f"Email: {child_user.get('email')}")
    st.write("### Journal Entries")

    journal_data = load_journal(get_user_identifier(child_user))
    if not journal_data:
        st.info("No journal notes found for this child yet.")
    else:
        for entry_key in sorted(journal_data.keys(), reverse=True):
            entry = journal_data[entry_key]
            label = f"{entry.get('date')} {entry.get('time', '')} — {entry.get('feeling')}"
            with st.expander(f"{label}"):
                st.write(f"**Time:** {entry.get('time', 'N/A')}")
                st.write(f"**Feeling:** {entry.get('feeling')}")
                st.write(f"**Breathing:** {entry.get('breathing')}")
                st.write(f"**Notes:** {entry.get('notes')}")

    if st.button("Back to Manage Children", key="back_to_manage"):
        st.session_state["page"] = "manage_children"
        st.session_state["viewing_child"] = None
        st.experimental_rerun()
        return


def journal():
    st.subheader("My Health Journal")
    current_user = st.session_state.get("user")
    if not current_user:
        st.error("Please log in first")
        return

    username = get_user_identifier(current_user)
    journal_data = load_journal(username)

    tab1, tab2 = st.tabs(["Add Entry", "View Entries"])

    with tab1:
        entry_date = st.date_input("Select a date", key="journal_date")
        date_str = entry_date.strftime("%Y-%m-%d")

        feelings = st.selectbox(
            "How are you feeling today?",
            ["Happy 😊", "Sad 😢", "Calm 😌", "Anxious 😰", "Energetic ⚡", "Tired 😴", "Frustrated 😤"],
            key="journal_feeling"
        )
        notes = st.text_area(
            "Write your health notes and feelings:",
            placeholder="Describe how you're feeling, any symptoms, activities, or anything noteworthy...",
            height=150,
            key="journal_notes"
        )
        breathing = st.slider(
            "How is your breathing today? (1 = difficult, 10 = easy)",
            1, 10, 10,
            key="journal_breathing"
        )

        if st.button("Save Entry", key="save_journal_entry"):
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            time_only = now.strftime("%H:%M:%S")
            entry_key = f"{date_str} {timestamp}"
            journal_data[entry_key] = {
                "date": date_str,
                "time": time_only,
                "feeling": feelings,
                "notes": notes,
                "breathing": breathing
            }
            save_journal(username, journal_data)
            st.success(f"Entry saved for {date_str} at {timestamp}")
            st.experimental_rerun()
            return

    with tab2:
        if not journal_data:
            st.info("No journal entries yet. Start by adding one!")
        else:
            for entry_key in sorted(journal_data.keys(), reverse=True):
                entry = journal_data[entry_key]
                label = f"{entry.get('date')} {entry.get('time', '')} — {entry.get('feeling')}"
                with st.expander(f"📅 {label}"):
                    st.write(f"**Breathing:** {entry.get('breathing')}")
                    st.write(f"**Notes:** {entry.get('notes')}")


def main():
    st.sidebar.title("Menu")
    if st.session_state.get("logged_in", False):
        if st.sidebar.button("Logout"):
            logout()
    else:
        st.sidebar.warning("Not logged in")

    if st.session_state.get("logged_in", False):
        options = ["Dashboard", "Journal"]
        if st.session_state.get("role") == "Parent":
            options.append("Manage Children")
    else:
        options = ["Login"]

    default_choice = st.session_state.get("page", "Login").replace("_", " ").title()
    if default_choice not in options:
        default_choice = options[0]

    choice = st.sidebar.selectbox("Select an option", options, index=options.index(default_choice) if default_choice in options else 0)

    if choice == "Login":
        st.session_state["page"] = "login"
        login()
    elif choice == "Dashboard":
        st.session_state["page"] = "dashboard"
        if not st.session_state.get("logged_in", False):
            st.error("Please log in to access the dashboard")
            login()
        else:
            dashboard()
    elif choice == "Journal":
        st.session_state["page"] = "journal"
        if not st.session_state.get("logged_in", False):
            st.error("Please log in to access the journal")
            login()
        else:
            journal()
    elif choice == "Manage Children":
        st.session_state["page"] = "manage_children"
        if not st.session_state.get("logged_in", False):
            st.error("Please log in to manage children")
            login()
        else:
            manage_children()
    if st.session_state.get("page") == "child_info":
        child_info()


if __name__ == "__main__":
    main()



