import streamlit as st
import json
from pathlib import Path

json_file = Path("login.json")
breath_file = Path("breath_info.json")

# load inventory
if json_file.exists():
    with open(json_file, "r") as f:
        login = json.load(f)
else:
    # Default data if file doesn't exist
    login = []

# load breath info
if breath_file.exists():
    with open(breath_file, "r") as f:
        breath_info = json.load(f)
else:
    breath_info = []



#st.set_page_config(page_title="Smart Coffee Kiosk Application")
st.title("Health Tracker for ashma *Working Title*")



# Make dashboard

# Dashboard should include: daily check in, wind power test with peak flow meter,
# and an character of our choice which shows their percentage of healthiness for the day (based on peak flow meter and daily check in)


#We want a home page, journal, awards, and a help section (maybe could implement the chatbot here)

#Journal should include a calendar where the user can write notes on their breathing throughout the day


#awards section should include awards for a streak when recording their medicines (7 day, 30 day, 3 months, 6 months, 1 year, 2 years, 5 years)
#and awards for a streak when recording their peak flow meter (7 day, 30 day, 3 months, 6 months, 1 year, 2 years, 5 years)
#loading bar for next award and a section to view all awards received


#help section should include a chatbot that can answer questions about asthma and how to use the app, and also a section to contact support if they have any issues with the app



#st.set_page_config(page_title="Smart Coffee Kiosk Application")
st.title("Health Tracker for ashma *Working Title*")

def home():
    st.subheader("Home")

def login():
    st.subheader("Login")

def record_breath():
    st.subheader("Record Breath")

def ask_question():
    st.subheader("Ask a Question")

def coming_soon():
    st.subheader("Coming Soon")







def main():
    st.sidebar.title("Menu")
    options = ["Home","Login", "Record breath", "Ask a Question", "Coming Soon"]

    choice = st.sidebar.selectbox("Select an option", options)
    
    if choice == "Login":
        login()
    elif choice == "Record breath":
        record_breath()
    elif choice == "Ask a Question":
        ask_question()
    elif choice == "Coming Soon":
        coming_soon()
    elif choice == "home":
        home()
if __name__ == "__main__":
    main()





















































#journal


# ============================================
# JOURNAL SECTION (Added by group member)
# ============================================

def journal():
    st.subheader("My Health Journal")
    st.write("Track your feelings and health notes throughout the year.")
    
    # Initialize journal data file
    journal_file = Path("journal.json")
    if journal_file.exists():
        with open(journal_file, "r") as f:
            journal_data = json.load(f)
    else:
        journal_data = {}
    
    # Create tabs for viewing and adding entries
    tab1, tab2 = st.tabs(["Add Entry", "View Entries"])
    
    with tab1:
        st.write("### Add a Journal Entry")
        # Calendar date picker
        selected_date = st.date_input(
            "Select a date",
            value=None,
            key="journal_date"
        )
        
        if selected_date:
            date_str = selected_date.strftime("%Y-%m-%d")
            
            # Text area for feelings and notes
            feelings = st.selectbox(
                "How are you feeling today?",
                ["Happy 😊", "Sad 😢", "Calm 😌", "Anxious 😰", "Energetic ⚡", "Tired 😴", "Frustrated 😤"]
            )
            
            notes = st.text_area(
                "Write your health notes and feelings:",
                placeholder="Describe how you're feeling, any symptoms, activities, or anything noteworthy...",
                height=150,
                key=f"notes_{date_str}"
            )
            
            # Breathing difficulty scale
            breathing = st.slider(
                "How is your breathing today? (1=Difficult, 10=Easy)",
                1, 10, 10,
                key=f"breathing_{date_str}"
            )
            
            # Save entry button
            if st.button("Save Entry", key=f"save_{date_str}"):
                journal_data[date_str] = {
                    "feeling": feelings,
                    "notes": notes,
                    "breathing": breathing
                }
                with open(journal_file, "w") as f:
                    json.dump(journal_data, f, indent=4)
                st.success(f"✅ Entry saved for {date_str}!")
    
    with tab2:
        st.write("### View Past Entries")
        if journal_data:
            # Sort dates in reverse order (newest first)
            sorted_dates = sorted(journal_data.keys(), reverse=True)
            
            for date in sorted_dates:
                entry = journal_data[date]
                with st.expander(f"📅 {date} - {entry['feeling']}"):
                    st.write(f"**Feeling:** {entry['feeling']}")
                    st.write(f"**Breathing Quality:** {entry['breathing']}/10")
                    st.write(f"**Notes:**\n{entry['notes']}")
                    
                    # Delete entry button
                    if st.button("Delete Entry", key=f"delete_{date}"):
                        del journal_data[date]
                        with open(journal_file, "w") as f:
                            json.dump(journal_data, f, indent=4)
                        st.success(f"Entry for {date} deleted.")
                        st.rerun()
        else:
            st.info("No journal entries yet. Start by adding one!")


