import streamlit as st
import sqlite3
import uuid
import pandas as pd
import json
from datetime import datetime

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

st.set_page_config(page_title="Office Helpdesk Bot",page_icon="🛠️")

st.title("🛠️ Office Helpdesk NLP Helpdesk")

# ---------------- NLP DATA ----------------

texts=[
"cannot login",
"password not working",
"account locked",
"vpn not connecting",
"vpn disconnected",
"internet slow",
"wifi not working",
"printer not printing",
"printer offline",
"suspicious email",
"phishing mail",
"cannot install software",
"software problem"
]

labels=[
"Access",
"Access",
"Access",
"VPN",
"VPN",
"WiFi",
"WiFi",
"Printer",
"Printer",
"Phishing",
"Phishing",
"Software",
"Software"
]

vectorizer=CountVectorizer()

X=vectorizer.fit_transform(texts)

model=MultinomialNB()

model.fit(X,labels)

def predict_issue(text):

    vec=vectorizer.transform([text])

    return model.predict(vec)[0]

# ---------------- TROUBLESHOOTING ----------------

solutions={
"VPN":"🔹 Restart VPN\n🔹 Check internet\n🔹 Try hotspot",
"WiFi":"🔹 Restart router\n🔹 Reconnect WiFi",
"Access":"🔹 Reset password\n🔹 Check caps lock",
"Printer":"🔹 Restart printer\n🔹 Clear print queue",
"Phishing":"🔹 Do not click links\n🔹 Report to IT",
"Software":"🔹 Contact IT for install access"
}

# ---------------- DATABASE ----------------

conn=sqlite3.connect("helpdesk.db",check_same_thread=False)
cursor=conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets(
ticket_id TEXT,
time TEXT,
category TEXT,
issue TEXT,
status TEXT
)
""")

conn.commit()

# ---------------- FUNCTIONS ----------------

def create_ticket(issue,category):

    ticket_id="HD-"+uuid.uuid4().hex[:6].upper()

    time=datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute(
    "INSERT INTO tickets VALUES (?,?,?,?,?)",
    (ticket_id,time,category,issue,"Open")
    )

    conn.commit()

    return ticket_id


def load_tickets():

    cursor.execute("SELECT * FROM tickets")

    return cursor.fetchall()


def update_status(ticket_id,status):

    cursor.execute(
    "UPDATE tickets SET status=? WHERE ticket_id=?",
    (status,ticket_id)
    )

    conn.commit()

# ---------------- CHAT STATE ----------------

if "issue" not in st.session_state:
    st.session_state.issue=None

# ---------------- CHATBOT ----------------

st.subheader("💬 Helpdesk Chatbot")

user_input=st.text_input("Describe your issue")

if user_input:

    category=predict_issue(user_input)

    st.session_state.issue=user_input

    st.session_state.category=category

    st.success(f"🔍 Detected Issue: {category}")

    st.info(solutions.get(category,"Provide more details"))

# ---------------- CREATE TICKET ----------------

if st.button("🎫 Create Ticket"):

    if st.session_state.issue:

        ticket=create_ticket(
        st.session_state.issue,
        st.session_state.category
        )

        st.success(f"Ticket Created: {ticket}")

        st.session_state.issue=None

    else:

        st.warning("Please describe issue first")

# ---------------- TICKETS DASHBOARD ----------------

st.divider()

st.subheader("📋 Tickets Dashboard")

tickets=load_tickets()

df=pd.DataFrame(
tickets,
columns=["Ticket ID","Time","Category","Issue","Status"]
)

# ---- STATS ----

col1,col2,col3=st.columns(3)

col1.metric("🟡 Open",len(df[df["Status"]=="Open"]))
col2.metric("🔵 In Progress",len(df[df["Status"]=="In Progress"]))
col3.metric("🟢 Resolved",len(df[df["Status"]=="Resolved"]))

# ---- FILTER ----

status_filter=st.selectbox(
"Filter Tickets",
["All","Open","In Progress","Resolved"]
)

if status_filter!="All":
    df=df[df["Status"]==status_filter]

st.dataframe(df)

# ---------------- UPDATE STATUS ----------------

st.subheader("🔧 Update Ticket Status")

ticket_ids=df["Ticket ID"].tolist()

if ticket_ids:

    selected_ticket=st.selectbox("Ticket ID",ticket_ids)

    new_status=st.selectbox(
    "New Status",
    ["Open","In Progress","Resolved"]
    )

    if st.button("Update Status"):

        update_status(selected_ticket,new_status)

        st.success("Status updated")

        st.experimental_rerun()

# ---------------- DOWNLOAD ----------------

st.subheader("⬇ Download Tickets")

csv=df.to_csv(index=False)

st.download_button(
"📥 Download CSV (Excel)",
csv,
"tickets.csv",
"text/csv"
)

json_data=df.to_json(orient="records")

st.download_button(
"📥 Download JSON",
json_data,
"tickets.json",
"application/json"
)