import streamlit as st
import sqlite3
import uuid
from datetime import datetime

st.set_page_config(page_title="Office Helpdesk NLP Bot", page_icon="🛠️")

# ----------------------------
# SIMPLE NLP TRAINING DATA
# ----------------------------

dataset = {
"Access":[
"cannot login",
"password not working",
"account locked",
"login failed",
"reset password"
],

"VPN":[
"vpn not connecting",
"vpn error",
"cannot connect vpn",
"vpn disconnecting"
],

"WiFi":[
"wifi not working",
"internet disconnected",
"wifi slow",
"network problem"
],

"Printer":[
"printer not printing",
"printer offline",
"cannot print document"
],

"Phishing":[
"suspicious email",
"phishing email",
"spam email"
],

"Software":[
"cannot install software",
"software installation issue",
"need admin access"
]
}


# ----------------------------
# SIMPLE NLP PREDICTION
# ----------------------------

def predict_category(text):

    text = text.lower()

    best_match = "General"
    best_score = 0

    for category, examples in dataset.items():

        score = 0

        for sentence in examples:

            for word in sentence.split():

                if word in text:
                    score += 1

        if score > best_score:
            best_score = score
            best_match = category

    return best_match


# ----------------------------
# TROUBLESHOOT STEPS
# ----------------------------

def quick_steps(cat):

    if cat == "VPN":
        return "Restart VPN, check internet, try hotspot."

    if cat == "WiFi":
        return "Reconnect WiFi or restart laptop."

    if cat == "Access":
        return "Check caps lock or reset password."

    if cat == "Printer":
        return "Restart printer and clear print queue."

    if cat == "Software":
        return "Check company software portal or request admin access."

    if cat == "Phishing":
        return "Do not click links and report email to IT."

    return "Please provide more details."


# ----------------------------
# DATABASE
# ----------------------------

conn = sqlite3.connect("helpdesk.db",check_same_thread=False)
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

    created = datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute(
    "INSERT INTO tickets VALUES (?,?,?,?,?)",
    (ticket_id,created,category,summary,"Open")
    )

    conn.commit()

    return ticket_id,category


def load_tickets():

    cur.execute("SELECT * FROM tickets ORDER BY created_at DESC")

    return cur.fetchall()


# ----------------------------
# SESSION STATE
# ----------------------------

if "messages" not in st.session_state:

    st.session_state.messages = [
    {"role":"assistant","content":"Hi 👋 I am your Helpdesk Bot. Describe your issue or type **create ticket**."}
    ]

if "last_issue" not in st.session_state:
    st.session_state.last_issue = ""


# ----------------------------
# TABS
# ----------------------------

chat_tab, ticket_tab = st.tabs(["💬 Chat","🎫 Tickets"])


# ----------------------------
# CHAT
# ----------------------------

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

                ticket_id,cat = create_ticket(st.session_state.last_issue)

                response=f"""
Ticket Created 🎫

ID: **{ticket_id}**  
Category: **{cat}**  
Status: **Open**
"""

        else:

            category=predict_category(user_input)

            steps=quick_steps(category)

            st.session_state.last_issue=user_input

            response=f"""
Detected Issue: **{category}**

Suggested Fix:
{steps}

If problem continues type **create ticket**
"""

        st.session_state.messages.append({"role":"assistant","content":response})

        st.rerun()


# ----------------------------
# TICKETS PAGE
# ----------------------------

with ticket_tab:

    st.title("Helpdesk Tickets")

    tickets=load_tickets()

    if len(tickets)==0:

        st.info("No tickets yet")

    else:

        for t in tickets:

            st.write("Ticket ID:",t[0])
            st.write("Created:",t[1])
            st.write("Category:",t[2])
            st.write("Issue:",t[3])
            st.write("Status:",t[4])
            st.divider()