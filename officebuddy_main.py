import streamlit as st
import sqlite3
import uuid
from datetime import datetime

st.set_page_config(page_title="Office Helpdesk Bot", page_icon="🛠️")

# -------------------------
# SIMPLE NLP DATASET
# -------------------------

training_data = {
    "Access": [
        "cannot login",
        "password not working",
        "account locked",
        "login problem"
    ],
    "VPN": [
        "vpn not connecting",
        "vpn error",
        "vpn disconnected"
    ],
    "WiFi": [
        "wifi not working",
        "internet slow",
        "network disconnected"
    ],
    "Printer": [
        "printer not printing",
        "printer offline"
    ],
    "Software": [
        "cannot install software",
        "software issue"
    ],
    "Phishing": [
        "suspicious email",
        "phishing email"
    ]
}

# -------------------------
# NLP CLASSIFIER
# -------------------------

def predict_category(text):

    text = text.lower()

    best_category = "General"
    best_score = 0

    for category, sentences in training_data.items():

        score = 0

        for sentence in sentences:

            for word in sentence.split():

                if word in text:
                    score += 1

        if score > best_score:
            best_score = score
            best_category = category

    return best_category


# -------------------------
# TROUBLESHOOT STEPS
# -------------------------

def quick_steps(cat):

    if cat == "VPN":
        return "Restart VPN app, check internet connection, or try hotspot."

    if cat == "WiFi":
        return "Reconnect WiFi or restart laptop."

    if cat == "Access":
        return "Check caps lock or reset password."

    if cat == "Printer":
        return "Restart printer and clear print queue."

    if cat == "Software":
        return "Request installation access from IT."

    if cat == "Phishing":
        return "Do not click links and report email to IT."

    return "Please provide more details."


# -------------------------
# DATABASE
# -------------------------

conn = sqlite3.connect("helpdesk.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tickets(
ticket_id TEXT,
created_at TEXT,
category TEXT,
issue TEXT,
status TEXT
)
""")

conn.commit()


def create_ticket(issue):

    category = predict_category(issue)

    ticket_id = "HD-" + uuid.uuid4().hex[:6].upper()

    time = datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute(
        "INSERT INTO tickets VALUES (?,?,?,?,?)",
        (ticket_id, time, category, issue, "Open")
    )

    conn.commit()

    return ticket_id, category


def load_tickets():

    cur.execute("SELECT * FROM tickets ORDER BY created_at DESC")

    return cur.fetchall()


# -------------------------
# SESSION STATE
# -------------------------

if "messages" not in st.session_state:

    st.session_state.messages = [
        {"role": "assistant", "content": "Hi 👋 I am your Office Helpdesk Bot.\nDescribe your issue. When ready type **create ticket**."}
    ]

if "last_issue" not in st.session_state:
    st.session_state.last_issue = None


# -------------------------
# TABS
# -------------------------

chat_tab, ticket_tab = st.tabs(["💬 Chat", "🎫 Tickets"])


# -------------------------
# CHAT
# -------------------------

with chat_tab:

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Describe your issue")

    if user_input:

        st.session_state.messages.append({"role": "user", "content": user_input})

        text = user_input.lower().strip()

        # CREATE TICKET COMMAND
        if text == "create ticket":

            if st.session_state.last_issue:

                ticket_id, category = create_ticket(st.session_state.last_issue)

                response = f"""
Ticket Created 🎫

Ticket ID: **{ticket_id}**  
Category: **{category}**  
Status: **Open**

Check the **Tickets tab** to view it.
"""

            else:

                response = "Please describe your issue first."

        # NORMAL ISSUE MESSAGE
        else:

            category = predict_category(user_input)

            steps = quick_steps(category)

            st.session_state.last_issue = user_input

            response = f"""
Detected Issue: **{category}**

Suggested Fix:
{steps}

If problem continues type **create ticket**
"""

        st.session_state.messages.append({"role": "assistant", "content": response})

        st.rerun()


# -------------------------
# TICKETS PAGE
# -------------------------

with ticket_tab:

    st.title("Helpdesk Tickets")

    tickets = load_tickets()

    if len(tickets) == 0:

        st.info("No tickets created yet")

    else:

        for t in tickets:

            st.write("Ticket ID:", t[0])
            st.write("Created:", t[1])
            st.write("Category:", t[2])
            st.write("Issue:", t[3])
            st.write("Status:", t[4])
            st.divider()