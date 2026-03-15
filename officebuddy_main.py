import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

st.set_page_config(page_title="Office Helpdesk Assistant", page_icon="🛠️")

st.title("🛠️ Office Helpdesk Assistant")

# ---------------- NLP KEYWORDS ----------------

nlp_data = {
    "Access": ["login","password","account","locked"],
    "VPN": ["vpn"],
    "WiFi": ["wifi","internet","network","slow"],
    "Printer": ["printer","printing"],
    "Phishing": ["phishing","spam","suspicious"],
    "Software": ["install","software","application"]
}

solutions = {
"VPN":"Restart VPN and check internet",
"WiFi":"Restart router or reconnect WiFi",
"Access":"Reset password or check caps lock",
"Printer":"Restart printer and clear queue",
"Phishing":"Do not click links, report to IT",
"Software":"Contact IT for installation access",
"General":"Please provide more details"
}

def detect_issue(text):
    text=text.lower()
    for cat,words in nlp_data.items():
        for w in words:
            if w in text:
                return cat
    return "General"

# ---------------- SESSION STORAGE ----------------

if "tickets" not in st.session_state:
    st.session_state.tickets=[]

if "current_issue" not in st.session_state:
    st.session_state.current_issue=None

if "current_category" not in st.session_state:
    st.session_state.current_category=None

# ---------------- CHATBOT ----------------

st.subheader("💬 Helpdesk Chatbot")

issue_text = st.text_input("Describe your issue")

if issue_text:

    category = detect_issue(issue_text)

    st.session_state.current_issue = issue_text
    st.session_state.current_category = category

    st.success(f"Detected Issue: {category}")
    st.info(solutions.get(category))

# ---------------- CREATE TICKET ----------------

if st.button("🎫 Create Ticket"):

    if st.session_state.current_issue:

        ticket_id = "HD-"+uuid.uuid4().hex[:6].upper()

        ticket = {
            "Ticket ID":ticket_id,
            "Time":datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Category":st.session_state.current_category,
            "Issue":st.session_state.current_issue,
            "Status":"Open"
        }

        st.session_state.tickets.append(ticket)

        st.success(f"Ticket Created: {ticket_id}")

        st.session_state.current_issue=None

    else:
        st.warning("Please describe the issue first")

# ---------------- DASHBOARD ----------------

st.divider()

st.subheader("📊 Ticket Dashboard")

df = pd.DataFrame(st.session_state.tickets)

if not df.empty:

    col1,col2,col3 = st.columns(3)

    col1.metric("Open", len(df[df["Status"]=="Open"]))
    col2.metric("In Progress", len(df[df["Status"]=="In Progress"]))
    col3.metric("Resolved", len(df[df["Status"]=="Resolved"]))

status_filter = st.selectbox(
"Filter Tickets",
["All","Open","In Progress","Resolved"]
)

if not df.empty and status_filter!="All":
    df = df[df["Status"]==status_filter]

st.dataframe(df)

# ---------------- UPDATE STATUS ----------------

st.subheader("Update Ticket Status")

if not df.empty:

    ticket_ids = df["Ticket ID"].tolist()

    selected_ticket = st.selectbox("Ticket ID", ticket_ids)

    new_status = st.selectbox(
        "New Status",
        ["Open","In Progress","Resolved"]
    )

    if st.button("Update Status"):

        for t in st.session_state.tickets:
            if t["Ticket ID"]==selected_ticket:
                t["Status"]=new_status

        st.success("Status Updated")

# ---------------- DOWNLOAD ----------------

st.subheader("Download Tickets")

if not df.empty:

    csv = df.to_csv(index=False)

    st.download_button(
        "Download CSV",
        csv,
        "tickets.csv",
        "text/csv"
    )

    json_data = df.to_json(orient="records")

    st.download_button(
        "Download JSON",
        json_data,
        "tickets.json",
        "application/json"
    )