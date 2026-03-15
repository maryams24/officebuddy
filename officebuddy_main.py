import streamlit as st
import sqlite3
import uuid
from datetime import datetime

# NLP libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="NLP Helpdesk Chatbot", page_icon="🛠️")

# -------------------------------
# TRAIN SIMPLE NLP MODEL
# -------------------------------

texts = [
"cannot login to my account",
"password not working",
"account locked",
"vpn not connecting",
"vpn error 809",
"cannot connect to vpn",
"wifi not working",
"internet disconnected",
"wifi slow",
"printer not printing",
"printer offline",
"cannot print document",
"suspicious email received",
"phishing email",
"spam email received",
"cannot install software",
"need admin rights",
"software installation problem"
]

labels = [
"Access",
"Access",
"Access",
"VPN",
"VPN",
"VPN",
"WiFi",
"WiFi",
"WiFi",
"Printer",
"Printer",
"Printer",
"Phishing",
"Phishing",
"Phishing",
"Software",
"Software",
"Software"
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)


def predict_category(text):
    vec = vectorizer.transform([text])
    return model.predict(vec)[0]

# -------------------------------
# DATABASE
# -------------------------------

conn = sqlite3.connect("tickets.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tickets(
ticket_id TEXT,
created_at TEXT,
category TEXT,
summary TEXT,
status TEXT
)
""")

conn.commit()


def create_ticket(summary):

    category = predict_category(summary)

    ticket_id = "HD-" + uuid.uuid4().hex[:6].upper()

    time = datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute(
    "INSERT INTO tickets VALUES (?,?,?,?,?)",
    (ticket_id, time, category, summary, "Open")
    )

    conn.commit()

    return ticket_id, category


def load_tickets():

    cur.execute("SELECT * FROM tickets ORDER BY created_at DESC")

    return cur.fetchall()

# -------------------------------
# QUICK TROUBLESHOOTING
# -------------------------------

def quick_steps(cat):

    if cat == "VPN":
        return "Try restarting VPN, check internet, or connect using hotspot."

    if cat == "WiFi":
        return "Restart WiFi, reconnect network, or restart laptop."

    if cat == "Access":
        return "Check caps lock or try resetting password."

    if cat == "Printer":
        return "Restart printer and clear print queue."

    if cat == "Software":
        return "Check company software portal or request admin access."

    if cat == "Phishing":
        return "Do not click links and report email to IT."

    return "Please provide more details."

# -------------------------------
# SESSION STATE
# -------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = [
    {"role":"assistant","content":"Hi 👋 I am your NLP Helpdesk Bot.\nDescribe your issue or type **create ticket**."}
    ]

if "last_issue" not in st.session_state:
    st.session_state.last_issue = ""

# -------------------------------
# TABS
# -------------------------------

chat_tab, ticket_tab = st.tabs(["💬 Chat","🎫 Tickets"])

# -------------------------------
# CHAT TAB
# -------------------------------

with chat_tab:

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Describe your issue")

    if user_input:

        st.session_state.messages.append({"role":"user","content":user_input})

        if user_input.lower() == "create ticket":

            if st.session_state.last_issue == "":
                response = "Please describe your issue first."

            else:

                ticket_id, cat = create_ticket(st.session_state.last_issue)

                response = f"""
Ticket Created 🎫

ID: **{ticket_id}**  
Category: **{cat}**  
Status: **Open**
"""

        else:

            category = predict_category(user_input)

            steps = quick_steps(category)

            st.session_state.last_issue = user_input

            response = f"""
Detected Category: **{category}**

Suggested Fix:
{steps}

If problem continues type **create ticket**
"""

        st.session_state.messages.append({"role":"assistant","content":response})

        st.rerun()

# -------------------------------
# TICKETS TAB
# -------------------------------

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