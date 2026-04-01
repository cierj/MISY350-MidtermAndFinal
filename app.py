import streamlit as st
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



# Make dashboard

# Dashboard should include: daily check in, wind power test with peak flow meter,
# and an character of our choice which shows their percentage of healthiness for the day (based on peak flow meter and daily check in)


#We want a home page, journal, awards, and a help section (maybe could implement the chatbot here)

#Journal should include a calendar where the user can write notes on their breathing throughout the day

