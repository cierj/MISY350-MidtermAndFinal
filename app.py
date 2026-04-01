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


#st.set_page_config(page_title="Smart Coffee Kiosk Application")
st.title("Health Tracker for ashma *Working Title*")


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
    options = ["Login", "Record breath", "Ask a Question", "Coming Soon"]

    choice = st.sidebar.selectbox("Select an option", options)
    
    if choice == "Login":
        login()
    elif choice == "Record breath":
        record_breath()
    elif choice == "Ask a Question":
        ask_question()
    elif choice == "Coming Soon":
        coming_soon()
if __name__ == "__main__":
    main()