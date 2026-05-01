from app import main


if __name__ == "__main__":
    main()

        st.rerun()
        return

    st.write("---")
    st.write("### Linked Children")
    children = current_user.get("children", [])
    if not children:
        st.info("No children linked yet")
        return

    for child_id in children:
        child_user = get_child_user(child_id)
        display_name = child_user.get("username") if child_user else child_id
        with st.expander(f"👶 {display_name}"):
            if child_user:
                st.write(f"Email: {child_user.get('email')}")
                st.write(f"Role: {child_user.get('role')}")
            if st.button(f"View {display_name}'s Info", key=f"view_{child_id}"):
                st.session_state["viewing_child"] = child_id
                st.session_state["page"] = "child_info"
                st.rerun()
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
                st.rerun()
                return


def child_info():
    child_id = st.session_state.get("viewing_child")
    if not child_id:
        st.error("No child selected")
        return

    current_user = require_login()
    if not current_user:
        return

    child_user = get_child_user(child_id)
    if not child_user:
        st.error("Child account not found")
        return

    st.subheader(f"{child_user.get('username')}\'s Info")
    st.write(f"Email: {child_user.get('email')}")
    st.write("### Journal Entries")

    journal_data = load_journal(get_user_identifier(child_user))
    display_journal_entries(journal_data, full_display=True)

    if st.button("Back to Manage Children", key="back_to_manage"):
        st.session_state["page"] = "manage_children"
        st.session_state["viewing_child"] = None
        st.rerun()
        return


def journal():
    st.subheader("My Health Journal")
    current_user = require_login()
    if not current_user:
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
            st.rerun()
            return

    with tab2:
        display_journal_entries(journal_data, full_display=False, prefix="📅 ")


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



