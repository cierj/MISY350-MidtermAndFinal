import streamlit as st
import json
from pathlib import Path

json_file = Path("inventory.json")
orders_file = Path("orders.json")

# load inventory
if json_file.exists():
    with open(json_file, "r") as f:
        inventory = json.load(f)
else:
    # Default data if file doesn't exist
    inventory = []

# load orders
if orders_file.exists():
    with open(orders_file, "r") as f:
        orders = json.load(f)
else:
    orders = []



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